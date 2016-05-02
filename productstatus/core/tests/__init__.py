import json
import copy
import django.test

from tastypie.test import ResourceTestCaseMixin


class ProductstatusResourceTest(ResourceTestCaseMixin, django.test.TestCase):
    """
    Base test resource that setup attributes and methods common to all
    test classes. This class will be inherited by the BaseTestCases.* classes.
    """

    fixtures = ['core.json']

    def setUp(self):
        super(ProductstatusResourceTest, self).setUp()

        self.url_prefix = '/api/v1'

        # create_apikey generates an Authorization HTTP header. The key itself
        # is already in the fixture.
        self.api_key_header = self.create_apikey(
            'foo',
            'd54f9200b680ff11eb1ffcb01a99bde2abcdefab',
        )

    def unserialize(self, response):
        return json.loads(response.content.decode('UTF-8'))


class BaseTestCases:
    """
    Nested base test classes so the unittest framework won't run the tests defined here.
    """

    class ProductstatusCollectionTest(ProductstatusResourceTest):
        """
        The tests defined here will be run for all the classes that inherit this baseclass.
        Please note that each subclass MUST set all the attributes in their own
        setUp method.
        """

        def setUp(self):
            super(BaseTestCases.ProductstatusCollectionTest, self).setUp()

            self.collection_size = 0
            self.base_url = self.url_prefix
            self.post_data = {}
            self.__model_class__ = None

        def test_post_collection_with_correct_size(self):
            """
            Test that you self.post_data can be posted to resource and that the collection size
            is correct.
            """
            self.assertEqual(self.__model_class__.objects.count(), self.collection_size)
            response = self.api_client.post(self.base_url,
                                            format='json',
                                            data=self.post_data,
                                            authentication=self.api_key_header)
            self.assertHttpCreated(response)
            self.assertEqual(self.__model_class__.objects.count(), self.collection_size + 1)

        def test_put_object_with_correct_size(self):
            """
            Test that data saved using a PUT does not create a new entry.
            """
            self.api_client.post(self.base_url, format='json', data=self.post_data,
                                 authentication=self.api_key_header)
            object_ = self.__model_class__.objects.all()[0]
            data = copy.copy(self.post_data)
            data['id'] = str(object_.id)
            self.api_client.put(self.base_url, format='json', data=data, authentication=self.api_key_header)
            self.assertEqual(self.__model_class__.objects.count(), self.collection_size + 1)

        def test_get_collection(self):
            """
            Test that api returns a valid json response and with correct number of objects
            """
            response = self.api_client.get(self.base_url, format='json')
            self.assertValidJSONResponse(response)
            self.assertEqual(len(self.unserialize(response)['objects']), self.collection_size)

    class ProductstatusItemTest(ProductstatusResourceTest):

        def setUp(self):
            super(BaseTestCases.ProductstatusItemTest, self).setUp()

            self.base_url = self.url_prefix
