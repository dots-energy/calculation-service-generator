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


import traceback
import threading
from paho.mqtt.client import Client

from model.io.log import SIM_LOGGER, LOCAL_LOGGER
from model.types import EsdlId
from model.calculation.service_calc import ServiceCalc
from model.io.io_data import IODataInterface, ModelParameters
from model.io.input_data_inventory import InputDataInventory
import model.io.messages as messages

MODEL_PARAMETERS = "model_parameters"
NEW_STEP = "new_step"
SIMULATION_DONE = "simulations_done"


class MqttClient:
    def __init__(
        self,
        host: str,
        port: int,
        qos: int,
        username: str,
        password: str,
        input_data_inventory: InputDataInventory,
        service_calc: ServiceCalc,
    ):
        self.host = host
        self.port = port
        self.qos = qos
        self.username = username
        self.password = password

        self.mqtt_client = None
        self.subscribed_topics = []

        self.input_data_inventory = input_data_inventory
        self.service_calc = service_calc

    def wait_for_data(self):
        # initialize mqtt connection
        self.mqtt_client = Client(clean_session=True)

        # The callback for when the client receives a CONNACK response from the server.
        def on_connect(client, userdata, flags, rc):
            # print("Connected with result code " + str(rc))
            # Subscribing in on_connect() means that if we lose the connection and
            # reconnect then subscriptions will be renewed.
            for topic in self.subscribed_topics:
                client.subscribe(topic, self.qos)

        # The callback for when a PUBLISH message is received from the server.
        def on_message(client, userdata, msg):
            t = threading.Thread(target=self._process_message, args=[client, msg])
            t.setDaemon(True)  # kill thread when main thread stops
            t.start()

        self.mqtt_client.on_connect = on_connect
        self.mqtt_client.on_message = on_message

        self.mqtt_client.username_pw_set(self.username, self.password)
        self.mqtt_client.connect(self.host, port=self.port)

        self._subscribe_lifecycle_topics()

        self._send_ready_for_processing()
        LOCAL_LOGGER.debug("Service started, waiting for model parameters...")
        self.mqtt_client.loop_forever()

    def _process_message(self, client: Client, msg):
        try:
            topic = msg.topic
            LOCAL_LOGGER.debug(f" [received] {topic}: {msg.payload}")

            data_name: str = self._get_data_name(topic)

            if data_name == SIMULATION_DONE:
                LOCAL_LOGGER.debug("Received simulation done message")
                self.service_calc.write_to_influxdb()
                SIM_LOGGER.info(
                    f"Simulation Orchestrator terminated service: '{{ cookiecutter.service_name }}: "
                    f"{self.service_calc.model_id}' - '{self.service_calc.simulation_id}'"
                )
                client.disconnect()
            else:
                if data_name == MODEL_PARAMETERS or data_name == NEW_STEP:  # set lifecycle main topic
                    main_topic = "/lifecycle/dots-so/model"
                else:  # get data main topic from message topic
                    main_topic = (
                        "/".join(topic.split("/")[0:4])
                    )  # first three items separated by '/'

                if data_name == MODEL_PARAMETERS:
                    model_parameter_data = self.input_data_inventory.create_new_class(
                        ModelParameters, msg.payload
                    )
                    self.service_calc.setup(model_parameter_data.parameters_dict)
                    self.input_data_inventory.set_expected_esdl_ids_for_input_data(
                        self.service_calc.connected_input_esdl_objects_dict
                    )
                    self._subscribe_data_topics(client, self.service_calc.connected_input_esdl_objects_dict)
                    self._send_parameterized()
                    non_executed_calc_names_input_received = []
                else:
                    # add input data and receive a list of calculations that have all required input available
                    non_executed_calc_names_input_received = self.input_data_inventory.add_input(
                        main_topic, data_name, msg.payload
                    )

                # do step for calculations that have received all required input
                if self.input_data_inventory.is_step_active():
                    for calc_name in non_executed_calc_names_input_received:
                        self._do_step(calc_name)

                        if self.input_data_inventory.all_calcs_done():
                            self._send_calculations_done()
                            self.input_data_inventory.delete_all_received_input_data()

        except Exception as ex:
            error_message = str(ex) + traceback.format_exc()

            LOCAL_LOGGER.error(error_message)
            self._send_error_occurred(error_message)
            client.disconnect()

    @staticmethod
    def _get_data_name(topic):
        message = topic.split("/")[6]
        if topic.startswith("/lifecycle/dots-so/model/"):
            if message == "ModelParameters":
                message = MODEL_PARAMETERS
            elif message == "NewStep":
                message = NEW_STEP
            elif message == "SimulationDone":
                message = SIMULATION_DONE
            else:
                raise Exception(f"Received unknown lifecycle message: '{message}'")
        return message

    def _subscribe_lifecycle_topics(self):
        topic = f"/lifecycle/dots-so/model/{self.service_calc.simulation_id}/{self.service_calc.model_id}/+"
        self.mqtt_client.subscribe(topic, self.qos)
        self.subscribed_topics.append(topic)

    def _subscribe_data_topics(self, client: Client, connected_input_esdl_objects_dict: dict):
        topics = []
        for main_topic, esdl_ids in self.input_data_inventory.expected_esdl_ids_dict.items():
            for esdl_id in esdl_ids:
                topics.append(f"{main_topic}/{self.service_calc.simulation_id}/{esdl_id}/#")
        for topic in set(topics):
            client.subscribe(topic, qos=self.qos)
            self.subscribed_topics.append(topic)

    def _send_ready_for_processing(self):
        topic = f"/lifecycle/model/mso/{self.service_calc.simulation_id}/{self.service_calc.model_id}/ReadyForProcessing"
        self.mqtt_client.publish(
            topic, payload=messages.ReadyForProcessing().SerializeToString()
        )
        LOCAL_LOGGER.debug(f" [sent] {topic}")

    def _send_parameterized(self):
        topic = f"/lifecycle/model/dots-so/{self.service_calc.simulation_id}/{self.service_calc.model_id}/Parameterized"
        self.mqtt_client.publish(
            topic, payload=messages.Parameterized().SerializeToString()
        )
        LOCAL_LOGGER.debug(f" [sent] {topic}")

    def _send_io_data(self, esdl_id: EsdlId, io_data: IODataInterface):
        topic = f"{io_data.get_main_topic()}/{self.service_calc.simulation_id}/{esdl_id}/{io_data.get_name()}"
        self.mqtt_client.publish(topic, io_data.get_values_as_serialized_protobuf())
        LOCAL_LOGGER.debug(f" [sent] {topic}: {io_data.get_variable_descr()}")

    def _send_calculations_done(self):
        topic = f"/lifecycle/model/dots-so/{self.service_calc.simulation_id}/{self.service_calc.model_id}/CalculationsDone"
        self.mqtt_client.publish(
            topic, payload=messages.CalculationsDone().SerializeToString()
        )
        LOCAL_LOGGER.debug(f" [sent] {topic}")

    def send_log(self, message: str):
        self.mqtt_client.publish(
            f"/log/model/dots-so/{self.service_calc.simulation_id}/{self.service_calc.model_id}",
            message.encode("utf-8"),
        )

    def _send_error_occurred(self, message: str):
        error_occurred_message = messages.ErrorOccurred(error_message=message)
        self.mqtt_client.publish(
            f"/lifecycle/model/dots-so/{self.service_calc.simulation_id}/{self.service_calc.model_id}/ErrorOccurred",
            error_occurred_message.SerializeToString(),
        )

    def _do_step(self, calc_name: str):
        # do step calculation if all data received for 'calc_name'
        SIM_LOGGER.debug(
            f"start '{self.service_calc.service_name} ({self.service_calc.model_id}) - {calc_name}'"
        )
        output_data_tuple = self.service_calc.calc_function(
            calc_name, self.input_data_inventory.get_input_data(calc_name)
        )

        # send results
        if output_data_tuple:
            for output_data_dict in output_data_tuple:
                for esdl_id, output_data in output_data_dict.items():
                    self._send_io_data(esdl_id, output_data)

        self.input_data_inventory.set_calc_done(calc_name)

        SIM_LOGGER.debug(
            f"finished '{self.service_calc.service_name} ({self.service_calc.model_id}) - {calc_name}'"
        )
