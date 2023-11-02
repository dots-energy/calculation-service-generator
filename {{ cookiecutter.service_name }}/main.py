#!/usr/bin/env python
import os
import typing
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env
from model.io.log import LOCAL_LOGGER
from model.service import Service


class EnvConfig:
    CONFIG_KEYS = [
        ("SIMULATION_ID", None, str, False),
        ("MODEL_ID", None, str, False),
        ("MQTT_HOST", "localhost", str, False),
        ("MQTT_PORT", "1883", int, False),
        ("MQTT_QOS", "0", int, False),
        ("MQTT_USERNAME", "", str, False),
        ("MQTT_PASSWORD", "", str, True),
        ("INFLUXDB_HOST", "", str, False),
        ("INFLUXDB_PORT", "", str, False),
        ("INFLUXDB_USER", "", str, False),
        ("INFLUXDB_PASSWORD", "", str, True),
        ("INFLUXDB_NAME", "", str, False),
    ]

    @staticmethod
    def load(
        keys: typing.List[typing.Tuple[str, typing.Optional[str], typing.Any, bool]]
    ) -> typing.Dict[str, typing.Any]:
        result = {}
        LOCAL_LOGGER.info("Config:")
        max_length_name = max(len(key[0]) for key in keys)
        for name, default, transform, hide in keys:
            if default is None and (name not in os.environ):
                raise Exception(f"Missing environment variable {name}")

            env_value = os.getenv(name, default)
            LOCAL_LOGGER.info(
                f'    {f"{name}:".ljust(max_length_name + 4)}{"<hidden>" if hide else env_value}'
            )
            result[name] = transform(env_value)
        LOCAL_LOGGER.info("")

        return result


def main():
    config = EnvConfig.load(EnvConfig.CONFIG_KEYS)

    Service(config).start()
    LOCAL_LOGGER.info(
        f"Service '{{ cookiecutter.service_name }}: {config['MODEL_ID']}' terminated"
    )


if __name__ == "__main__":
    main()
