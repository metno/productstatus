from modelstatus.core.models import ModelRun
from . import BaseTestCases


class ModelRunCollectionTest(BaseTestCases.ModelstatusCollectionTest):

    def setUp(self):
        super(ModelRunCollectionTest, self).setUp()

        self.base_url = "%s%s" % (self.url_prefix, '/model_run/')
        self.detail_url = "%s%s/" % (self.base_url, "c491e9c8-0abd-4763-ba50-efcf6e6c2f25")
        self.collection_size = 2
        self.post_data = {
            'model': '/api/v1/model/66340f0b-2c2c-436d-a077-3d939f4f7283/',
            'reference_time': '2015-10-29T00:00:00Z',
            }

        self.__model_class__ = ModelRun

    def test_post_fails_on_id(self):
        """
        Test that the API does not store model_run with 'id' parameter specified
        in a POST request.
        """
        self.post_data['id'] = '683ec0f1-1843-43e1-b0be-52c0b6a03741'
        self.assertEqual(ModelRun.objects.count(), 2)
        resp = self.api_client.post(self.base_url, format='json', data=self.post_data,
                                    authentication=self.api_key_header)

        self.assertEqual(ModelRun.objects.count(), 3)
        self.assertEqual(resp.status_code, 201)
        with self.assertRaises(ModelRun.DoesNotExist):
            ModelRun.objects.get(id='683ec0f1-1843-43e1-b0be-52c0b6a03741')

    def test_get_collection_with_filter(self):
        """
        Test that model_run filters by reference_time and model, by filtering so the response
        is a collection of 0 objects.
        """
        query_string = "model=66340f0b-2c2c-436d-a077-3d939f4f7283&reference_time=2015-10-28T12:00:00Z&order_by=version&limit=1"
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
        self.assertEqual(decoded_content['objects'][0]['reference_time'], '2015-10-28T00:00:00Z')

    def test_order_by_desc(self):
        """
        Test that order by asc works
        """
        query_string = "order_by=-reference_time"
        resp = self.api_client.get("%s?%s" % (self.base_url, query_string), format='json')
        self.assertValidJSONResponse(resp)

        decoded_content = self.unserialize(resp)
        self.assertEqual(decoded_content['objects'][0]['reference_time'], '2015-11-05T18:00:00Z')

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

    def test_fail_on_bogus_post(self):
        """
        Tests that a POST fails when the uri to model is erroneous
        """
        bogus_data = {
            'model': '/api/v1/model/d0c6ffbe-f4ee-48e3-8005-1df56ad67076/',
            'reference_time': '2015-10-29T00:00:00Z',
            }
        response = self.api_client.post(self.base_url, format='json', data=bogus_data)

        self.assertEqual(response.status_code, 400)

    def _get_version_from_resource(self, url):
        response = self.api_client.get(url, format='json')

        return self.unserialize(response)['version']


class ModelRunItemTest(BaseTestCases.ModelstatusItemTest):

    def setUp(self):
        super(ModelRunItemTest, self).setUp()

        self.item_uuid = "c491e9c8-0abd-4763-ba50-efcf6e6c2f25"
        self.base_url = "%s%s%s/" % (self.url_prefix, '/model_run/', self.item_uuid)
