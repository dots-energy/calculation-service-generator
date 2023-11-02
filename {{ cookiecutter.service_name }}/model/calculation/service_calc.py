#!/usr/bin/env python
{% import 'jinja2-templates/service_calc.jinja2' as service_calc_j2 %}
from threading import Lock
from typing import Tuple, Optional, List
from datetime import datetime

from model.io.log import LOCAL_LOGGER as LOGGER
from model.types import EsdlId, ServiceName
from esdl import esdl, EnergySystem
import model.calculation.esdl_parser as esdl_parser
from model.calculation.influxdb_connector import InfluxDBConnector

{{service_calc_j2.import_io_classes(cookiecutter)}}


class ServiceCalc:
    # constructor is called when the model service is created
    def __init__(
            self, simulation_id: str, model_id: str, influxdb_host: str, influxdb_port: int,
            influxdb_user: str, influxdb_password: str, influxdb_name: str
    ):
        self.simulation_id = simulation_id
        self.model_id = model_id
        self.lock = Lock()
        self.service_name: ServiceName = '{{ cookiecutter.service_name }}'

        # set in setup()
        self.simulation_name: Optional[str] = None
        self.simulation_start_date: Optional[datetime] = None
        self.time_step_seconds: Optional[int] = None
        self.nr_of_time_steps: Optional[int] = None
        self.esdl_energy_system: Optional[EnergySystem] = None
        self.esdl_ids: Optional[List[EsdlId]] = None
        self.esdl_objects: dict[EsdlId, esdl] = {}

        # per ESDL object:
        #     a dictionary with, per calculation service, a list of connected ESDL objects
        self.connected_input_esdl_objects_dict: dict[EsdlId, dict[ServiceName, List[EsdlId]]] = {}

        # for writing to influx db
        self.influxdb_client: InfluxDBConnector = InfluxDBConnector(
            influxdb_host, str(influxdb_port), influxdb_user, influxdb_password, influxdb_name
        )

    # setup is called upon receiving 'ModelParameters' message
    def setup(self, model_parameters: dict):
        self.simulation_name = model_parameters['simulation_name']

        self.simulation_start_date = datetime.fromtimestamp(model_parameters['start_timestamp'])
        self.time_step_seconds = int(model_parameters['time_step_seconds'])
        self.nr_of_time_steps = int(model_parameters['nr_of_time_steps'])

        # get esdl uuids and system
        self.esdl_ids = model_parameters['esdl_ids']
        self.esdl_energy_system = esdl_parser.get_energy_system(model_parameters['esdl_base64string'])

        # get esdl objects and connected services for all esdl object in the model
        for esdl_id in self.esdl_ids:
            self.esdl_objects[esdl_id] = esdl_parser.get_model_esdl_object(esdl_id, self.esdl_energy_system)
            # find connected esdl objects
            self.connected_input_esdl_objects_dict[esdl_id] = esdl_parser.get_connected_input_esdl_objects(
                esdl_id,
                model_parameters['calculation_services'],
                model_parameters['esdl_base64string']
            )

        # Optional: initialize influx db data output (with example output data names)
        # profile_output_data_names = ['temperature', 'solar_energy']
        # self.influxdb_client.init_profile_output_data(
        #     self.simulation_id, self.model_id, type(list(self.esdl_objects.values())[0]).__name__.lower(),
        #     self.simulation_start_date, self.time_step_seconds, self.nr_of_time_steps, self.esdl_ids,
        #     profile_output_data_names, self.esdl_objects
        # )

    # write_to_influxdb is called upon 'SimulationDone' message
    def write_to_influxdb(self):
        if self.influxdb_client and self.influxdb_client.simulation_id:  # only if created and initialized
            LOGGER.debug('Write to influx db')
            self.influxdb_client.write_output()

    # entry calculation function for redirection
    def calc_function(self, calc_name: str, input_data_dict: dict):
        output_data_tuple = []
        try:
            # don't allow concurrent calculations on a service
            self.lock.acquire()
            {{- service_calc_j2.ifs_calc_functions(cookiecutter)}}
            self.lock.release()
        except Exception as e:
            self.lock.release()
            raise e
        return output_data_tuple
    {{service_calc_j2.calc_functions(cookiecutter) -}}