from django.apps import AppConfig
from django.conf import settings

import productstatus.core.kafkapublisher


class EventPublisher(AppConfig):
    name = 'productstatus.core'

    def ready(self):
        """!
        @brief Instantiate Kafka publisher object unless in test mode.
        """
        if settings.TESTING:
            self.publisher = None
        else:
            self.publisher = productstatus.core.kafkapublisher.KafkaPublisher(
                settings.KAFKA_BROKERS,
                settings.KAFKA_CLIENT_ID,
                settings.KAFKA_TOPIC,
                settings.KAFKA_REQUEST_TIMEOUT,
            )

    def send_message(self, instance):
        """!
        @brief Publish a message about a model instance.
        """
        if not self.publisher:
            return
        self.publisher.publish_resource(instance)
