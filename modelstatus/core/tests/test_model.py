from . import BaseTestCases
from modelstatus.core.models import Model


class ModelCollectionTest(BaseTestCases.ModelstatusCollectionTest):

    def setUp(self):
        super(ModelCollectionTest, self).setUp()

        self.base_url = "%s%s" % (self.url_prefix, "/model/")
        self.collection_size = 2
        self.post_data = {
            "wdb_data_provider": "modelorama_indeed",
            "grid_resolution": "2500.00000",
            "name": "Modelorama",
            "grid_resolution_unit": "m",
            "time_steps": 5,
            "bounding_box": "0,0,0,0",
            "contact": "/api/v1/person/e215b153-7d93-443e-8246-165c9b70f180/",
            "prognosis_length": 10,
            "institution": "/api/v1/institution/16f48ccc-3b9a-4c02-a03a-f836fff4b03b/",
            "projection": "/api/v1/projection/e07d64d6-66b2-4cfb-ab6b-f406d00f5600/"
            }
        self.__model_class__ = Model


class ModelItemTest(BaseTestCases.ModelstatusItemTest):

    def setUp(self):
        super(ModelItemTest, self).setUp()

        self.item_uuid = "66340f0b-2c2c-436d-a077-3d939f4f7283"
        self.base_url = "%s%s%s/" % (self.url_prefix, "/model/", self.item_uuid)
