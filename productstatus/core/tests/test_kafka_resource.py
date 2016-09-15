from . import ProductstatusResourceTest

from django.conf import settings

import tastypie.exceptions


class KafkaResourceTest(ProductstatusResourceTest):

    RESPONSE_OBJECT = {
        u'id': 'default',
        u'topic': settings.KAFKA_TOPIC,
        u'brokers': settings.KAFKA_BROKERS,
        u'ssl': settings.KAFKA_SSL,
        u'ssl_verify': settings.KAFKA_SSL_VERIFY,
        u'heartbeat_interval': settings.KAFKA_HEARTBEAT_INTERVAL,
        u'resource_uri': '/api/v1/kafka/default/',
    }

    def test_get_collection(self):
        """!
        @brief Test that the Kafka configuration details are returned as a list.
        """
        url = "%s/kafka/" % self.url_prefix
        response = self.api_client.get(url, format='json')
        self.assertValidJSONResponse(response)

        decoded_content = self.unserialize(response)
        self.assertListEqual(decoded_content['objects'], [self.RESPONSE_OBJECT])

    def test_get_resource_default(self):
        """!
        @brief Test that the Kafka configuration details are returned.
        """
        url = "%s/kafka/default/" % self.url_prefix
        response = self.api_client.get(url, format='json')
        self.assertValidJSONResponse(response)

        decoded_content = self.unserialize(response)
        self.assertDictEqual(decoded_content, self.RESPONSE_OBJECT)

    def test_get_resource_not_found(self):
        """!
        @brief Test that the Kafka configuration details are not returned for a
        resource id other than 'default'.
        """
        url = "%s/kafka/foo/" % self.url_prefix
        with self.assertRaises(tastypie.exceptions.NotFound):
            self.api_client.get(url, format='json')
