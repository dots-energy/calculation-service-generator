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

import pika


def wait_for_logs():
    rabbitmq_host = "localhost"
    exchange = "dots"

    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
    channel = connection.channel()

    channel.exchange_declare(exchange=exchange, exchange_type="topic")

    queue = channel.queue_declare("", exclusive=True).method.queue

    channel.queue_bind(exchange=exchange, queue=queue, routing_key="services-log")

    def callback(ch, method, properties, body):
        message = body.decode("utf-8")
        print("\n [received] {}: {}".format(method.routing_key, message))

    channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()


if __name__ == "__main__":
    wait_for_logs()
