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

import typing, numpy, datetime
from influxdb import InfluxDBClient
from model.types import EsdlId
from esdl import esdl

from model.io.log import LOCAL_LOGGER as LOGGER


class InfluxDBConnector:
    """A connector writes data to an InfluxDB database."""

    def __init__(
            self,
            influx_host: str,
            influx_port: str,
            influx_user: str,
            influx_password: str,
            influx_database_name: str
    ):
        self.influx_host: str = influx_host.split("//")[-1]
        self.influx_port: str = influx_port
        self.influx_database_name: str = influx_database_name
        self.influx_user: str = influx_user
        self.influx_password: str = influx_password

        LOGGER.debug("influx server: {}".format(self.influx_host))
        LOGGER.debug("influx port: {}".format(self.influx_port))
        LOGGER.debug("influx database: {}".format(self.influx_database_name))

        self.client: typing.Optional[InfluxDBClient] = None
        self.simulation_id: typing.Optional[str] = None
        self.model_id: typing.Optional[str] = None
        self.esdl_type: typing.Optional[str] = None
        self.start_date: typing.Optional[datetime] = None
        self.time_step_seconds: typing.Optional[int] = None
        self.nr_of_time_steps: typing.Optional[int] = None
        self.profile_output_data: dict = {}
        self.summary_output_data: dict = {}
        self.esdl_objects: typing.Optional[dict[EsdlId, esdl]] = None

    def connect(self) -> InfluxDBClient:
        client = None
        try:
            LOGGER.debug("Connecting InfluxDBClient")
            client = InfluxDBClient(
                host=self.influx_host,
                port=self.influx_port,
                database=self.influx_database_name,
                username=self.influx_user,
                password=self.influx_password,
            )
            LOGGER.debug("InfluxDBClient ping: {}".format(client.ping()))
            self.client = client
        except Exception as e:
            LOGGER.debug("Failed to connect to influx db: {}".format(e))
            if client:
                client.close()
            self.client = None
        return self.client

    def query(self, query):
        if self.client is None:
            self.connect()

        return self.client.query(query)

    def create_database(self):
        if self.client is None:
            self.connect()
        self.client.create_database(self.influx_database_name)

    def write(self, msgs):
        if self.client is None:
            self.connect()

        # Send message to database.
        self.client.write_points(
            msgs, database=self.influx_database_name, time_precision="s"
        )

    def close(self):
        if self.client:
            self.client.close()
        self.client = None

    def init_profile_output_data(
            self,
            simulation_id: str,
            model_id: str,
            esdl_type: str,
            start_date: datetime,
            time_step_seconds: int,
            nr_of_time_steps: int,
            esdl_ids: typing.List[EsdlId],
            output_names: typing.List[str],
            esdl_objects: dict[EsdlId, esdl],
    ):
        self.simulation_id = simulation_id
        self.esdl_type = esdl_type
        self.model_id = model_id
        self.start_date = start_date
        self.time_step_seconds = time_step_seconds
        self.nr_of_time_steps = nr_of_time_steps
        for esdl_id in esdl_ids:
            self.profile_output_data[esdl_id] = {}
            for output_name in output_names:
                self.profile_output_data[esdl_id][output_name] = numpy.zeros(self.nr_of_time_steps)
            self.summary_output_data[esdl_id] = {}
        self.esdl_objects = esdl_objects

    def set_time_step_data_point(self, esdl_id: EsdlId, output_name: str, time_step_nr: int, value: float):
        self.profile_output_data[esdl_id][output_name][time_step_nr - 1] = float(value)

    def set_summary_data_point(self, esdl_id: EsdlId, output_name: str, value: float):
        self.summary_output_data[esdl_id][output_name] = float(value)

    def write_output(self):
        points = list()
        first_timestamp = None

        for i_step in range(self.nr_of_time_steps):
            step_time = (
                    self.start_date + datetime.timedelta(0, i_step * self.time_step_seconds)
            ).strftime("%Y-%m-%dT%H:%M:%SZ")
            if first_timestamp is None:
                first_timestamp = step_time

            for esdl_id, esdl_object_profile_output_data in self.profile_output_data.items():
                fields = {}
                for output_name in esdl_object_profile_output_data.keys():
                    if i_step < len(esdl_object_profile_output_data[output_name]):
                        fields[output_name] = esdl_object_profile_output_data[output_name][
                            i_step
                        ]
                    else:  # allow data writing even if simulation was terminated
                        fields[output_name] = 0.0
                self.add_measurement(points, esdl_id, step_time, fields)

        if self.summary_output_data:
            for esdl_id, esdl_object_summary_output_data in self.summary_output_data.items():
                fields = {}
                for output_name in esdl_object_summary_output_data.keys():
                    fields[output_name] = esdl_object_summary_output_data[output_name]
                if fields:
                    self.add_measurement(points, esdl_id, first_timestamp, fields)

        LOGGER.info(
            f"InfluxDB writing {len(points)} points to measurement '{self.esdl_type}'"
            f" with tag simulationRun {self.simulation_id}"
        )
        self.write(points)

    def add_measurement(self, points, esdl_id, timestamp, fields):
        try:
            if hasattr(self.esdl_objects[esdl_id], 'name'):
                esdl_name = self.esdl_objects[esdl_id].name
            else:
                esdl_name = self.esdl_type
            item = {
                "measurement": f"{self.esdl_type}",
                "tags": {
                    "simulation_id": self.simulation_id,
                    "model_id": self.model_id,
                    "esdl_id": esdl_id,
                    "esdl_name": esdl_name,
                },
                "time": timestamp,
                "fields": fields,
            }
            points.append(item)
        except Exception as e:
            LOGGER.debug(f"Exception: {e} {e.args}")
