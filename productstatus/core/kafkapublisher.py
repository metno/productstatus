from django.conf import settings

import datetime
import dateutil.tz
import uuid
import logging
import json
import kafka


MESSAGE_PROTOCOL_VERSION = [1, 4, 0]


class KafkaPublisher(object):
    """!
    KafkaPublisher is responsible for sending out messages about new
    or updated resources.
    """

    def __init__(self, brokers, client_id, topic, timeout):
        self.brokers = brokers
        self.client_id = client_id
        self.topic = topic
        self.timeout = timeout
        self.json_producer = kafka.KafkaProducer(bootstrap_servers=self.brokers,
                                                 client_id=self.client_id,
                                                 acks=1,
                                                 value_serializer=lambda m: json.dumps(m).encode('utf-8'))

    def publish_resource(self, instance):
        """!
        @brief Publish a model instance to the configured Kafka topic.
        """

        msg = KafkaPublisher.resource_message(instance)
        self.send_message(msg)

    def send_message(self, msg):
        """
        Send a json message to Kafka.
        """

        future = self.json_producer.send(self.topic, msg)

        try:
            # make sure messages are sent immediately and throws an exception on failure
            record_metadata = future.get(timeout=self.timeout)
        except kafka.common.KafkaError:
            logging.critical("Failed to send json message to Kafka")
            raise

        logging.info("Published message to Kafka (topic: %s, partition: %s, offset: %s): %s"
                     % (record_metadata.topic, record_metadata.partition, record_metadata.offset, msg))

    @staticmethod
    def resource_message(model_instance):
        """
        Kafka collects and distributes messages with information about what
        resources have changed and where to go to get all information
        about each resource.
        """

        msg = {
            'message_id': unicode(uuid.uuid4()),
            'message_timestamp': datetime.datetime.utcnow().replace(tzinfo=dateutil.tz.tzutc()).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'url': model_instance.full_url(),
            'uri': model_instance.full_uri(),
            'version': MESSAGE_PROTOCOL_VERSION,
            'resource': model_instance.resource_name(),
            'type': 'resource',
            'id': str(model_instance.id),
            }

        return msg
