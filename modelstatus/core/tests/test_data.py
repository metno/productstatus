from . import BaseTestCases
from modelstatus.core.models import Data


class DataCollectionTest(BaseTestCases.ModelstatusCollectionTest):

    def setUp(self):
        super(DataCollectionTest, self).setUp()

        self.base_url = "%s%s" % (self.url_prefix, "/data/")
        self.collection_size = 1
        self.post_data = {
            "variables": [
                "/api/v1/variable/72a56a36-0567-41f0-bcbe-5ff90c3d79ac/"
                ],
            "time_period_end": "2015-11-23T12:00:00Z",
            "time_period_begin": "2015-11-20T00:00:00Z",
            "productinstance": "/api/v1/productinstance/88d28ffd-d448-4319-a94e-16889955f94a/"
            }
        self.__model_class__ = Data

    def test_post_with_only_model_run(self):
        """
        Test that a POST request supplying only a `productinstance` resource is being accepted.
        is correct.
        """
        data = {
            "productinstance": "/api/v1/productinstance/88d28ffd-d448-4319-a94e-16889955f94a/"
        }
        response = self.api_client.post(self.base_url,
                                        format='json',
                                        data=data,
                                        authentication=self.api_key_header,
                                        )
        self.assertHttpCreated(response)


class DataItemTest(BaseTestCases.ModelstatusItemTest):

    def setUp(self):
        super(DataItemTest, self).setUp()

        self.item_uuid = "d78d50b8-5119-45fd-8195-6e5623cebd8b"
        self.base_url = "%s%s%s/" % (self.url_prefix, "/data/", self.item_uuid)
