from django.db.models.signals import post_save
from django.apps import AppConfig
from django.conf import settings
import modelstatus.core.zeromq

class ModelStatusConfig(AppConfig):
    name = 'modelstatus.core'

    def ready(self):
        """
        Set signal hook for sending zeromq messages for specific modelstatus models/resources.
        """

        self.zmq = modelstatus.core.zeromq.ZMQPublisher(settings.ZEROMQ_SUBSCRIBE_SOCKET) 
        
        publish_resources = ['ModelRun', 'DataFile', 'Data'] 
        for resource in publish_resources:
            post_save.connect(self.zmq.publish_resource, sender=self.get_model(resource))
