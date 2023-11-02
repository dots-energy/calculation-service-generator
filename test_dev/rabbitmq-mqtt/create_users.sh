#!/bin/sh

# Create Rabbitmq user
( rabbitmq_ready=1 ; \
while [ $rabbitmq_ready -ne 0 ]
do
  echo "wait for rabbitmq to be ready..." ; \
  sleep 3 ; \
  rabbitmqctl status 2>null ; \
  rabbitmq_ready=$? ; \
done

echo "rabbitmq ready: adding users"

rabbitmqctl add_user $RABBITMQ_ADMIN_USER $RABBITMQ_ADMIN_PASSWORD 2>/dev/null
rabbitmqctl set_user_tags $RABBITMQ_ADMIN_USER administrator ; \
rabbitmqctl set_permissions -p / $RABBITMQ_ADMIN_USER  ".*" ".*" ".*" ; \
rabbitmqctl add_user $RABBITMQ_DOTS_USER $RABBITMQ_DOTS_PASSWORD 2>/dev/null ; \
rabbitmqctl set_user_tags $RABBITMQ_DOTS_USER management ; \
rabbitmqctl set_permissions -p / $RABBITMQ_DOTS_USER  ".*" ".*" ".*" ; \
rabbitmqctl delete_user guest ; \
echo "*** Admin User: '$RABBITMQ_ADMIN_USER' with password '$RABBITMQ_ADMIN_PASSWORD' completed. ***" ; \
echo "*** API User: '$RABBITMQ_DOTS_USER' with password '$RABBITMQ_DOTS_PASSWORD' completed. ***") &

# $@ is used to pass arguments to the rabbitmq-server command.
# For example if you use it like this: docker run -d rabbitmq arg1 arg2,
# it will be as you run in the container rabbitmq-server arg1 arg2
rabbitmq-server $@