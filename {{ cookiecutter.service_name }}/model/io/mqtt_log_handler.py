#!/usr/bin/env python
import logging
from logging import StreamHandler, LogRecord, Formatter

from model.io.mqtt_client import MqttClient


class MqttLogHandler(StreamHandler):
    def __init__(self, client: MqttClient):
        StreamHandler.__init__(self)
        formatter = Formatter(
            fmt="%(asctime)s [%(threadName)s][%(filename)s:%(lineno)d][%(levelname)s]: %(message)s"
        )
        super().setFormatter(formatter)
        self.client = client

    def emit(self, record: LogRecord):
        if record.levelno >= logging.INFO:
            self.client.send_log(self.format(record))
