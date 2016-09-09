import django.test

import productstatus.core.lookup


class LookupTest(django.test.TestCase):
    """!
    Tests for the search functions.
    """

    fixtures = ['core.json']

    def setUp(self):
        pass

    def test_get_objects_from_field(self):
        """!
        @brief Test that any core models can be retrieved using a lookup function.
        """
        products = productstatus.core.lookup.get_objects_from_field('id', '7d3fe736-5902-44d5-a34c-86f877190523')
        self.assertEqual(len(products), 1)
        self.assertIsInstance(products[0], productstatus.core.models.Product)
        self.assertEqual(products[0].slug, 'test-product')
        service_backends = productstatus.core.lookup.get_objects_from_field('pk', '495bb3be-e327-4840-accf-afefcd411e06')
        self.assertEqual(len(service_backends), 1)
        self.assertIsInstance(service_backends[0], productstatus.core.models.ServiceBackend)
        self.assertEqual(service_backends[0].slug, 'datastore1')

    def test_lookup_uuid(self):
        """!
        @brief Test that querying for a string containing an UUID returns the proper object.
        """
        result = productstatus.core.lookup.lookup_uuid('Foo bar /api/v1/datainstance/ae443952-7990-4cee-9913-41dfd0092dc1/')
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], productstatus.core.models.DataInstance)
        self.assertEqual(str(result[0].id), 'ae443952-7990-4cee-9913-41dfd0092dc1')

    def test_lookup_slug(self):
        """!
        @brief Test that querying for a string that is a slug returns the proper object.
        """
        result = productstatus.core.lookup.lookup_slug('foo-bar')
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], productstatus.core.models.Person)
        self.assertEqual(str(result[0].id), 'b407e09d-b0c4-4289-95fe-75a2497f6eaa')

    def test_lookup_name(self):
        """!
        @brief Test that querying for a string that is a name returns the proper object.
        """
        result = productstatus.core.lookup.lookup_name('This is a test')
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], productstatus.core.models.Product)
        self.assertEqual(str(result[0].id), '7d3fe736-5902-44d5-a34c-86f877190523')

    def test_lookup_url(self):
        """!
        @brief Test that querying for a string that contains a url returns the proper object.
        """
        result = productstatus.core.lookup.lookup_url('test.nc')
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], productstatus.core.models.DataInstance)
        self.assertIsInstance(result[1], productstatus.core.models.DataInstance)
        self.assertEqual(str(result[0].id), '8e52633f-04bc-40d5-99e1-6b1c9b9010f4')
        self.assertEqual(str(result[1].id), 'ae443952-7990-4cee-9913-41dfd0092dc1')
