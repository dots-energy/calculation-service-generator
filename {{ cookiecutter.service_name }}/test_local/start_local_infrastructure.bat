@ECHO OFF

echo Starting MQTT broker...
:: Choose Mosquitto or RabbitMQ
call dots-local-infrastructure\start.bat
:: call rabbitmq-mqtt\run_rabbitmq_mqtt.bat
