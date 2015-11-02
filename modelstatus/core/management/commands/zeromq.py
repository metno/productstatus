from django.core.management.base import BaseCommand, CommandError

from django.conf import settings

import zmq

class Command(BaseCommand):
    help = 'Start the ZeroMQ publisher service'

    def handle(self, *args, **options):
        context = zmq.Context(1)
        sub = context.socket(zmq.XSUB)
        pub = context.socket(zmq.XPUB)
        sub.bind(settings.ZEROMQ_SUBSCRIBE_SOCKET)
        pub.bind(settings.ZEROMQ_PUBLISH_SOCKET)

        self.stdout.write('Starting ZeroMQ proxy: sub=%s pub=%s' % (
            settings.ZEROMQ_SUBSCRIBE_SOCKET, settings.ZEROMQ_PUBLISH_SOCKET))

        zmq.proxy(sub, pub)
