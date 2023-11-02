#!/usr/bin/env python
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
