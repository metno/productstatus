from . import BaseTestCases
from modelstatus.core.models import DataFile


class DataFileCollectionTest(BaseTestCases.ModelstatusCollectionTest):

    def setUp(self):
        super(DataFileCollectionTest, self).setUp()

        self.base_url = "%s%s" % (self.url_prefix, "/data_file/")
        self.collection_size = 2
        self.post_data = {
            "expires": "2015-12-28T09:00:00Z",
            "format": "/api/v1/data_format/d921b282-b4b1-435f-b7e8-2b58daa8a0ff/",
            "url": "https://datastore1.met.no/file2.nc",
            "service_backend": "/api/v1/service_backend/f314a536-bb96-4d2a-83cd-9764e2e3e16a/",
            "data": "/api/v1/data/d78d50b8-5119-45fd-8195-6e5623cebd8b/"
            }
        self.__model_class__ = DataFile


class DataFileItemTest(BaseTestCases.ModelstatusItemTest):

    def setUp(self):
        super(DataFileItemTest, self).setUp()

        self.item_uuid = "093c9ce8-b2d7-43eb-8c74-a84cdc6ca9e2"
        self.base_url = "%s%s%s/" % (self.url_prefix, "/data_file/", self.item_uuid)
