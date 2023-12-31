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


import typing

from model.io.log import SIM_LOGGER
from model.io.input_data_inventory import InputDataInventory
from model.calculation.service_calc import ServiceCalc
from model.io.mqtt_client import MqttClient
from model.io.mqtt_log_handler import MqttLogHandler
import model.calculation.esdl_parser as esdl_parser


class Service:
    def __init__(self, config: typing.Dict[str, typing.Any]):
        # initialize input data container and service calc
        input_data_inventory = InputDataInventory()
        service_calc = ServiceCalc(
            simulation_id=config["SIMULATION_ID"],
            model_id=config["MODEL_ID"],
            influxdb_host=config["INFLUXDB_HOST"],
            influxdb_port=config["INFLUXDB_PORT"],
            influxdb_user=config["INFLUXDB_USER"],
            influxdb_password=config["INFLUXDB_PASSWORD"],
            influxdb_name=config["INFLUXDB_NAME"],
        )

        # initialize mqtt client
        self.mqtt_client = MqttClient(
            host=config["MQTT_HOST"],
            port=config["MQTT_PORT"],
            qos=config["MQTT_QOS"],
            username=config["MQTT_USERNAME"],
            password=config["MQTT_PASSWORD"],
            input_data_inventory=input_data_inventory,
            service_calc=service_calc,
        )

        mqtt_handler = MqttLogHandler(self.mqtt_client)
        SIM_LOGGER.addHandler(mqtt_handler)

    def start(self):
        self.mqtt_client.wait_for_data()
