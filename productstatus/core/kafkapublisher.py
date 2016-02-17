from django.conf import settings

import logging
import json
import kafka


MESSAGE_PROTOCOL_VERSION = [1, 3, 0]


class KafkaPublisher(object):
    """
    KafkaPublisher is responsible for sending out messages about new
    or updated resources.

    The method publish_resource should be connected
    as a callback function to a signal for models we wish to send out
    messages about. Do this in productstatus.core.apps.
    """

    def __init__(self):
        self.json_producer = kafka.KafkaProducer(bootstrap_servers=settings.KAFKA_BROKERS,
                                                 client_id=settings.KAFKA_CLIENT_ID,
                                                 value_serializer=lambda m: json.dumps(m).encode('utf-8'))

    def publish_resource(self, sender, instance, **kwargs):
        """
        This method is used as a hook for django signals.
        Creates json messages based on the parameters from the signal
        and publishes then via Kafka.
        """

        msg = KafkaPublisher.resource_message(instance)
        self.send_message(msg)

    def send_message(self, msg):
        """
        Send a json message to Kafka.
        """

        future = self.json_producer.send(settings.KAFKA_TOPIC, msg)

        try:
            record_metadata = future.get(timeout=10)
        except kafka.common.KafkaError:
            logging.critical("Failed to send json message to Kafka")
            raise

        logging.info("Published message to Kafka (topic: %s, partition: %s, offset:%s): %s"
                     % (record_metadata.topic, record_metadata.partition, record_metadata.offset, msg))

    @staticmethod
    def resource_message(model_instance):
        """
        Kafka collects and distributes messages with information about what
        resources have changed and where to go to get all information
        about each resource.
        """

        resource_name = KafkaPublisher.get_resource_name(model_instance)
        msg = {
            'url': "%s://%s%s/%s/%s/" % (settings.PRODUCTSTATUS_PROTOCOL,
                                         settings.PRODUCTSTATUS_HOST,
                                         settings.PRODUCTSTATUS_BASE_PATH,
                                         resource_name,
                                         model_instance.id),
            'uri': '%s/%s/%s/' % (settings.PRODUCTSTATUS_BASE_PATH,
                                  resource_name,
                                  model_instance.id),
            'version': MESSAGE_PROTOCOL_VERSION,
            'resource': resource_name,
            'type': 'resource',
            'id': str(model_instance.id)
            }

        return msg

    @staticmethod
    def get_resource_name(model_instance):
        """
        Return the name of the resource that represents the collection
        model_instance is in.
        """

        return model_instance.__class__.__name__.lower()
