from productstatus.core.models import ProductInstance
from . import BaseTestCases


class ProductInstanceCollectionTest(BaseTestCases.ProductstatusCollectionTest):

    def setUp(self):
        super(ProductInstanceCollectionTest, self).setUp()

        self.base_url = "%s%s" % (self.url_prefix, '/productinstance/')
        self.detail_url = "%s%s/" % (self.base_url, "88d28ffd-d448-4319-a94e-16889955f94a")
        self.collection_size = 3
        self.post_data = {
            'product': '/api/v1/product/7d3fe736-5902-44d5-a34c-86f877190523/',
            'state': 0,
            'reference_time': '2015-10-29T00:00:00Z',
            }

        self.__model_class__ = ProductInstance

    def test_post_own_id_overridden(self):
        """
        Test that the API does not store productinstance with 'id' parameter specified
        in a POST request.
        """
        self.post_data['id'] = '683ec0f1-1843-43e1-b0be-52c0b6a03741'
        resp = self.api_client.post(self.base_url, format='json', data=self.post_data,
                                    authentication=self.api_key_header)

        self.assertEqual(ProductInstance.objects.count(), self.collection_size + 1)
        self.assertEqual(resp.status_code, 201)
        with self.assertRaises(ProductInstance.DoesNotExist):
            ProductInstance.objects.get(id='683ec0f1-1843-43e1-b0be-52c0b6a03741')

    def test_get_collection_with_filter(self):
        """
        Test that productinstance filters by reference_time and product, by filtering so the response
        is a collection of 0 objects.
        """
        query_string = "product=7d3fe736-5902-44d5-a34c-86f877190523&reference_time=2015-12-08T12:00:00Z&order_by=version&limit=1"
        resp = self.api_client.get("%s?%s" % (self.base_url, query_string), format='json')
        self.assertValidJSONResponse(resp)

        decoded_content = self.unserialize(resp)
        self.assertEqual(len(decoded_content['objects']), 0)

    def test_order_by_asc(self):
        """
        Test that order by asc works
        """
        query_string = "order_by=reference_time"
        resp = self.api_client.get("%s?%s" % (self.base_url, query_string), format='json')
        self.assertValidJSONResponse(resp)

        decoded_content = self.unserialize(resp)
        self.assertEqual(decoded_content['objects'][0]['reference_time'], '2015-10-01T00:00:00Z')

    def test_order_by_desc(self):
        """
        Test that order by asc works
        """
        query_string = "order_by=-reference_time"
        resp = self.api_client.get("%s?%s" % (self.base_url, query_string), format='json')
        self.assertValidJSONResponse(resp)

        decoded_content = self.unserialize(resp)
        self.assertEqual(decoded_content['objects'][0]['reference_time'], '2015-12-08T00:00:00Z')

    def test_increment_version(self):
        """
        The version field should be incremented if the data_provider
        and reference_time has been posted before.
        """
        first_resp = self.api_client.post(self.base_url, format='json', data=self.post_data,
                                          authentication=self.api_key_header)
        second_resp = self.api_client.post(self.base_url, format='json', data=self.post_data,
                                           authentication=self.api_key_header)

        first_version = self._get_version_from_resource(first_resp['Location'])
        second_version = self._get_version_from_resource(second_resp['Location'])

        self.assertTrue(first_version < second_version)

    def test_set_version(self):
        """
        Store version field instead of autoincrement when version is specified in the json payload.
        """
        test_version = 13
        self.post_data['version'] = test_version
        resp = self.api_client.post(self.base_url, format='json', data=self.post_data,
                                    authentication=self.api_key_header)

        version_in_response = self._get_version_from_resource(resp['Location'])

        self.assertEqual(test_version, version_in_response)

    def test_fail_on_bogus_post(self):
        """
        Tests that a POST fails when the uri to product is erroneous
        """
        bogus_data = {
            'model': '/api/v1/product/d0c6ffbe-f4ee-48e3-8005-1df56ad67076/',
            'reference_time': '2015-10-29T00:00:00Z',
            }
        response = self.api_client.post(self.base_url, format='json', data=bogus_data,
                                        authentication=self.api_key_header)

        self.assertEqual(response.status_code, 400)

    def _get_version_from_resource(self, url):
        response = self.api_client.get(url, format='json')

        return self.unserialize(response)['version']


class ProductInstanceItemTest(BaseTestCases.ProductstatusItemTest):

    def setUp(self):
        super(ProductInstanceItemTest, self).setUp()

        self.item_uuid = "c491e9c8-0abd-4763-ba50-efcf6e6c2f25"
        self.base_url = "%s%s%s/" % (self.url_prefix, '/productinstance/', self.item_uuid)
