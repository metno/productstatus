import django.test

import productstatus.core.expired


class ExpiredTest(django.test.TestCase):
    """!
    Tests for expired datainstance lookups.
    """

    fixtures = ['core.json']

    def setUp(self):
        pass

    def test_expired(self):
        """!
        @brief Test that the correct expired DataInstance resources are returned.
        """
        table = [
            ('530d166a-ace9-46d5-b817-9168ca5946b1',
            '495bb3be-e327-4840-accf-afefcd411e06',
            ['bf6893b6-7963-4b61-9149-5a0a67ecd78e'],),
            ('7d3fe736-5902-44d5-a34c-86f877190523',
            '495bb3be-e327-4840-accf-afefcd411e06',
            ['ae443952-7990-4cee-9913-41dfd0092dc1'],),
        ]
        expired = productstatus.core.expired.get_expired_datainstances()
        self.assertEqual(len(expired), 2)
        for i, item in enumerate(expired):
            product, servicebackend, instances = item
            ids = [str(instance.id) for instance in instances]
            self.assertEqual(str(product.id), table[i][0])
            self.assertEqual(str(servicebackend.id), table[i][1])
            self.assertEqual(ids, table[i][2])
