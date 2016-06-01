from django.core.management.base import BaseCommand, CommandError
from django.apps import apps as django_apps

import django.db

import productstatus.core.kafkapublisher
import productstatus.core.models

import time
import json
import logging


class Command(BaseCommand):
    help = 'Runs the Kafka publisher'

    def handle(self, *args, **options):
        logging.info('Starting Kafka publisher')
        app = django_apps.get_app_config('core')
        while True:
            messages = productstatus.core.models.PendingMessage.all_pending()
            for message in messages:
                with django.db.transaction.atomic():
                    id = message.id
                    message.delete()
                    app.send_message(json.loads(message.message))
                logging.info('Message %s has been sent and deleted from the message queue', id)
            time.sleep(1)
