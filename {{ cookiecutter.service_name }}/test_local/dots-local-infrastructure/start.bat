copy dots-local-infrastructure\unencrypted_password_file.conf dots-local-infrastructure\mqtt_passwd
docker run --rm -v "%cd%\dots-local-infrastructure\mqtt_passwd:\mosquitto\config\mqtt_passwd" eclipse-mosquitto mosquitto_passwd -U \mosquitto\config\mqtt_passwd

docker-compose --file dots-local-infrastructure\docker-compose.yml up