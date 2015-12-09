from django.conf import settings

import errno
import logging
import zmq


MESSAGE_PROTOCOL_VERSION = [1, 2, 0]


class ZMQPublisher(object):
    """
    ZMQPublisher is responsible for sending out messages about new
    or updated resources.

    The method publish_resource should be connected
    as a callback function to a signal for models we wish to send out
    messages about. Do this in productstatus.core.apps.
    """

    def __init__(self, socket_str):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.connect(settings.ZEROMQ_SUBSCRIBE_SOCKET)

    def publish_resource(self, sender, instance, **kwargs):
        """
        This message should be used as hook for django signals.
        Creates and sends zeromq messages based on the parameters from the signal.
        """

        msg = ZMQPublisher.resource_message(instance)
        self.send_message(msg)

    def send_message(self, msg):
        """
        Send zeromq json message.
        """

        error_count = 0
        while True:
            try:
                self.socket.send_json(msg)
                break
            except zmq.ZMQError as e:
                if e.errno == errno.EINTR:
                    if error_count < 2:
                        logging.warn("Interrupted while transmitting ZeroMQ message, retrying")
                        error_count += 1
                        continue
                    else:
                        logging.critical("ZeroMQ sending has been interrupted multiple times..Giving up!")
                        raise
                else:
                    raise
        logging.info("Published ZeroMQ message: %s" % msg)

    @staticmethod
    def resource_message(model_instance):
        """
        Zeromq message should give information about what resource have changed
        and where to go to get all information about the resource.
        """

        resource_name = ZMQPublisher.get_resource_name(model_instance)
        msg = {
            'url': "%s://%s%s/%s/%s/" % (settings.PRODUCTSTATUS_PROTOCOL,
                                         settings.PRODUCTSTATUS_HOST,
                                         settings.PRODUCTSTATUS_BASE_PATH,
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
        Return the name of the resource that represents the collection model_instance is in.
        """

        return model_instance.__class__.__name__.lower()
