import django.test

import productstatus.core.models
import productstatus.core.kafkapublisher


class KafkaPublisherTest(django.test.TestCase):

    fixtures = ['core.json']

    def test_event_uri(self):
        data_instance = productstatus.core.models.DataInstance.objects.get(id='ae443952-7990-4cee-9913-41dfd0092dc1')
        event_hash = productstatus.core.kafkapublisher.KafkaPublisher.resource_message(data_instance)
        assert event_hash['uri'] == '/api/v1/datainstance/ae443952-7990-4cee-9913-41dfd0092dc1/'
        assert event_hash['object_version'] == 0
