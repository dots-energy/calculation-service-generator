#!/usr/bin/env python
import json
import time
import pika
from dotenv import load_dotenv

from service_name.io_data import *

service_name = "service_name"
rabbitmq_host = "localhost"
exchange = "dots"

connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
channel = connection.channel()

channel.exchange_declare(exchange=exchange, exchange_type="topic")
channel.queue_declare("", exclusive=True)


def test_service():
    seconds_between_sends = 2

    # The config_data and receive_services data will be constructed by the
    # Simulation Orchestrator from the ESDL model
    config_dict = ConfigData(2.4, "ok").get_output_dict()
    receive_dict = {
        "origin_service1": {"number_of": "2", "uuids": ["UUID_1", "UUID_2"]},
        "origin_service2": {"number_of": "5", "uuids": []},
    }
    init_dict = {"config_data": config_dict, "receive_services": receive_dict}
    send_output(
        os.getenv("RABBITMQ_LIFECYCLE_TOPIC") + ".init." + os.getenv("SERVICE_UUID"),
        json.dumps(init_dict),
    )
    print("sent lifecycle_init")
    time.sleep(seconds_between_sends)

    # the 'lifecycle.step' will be sent by the Simulation Orchestrator at the start of each time step
    step_dict = NewStepData("ok").get_output_dict()
    send_output(os.getenv("RABBITMQ_LIFECYCLE_TOPIC") + ".step", json.dumps(step_dict))
    print("sent lifecycle_step")
    time.sleep(seconds_between_sends)

    # the data below will originate from other services in the simulation model
    # send all 'origin_service1' data objects, 'number_of' times
    for i in range(int(receive_dict["origin_service1"]["number_of"])):
        if len(receive_dict["origin_service1"]["uuids"]):
            uuid = receive_dict["origin_service1"]["uuids"][i]
        else:
            uuid = "ANY_UUID"
        send_data(InputData1(True, 2.4), uuid)
        print("sent InputData1")
        time.sleep(seconds_between_sends)
        send_data(InputData2("ok", True, 2.4), uuid)
        print("sent InputData2")
        time.sleep(seconds_between_sends)

    # send all 'origin_service2' data objects, 'number_of' times
    for i in range(int(receive_dict["origin_service2"]["number_of"])):
        if len(receive_dict["origin_service2"]["uuids"]):
            uuid = receive_dict["origin_service2"]["uuids"][i]
        else:
            uuid = "ANY_UUID"
        send_data(InputData3(2.4), uuid)
        print("sent InputData3")
        time.sleep(seconds_between_sends)

    # end with 'lifecyle.stop'
    send_output(os.getenv("RABBITMQ_LIFECYCLE_TOPIC") + ".stop", json.dumps({}))
    print("sent lifecycle_stop")


def send_data(output_data: IODataInterface, service_uuid: str):
    topic = (
        output_data.get_main_topic() + "." + service_uuid + "." + output_data.get_name()
    )
    send_output(topic, json.dumps(output_data.get_output_dict()))


def send_output(topic: str, message: str):
    body: bytes = message.encode("utf-8")
    channel.basic_publish(exchange=exchange, routing_key=topic, body=body)


if __name__ == "__main__":
    load_dotenv()
    test_service()
