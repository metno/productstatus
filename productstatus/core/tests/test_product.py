from . import BaseTestCases
from productstatus.core.models import Product


class ProductCollectionTest(BaseTestCases.ProductstatusCollectionTest):

    def setUp(self):
        super(ProductCollectionTest, self).setUp()

        self.base_url = "%s%s" % (self.url_prefix, "/product/")
        self.collection_size = 1
        self.post_data = {
            "wdb_data_provider": "modelorama_indeed",
            "grid_resolution": "2500.00000",
            "name": "Modelorama",
            "grid_resolution_unit": "m",
            "time_steps": 5,
            "bounding_box": "0,0,0,0",
            "contact": "/api/v1/person/b407e09d-b0c4-4289-95fe-75a2497f6eaa/",
            "prognosis_length": 10,
            "institution": "/api/v1/institution/b3528b13-84aa-49a2-8895-77c1b3fce9d8/",
            "projection": "/api/v1/projection/d454efcc-d822-4d60-a65c-e94680953768/",
            "license": "/api/v1/license/92a5a153-53a4-4170-a0bc-cbd4ed14a05c/",
            }
        self.__model_class__ = Product


class ProductItemTest(BaseTestCases.ProductstatusItemTest):

    def setUp(self):
        super(ProductItemTest, self).setUp()

        self.item_uuid = "7d3fe736-5902-44d5-a34c-86f877190523"
        self.base_url = "%s%s%s/" % (self.url_prefix, "/product/", self.item_uuid)
