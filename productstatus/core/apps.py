from django.db.models.signals import post_save
from django.apps import AppConfig
from django.conf import settings

import productstatus.core.kafkapublisher


class ProductstatusConfig(AppConfig):
    name = 'productstatus.core'

    def ready(self):
        """
        Set signal hook for sending Kafka messages for specific Productstatus models/resources.
        """

        # Do not publish events using Kafka in unit test mode
        if settings.TESTING:
            return

        self.kafkapublisher = productstatus.core.kafkapublisher.KafkaPublisher()

        publish_resources = ['ProductInstance', 'DataInstance', 'Data']
        for resource in publish_resources:
            post_save.connect(self.kafkapublisher.publish_resource, sender=self.get_model(resource))
