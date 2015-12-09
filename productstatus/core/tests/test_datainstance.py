from . import BaseTestCases
from productstatus.core.models import DataInstance


class DataInstanceCollectionTest(BaseTestCases.ProductstatusCollectionTest):

    def setUp(self):
        super(DataInstanceCollectionTest, self).setUp()

        self.base_url = "%s%s" % (self.url_prefix, "/datainstance/")
        self.collection_size = 2
        self.post_data = {
            "expires": "2015-12-28T09:00:00Z",
            "format": "/api/v1/dataformat/4a052f4e-61b8-4a10-9235-11f2dbb31bcc/",
            "url": "https://datastore1.example.com/file2.nc",
            "servicebackend": "/api/v1/servicebackend/495bb3be-e327-4840-accf-afefcd411e06/",
            "data": "/api/v1/data/434405fa-b3ca-42b1-b764-959d06370b32/"
            }
        self.__model_class__ = DataInstance


class DataInstanceItemTest(BaseTestCases.ProductstatusItemTest):

    def setUp(self):
        super(DataInstanceItemTest, self).setUp()

        self.item_uuid = "ae443952-7990-4cee-9913-41dfd0092dc1"
        self.base_url = "%s%s%s/" % (self.url_prefix, "/datainstance/", self.item_uuid)
