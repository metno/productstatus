from django.core.management.base import BaseCommand, CommandError
from django.apps import apps as django_apps
from django.conf import settings

import django.db

import productstatus.core.kafkapublisher
import productstatus.core.models

import time
import json
import logging
import timeit


class Command(BaseCommand):
    help = 'Runs the Kafka publisher'

    def needs_heartbeat(self):
        return timeit.default_timer() >= self.next_heartbeat_time

    def send_heartbeat(self):
        msg = productstatus.core.kafkapublisher.KafkaPublisher.heartbeat_message()
        self.next_heartbeat_time = timeit.default_timer() + settings.KAFKA_HEARTBEAT_INTERVAL
        self.app.send_message(msg)
        self.heartbeat_count += 1
        logging.debug('Sent heartbeat %d', self.heartbeat_count)

    def send_pending(self):
        messages = productstatus.core.models.PendingMessage.all_pending()
        for message in messages:
            with django.db.transaction.atomic():
                id = message.id
                message.delete()
                self.app.send_message(json.loads(message.message))
            logging.info('Message %s has been sent and deleted from the pending message queue', id)

    def handle(self, *args, **options):
        logging.info('Starting Kafka publisher')
        self.app = django_apps.get_app_config('core')
        self.next_heartbeat_time = 0
        self.heartbeat_count = 0
        while True:
            if self.needs_heartbeat():
                self.send_heartbeat()
            self.send_pending()
            time.sleep(1)
