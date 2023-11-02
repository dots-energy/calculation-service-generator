#!/bin/bash

cp ./dots-local-infrastructure/unencrypted_password_file.conf dots-local-infrastructure/mqtt_passwd.temp
mv dots-local-infrastructure/mqtt_passwd.temp dots-local-infrastructure/mqtt_passwd
docker run --rm -v "$PWD/dots-local-infrastructure/mqtt_passwd:/mosquitto/config/mqtt_passwd" eclipse-mosquitto mosquitto_passwd -U /mosquitto/config/mqtt_passwd

docker-compose --file ./mosquitto/docker-compose.yml up