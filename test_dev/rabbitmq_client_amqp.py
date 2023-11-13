#  This work is based on original code developed and copyrighted by TNO 2023.
#  Subsequent contributions are licensed to you by the developers of such code and are
#  made available to the Project under one or several contributor license agreements.
#
#  This work is licensed to you under the Apache License, Version 2.0.
#  You may obtain a copy of the license at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Contributors:
#      TNO         - Initial implementation
#  Manager:
#      TNO


import os
import logging
import pika
import json
import traceback
from json import JSONDecodeError

from service_name.service_calc import ServiceCalc
from service_name.io_data import IODataInterface
from service_name.input_data_container import InputDataContainer


class RabbitmqClient:
    def __init__(self):
        rabbitmq_host = os.getenv("RABBITMQ_HOST")
        self.rabbitmq_exchange = os.getenv("RABBITMQ_EXCHANGE")
        self.rabbitmq_lifecycle_topic = os.getenv("RABBITMQ_LIFECYCLE_TOPIC")
        self.rabbitmq_log_topic = os.getenv("RABBITMQ_LOG_TOPIC")

        # initialize rabbitmq connection
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=rabbitmq_host)
        )
        self.channel = connection.channel()
        self.channel.exchange_declare(
            exchange=self.rabbitmq_exchange, exchange_type="topic"
        )
        self.queue = self.channel.queue_declare("", exclusive=True).method.queue

        self.input_data_container = InputDataContainer()
        self.service_calc = ServiceCalc()

        self.logger = logging.getLogger("rabbitmq-logger")

    def wait_for_data(self):
        self.bind_lifecycle_topics()

        def callback(ch, method, properties, body):
            topic = method.routing_key

            message = body.decode("utf-8")
            self.logger.info(" [received] {}: {}".format(topic, message))

            data_name: str = self.get_data_name(topic)

            if data_name == "stop_simulation":
                self.channel.stop_consuming()
                self.logger.info("Service stopped")
            else:
                try:
                    data_dict: dict = json.loads(body)
                except JSONDecodeError:
                    raise IOError(
                        "Error reading the input from topic '{}'.".format(topic)
                    )
                try:
                    if data_name == "initialize_simulation":
                        number_of_services_dict = {self.rabbitmq_lifecycle_topic: 1}
                        for service_name, service_descr in data_dict[
                            "receive_services"
                        ].items():
                            number_of_services_dict[service_name] = service_descr[
                                "number_of"
                            ]
                        self.input_data_container.add_config(
                            data_dict["config_data"], number_of_services_dict
                        )
                        self.service_calc.initialize(
                            self.input_data_container.model_parameters.get_output_dict()
                        )
                        self.bind_data_topics(data_dict["receive_services"])
                    else:
                        if data_name == "new_step_data":
                            self.input_data_container.delete_all_received_input_data()
                        calc_names_all_input_received = (
                            self.input_data_container.add_input(
                                topic.split(".")[0], data_name, data_dict
                            )
                        )
                        for calc_name in calc_names_all_input_received:
                            # do step if all input received
                            self.do_step(calc_name)
                except Exception as ex:
                    error_message = str(ex) + traceback.format_exc()
                    self.logger.error(error_message)
                    self.logger.info("Waiting for input...")

        self.channel.basic_consume(
            queue=self.queue, on_message_callback=callback, auto_ack=True
        )

        self.logger.info("Waiting for input...")
        self.channel.start_consuming()

    def get_data_name(self, topic):
        main_topic = topic.split(".")[0]
        if main_topic == self.rabbitmq_lifecycle_topic:
            lifecycle_command = topic.split(".")[1]
            if lifecycle_command == "stop":
                data_name = "stop_simulation"
            elif lifecycle_command == "init":
                data_name = "initialize_simulation"
            else:
                data_name = "new_step_data"
        else:
            data_name = topic.split(".")[2]
        return data_name

    def bind_lifecycle_topics(self):
        life_cycle_commands = ["init." + self.service_calc.model_id, "step", "stop"]
        for life_cycle_command in life_cycle_commands:
            self.channel.queue_bind(
                exchange=self.rabbitmq_exchange,
                queue=self.queue,
                routing_key=self.rabbitmq_lifecycle_topic + "." + life_cycle_command,
            )

    def bind_data_topics(self, receive_services: dict):
        topics = []
        for service_name, service_descr in receive_services.items():
            if len(service_descr["uuids"]) == 0:
                topics.append(service_name + ".#")
            else:
                for uuid in service_descr["uuids"]:
                    topics.append(service_name + "." + uuid + ".#")
        for topic in topics:
            self.channel.queue_bind(
                exchange=self.rabbitmq_exchange, queue=self.queue, routing_key=topic
            )

    def send_io_data(self, io_data: IODataInterface):
        topic = (
            io_data.get_main_topic()
            + "."
            + self.service_calc.model_id
            + "."
            + io_data.get_name()
        )
        self.send_output(topic, json.dumps(io_data.get_output_dict()))

    def send_log(self, message: str):
        self.send_output(
            self.rabbitmq_log_topic + "." + self.service_calc.service_name, message
        )

    def send_output(self, topic: str, message: str):
        body: bytes = message.encode("utf-8")
        topic += "." + self.service_calc.model_id
        self.channel.basic_publish(
            exchange=self.rabbitmq_exchange, routing_key=topic, body=body
        )

    def do_step(self, calc_name: str):
        # do step calculation if all data received for 'calc_name'
        self.logger.info(
            "start '{} - {}'".format(self.service_calc.service_name, calc_name)
        )
        output_data_list = self.service_calc.calc_function(
            calc_name, self.input_data_container.get_input_data(calc_name)
        )

        # send results
        for output_data in output_data_list:
            self.send_io_data(output_data)
            self.logger.info(
                " [sent] {}: {}".format(
                    output_data.get_main_topic(), output_data.get_output_dict()
                )
            )

        self.logger.info(
            "finished '{} - {}'".format(self.service_calc.service_name, calc_name)
        )
