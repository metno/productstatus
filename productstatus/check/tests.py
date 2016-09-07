import django.test

import productstatus.check
import productstatus.check.models


class CheckTest(django.test.TestCase):
    """!
    Tests for the check framework.
    """

    fixtures = ['core.json', 'check.json']

    def setUp(self):
        pass

    def test_simple_check(self):
        """!
        @brief Test that SimpleCheckResult works properly.
        """
        result = productstatus.check.SimpleCheckResult(productstatus.check.WARNING, 'foo')
        self.assertEqual(result.get_code(), productstatus.check.WARNING)
        self.assertEqual(result.get_message(), 'foo')

    def test_check_result_worst(self):
        """!
        @brief Test that a check's result code equals the worst severity from
        its CheckResultPart children.
        """
        check = productstatus.check.models.Check.objects.get(pk='8340969c-7f93-4527-8868-a23e3ed80d8b')
        result = productstatus.check.CheckResult()
        ok = productstatus.check.CheckResultPart()
        ok.ok('foo')
        result.add_part(ok)
        self.assertEqual(result.get_code(), productstatus.check.OK)
        critical = productstatus.check.CheckResultPart()
        critical.critical('bar')
        result.add_part(critical)
        self.assertEqual(result.get_code(), productstatus.check.CRITICAL)

    def test_check_execute(self):
        """!
        @brief Test that a check executes and gives a correct check structure back.
        """
        check = productstatus.check.models.Check.objects.get(pk='8340969c-7f93-4527-8868-a23e3ed80d8b')
        result = check.execute()
        self.assertIsInstance(result, productstatus.check.CheckResult)
        parts = result.get_parts()
        [self.assertIsInstance(x, productstatus.check.CheckResultPart) for x in parts]
        self.assertEqual(len(parts), 3)
        result.get_code()
        result.get_message()

    def test_check_data_instances(self):
        """!
        @brief Test checking for number of data instances on a specific service
        backend, according to a grace time.
        """
        check = productstatus.check.models.Check.objects.get(pk='8340969c-7f93-4527-8868-a23e3ed80d8b')
        check_part = check.checkconditiondatainstance_set.all()[0]
        product_instance = check.product.latest_product_instance()

        # check that everything is OK by default: 1 datainstance on the backend
        result = check_part.execute()
        self.assertEqual(result.code, productstatus.check.OK)

        # set required number to 2 datainstances, the check should fail
        check_part.count = 2
        result = check_part.execute()
        self.assertEqual(result.code, productstatus.check.CRITICAL)

        # increase the grace time for the check, it should succeed again
        delta = productstatus.now_with_timezone() - product_instance.reference_time
        check_part.grace_time = (delta.total_seconds() / 60) + 2
        result = check_part.execute()
        self.assertEqual(result.code, productstatus.check.OK)

        # set the grace time to just a little bit below required threshold, it should now fail
        check_part.grace_time = (delta.total_seconds() / 60) - 2
        result = check_part.execute()
        self.assertEqual(result.code, productstatus.check.CRITICAL)

    def test_check_age(self):
        """!
        @brief Test checking for reference time age.
        """
        check = productstatus.check.models.Check.objects.get(pk='8340969c-7f93-4527-8868-a23e3ed80d8b')
        check_part = check.checkconditionage_set.all()[0]
        product_instance = check.product.latest_product_instance()

        # check failure on too old reference time
        check_part.maximum_age = 0
        result = check_part.execute()
        self.assertEqual(result.code, productstatus.check.CRITICAL)

        # increase the maximum age for the check, it should succeed again
        delta = productstatus.now_with_timezone() - product_instance.reference_time
        check_part.maximum_age = (delta.total_seconds() / 60) + 2
        result = check_part.execute()
        self.assertEqual(result.code, productstatus.check.OK)
