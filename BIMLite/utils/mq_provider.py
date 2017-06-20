__author__ = 'naveen.krishnan'

import logging

import pika

from BIMLite.config import config


class MQProvider(object):
    def __init__(self):
        self.log = logging.getLogger(__name__)
        self.mq = config.get_notification_mq()
        self.exchange = self.mq['MESSAGE_QUEUE_EXCHANGE']
        self.user_name = self.mq['MESSAGE_QUEUE_USERNAME']
        self.password = self.mq['MESSAGE_QUEUE_PASSWORD']
        self.host = self.mq['MESSAGE_QUEUE_SERVER']
        self.port = int(self.mq['MESSAGE_QUEUE_PORT'])
        self.vhost = self.mq['MESSAGE_QUEUE_VHOST']
        self.queue_name = self.mq['MESSAGE_QUEUE_NAME_NOTIFICATION']
        self.routing_key = self.mq['MESSAGE_QUEUE_PASSWORD']
        self.connection = self._create_mq_connection()

    def _create_mq_connection(self):  # return a pika connection
        connection = None
        try:
            self.log.debug("Creating new Rabbitmq connection")
            credentials = pika.PlainCredentials(self.user_name, self.password)
            parameters = pika.ConnectionParameters(host=self.host,
                                                   port=self.port,
                                                   virtual_host=self.vhost,
                                                   credentials=credentials)
            self.log.debug(
                "Opening connection to the message queue running in Server : {} port : {}".format(
                    self.host, self.port))
            connection = pika.BlockingConnection(parameters)
            self.log.debug("Connection created")
        except Exception as exception:
            raise exception
        return connection

    def publish_message_to_queue(self, queue=None, routing_key=None, headers=None, message=None):
        try:
            self.log.debug("Initiating open connection to the message queue")
            self.channel = self.connection.channel()
            self.channel.exchange_declare(exchange=self.exchange, durable=True)
            self.channel.queue_declare(queue=queue, durable=True)
            self.channel.queue_bind(exchange=self.exchange, queue=queue, routing_key=routing_key)
            headers = {'NotificationVersion': 2}
            self._push_data_to_messagequeue(routing_key, headers, message)
            self.log.info("Done publishing message to the message queue")
        except Exception as exception:
            raise exception

    def _push_data_to_messagequeue(self, routing_key, headers, message):
        try:
            self.log.debug("Entered into DataLogger > push_data_to_messagequeue()")
            self.log.debug("Message -- %s -- is ready to publish", message)
            properties = pika.BasicProperties(headers=headers, content_type="text/plain")
            self.channel.basic_publish(exchange=self.exchange,
                                       routing_key=routing_key,
                                       body=message, properties=properties)
            self.log.debug("Message published successfully")
            self.channel.close()
            self.connection.close()
        except Exception as exception:
            raise exception
