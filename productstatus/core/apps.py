from django.apps import AppConfig
from django.conf import settings

import productstatus.core.kafkapublisher


class EventPublisher(AppConfig):
    name = 'productstatus.core'

    def ready(self):
        """!
        @brief Ensure Kafka publisher will be instantiated later.
        """
        self.publisher = None

    def send_message(self, instance):
        """!
        @brief Instantiate Kafka publisher if needed, then publish a message about a model instance.
        """
        if settings.TESTING:
            return
        if not self.publisher:
            self.publisher = productstatus.core.kafkapublisher.KafkaPublisher(
                settings.KAFKA_BROKERS,
                settings.KAFKA_CLIENT_ID,
                settings.KAFKA_TOPIC,
                settings.KAFKA_REQUEST_TIMEOUT,
            )
        self.publisher.publish_resource(instance)
