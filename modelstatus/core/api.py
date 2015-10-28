from tastypie import fields, resources

import modelstatus.core.models


class ModelResource(resources.ModelResource):
    class Meta:
        queryset = modelstatus.core.models.Model.objects.all()
        excludes = ['level', 'lft', 'rght', 'tree_id']


class ModelRunResource(resources.ModelResource):
    model = fields.ForeignKey('modelstatus.core.api.ModelResource', 'model')

    class Meta:
        queryset = modelstatus.core.models.ModelRun.objects.all()
        resource_name = 'model_run'
