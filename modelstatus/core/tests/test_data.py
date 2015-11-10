from . import BaseTestCases
from modelstatus.core.models import Data


class DataCollectionTest(BaseTestCases.ModelstatusCollectionTest):

    def setUp(self):
        super(DataCollectionTest, self).setUp()

        self.base_url = "%s%s" % (self.url_prefix, "/data/")
        self.collection_size = 2
        self.post_data = {
            "variables": [
                "/api/v1/variable/bf8515aa-188f-4d0b-a2cc-44ebd3104081/"
                ],
            "time_period_end": "2015-11-23T12:00:00Z",
            "time_period_begin": "2015-11-20T00:00:00Z",
            "model_run": "/api/v1/model_run/c491e9c8-0abd-4763-ba50-efcf6e6c2f25/"
            }
        self.__model_class__ = Data

    def test_post_with_only_model_run(self):
        """
        Test that a POST request supplying only a `model_run` resource is being accepted.
        is correct.
        """
        data = {
            "model_run": "/api/v1/model_run/c491e9c8-0abd-4763-ba50-efcf6e6c2f25/"
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
