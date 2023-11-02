#!/bin/bash

echo Starting MQTT broker...
# Choose Mosquitto or RabbitMQ
dots-local-infrastructure/start.sh
# rabbitmq-mqtt/run_rabbitmq_mqtt.bat