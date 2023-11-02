import os
import logging

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

LOCAL_LOGGER = logging.getLogger("local-logger")
SIM_LOGGER = logging.getLogger("sim-logger")

logging.basicConfig(
    format="%(asctime)s [%(threadName)s][%(filename)s:%(lineno)d][%(name)s-%(levelname)s]: %(message)s",
    level=LOG_LEVEL,
    datefmt="%m/%d/%Y %I:%M:%S %p",
)
