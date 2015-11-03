from tastypie import fields, resources, authentication, authorization

import modelstatus.core.models


class BaseMeta:
    authentication = authentication.MultiAuthentication(
        authentication.ApiKeyAuthentication(),
        authentication.Authentication(),
    )
    authorization = authorization.DjangoAuthorization()


class ModelResource(resources.ModelResource):
    parent = fields.ForeignKey('modelstatus.core.api.ModelResource', 'parent', null=True)

    class Meta(BaseMeta):
        queryset = modelstatus.core.models.Model.objects.all()
        filtering = {
            'wdb_data_provider': ['exact'],
            'lft': resources.ALL,
            'rght': resources.ALL,
        }


class ModelRunResource(resources.ModelResource):
    model = fields.ForeignKey('modelstatus.core.api.ModelResource', 'model')

    class Meta(BaseMeta):
        queryset = modelstatus.core.models.ModelRun.objects.all()
        resource_name = 'model_run'
        filtering = {
            'model': ['exact'],
            'reference_time': resources.ALL,
            'version': resources.ALL,
        }
        ordering = [
            'reference_time',
            'version',
        ]


class DataResource(resources.ModelResource):
    model_run = fields.ForeignKey('modelstatus.core.api.ModelRunResource', 'model_run')

    class Meta(BaseMeta):
        queryset = modelstatus.core.models.Data.objects.all()
        filtering = {
            'model_run': ['exact'],
            'time_period_begin': resources.ALL,
            'time_period_end': resources.ALL,
        }


class DataFileResource(resources.ModelResource):
    data = fields.ForeignKey('modelstatus.core.api.DataResource', 'data')
    format = fields.ForeignKey('modelstatus.core.api.DataFormatResource', 'format')
    service_backend = fields.ForeignKey('modelstatus.core.api.ServiceBackendResource', 'service_backend')

    class Meta(BaseMeta):
        queryset = modelstatus.core.models.DataFile.objects.all()
        resource_name = 'data_file'
        filtering = {
            'data': ['exact'],
            'service_backend': ['exact'],
            'format': ['exact'],
            'expires': resources.ALL,
            'lft': resources.ALL,
            'rght': resources.ALL,
        }


class DataFormatResource(resources.ModelResource):
    class Meta(BaseMeta):
        queryset = modelstatus.core.models.DataFormat.objects.all()
        resource_name = 'data_format'
        filtering = {
            'name': resources.ALL,
        }


class ServiceBackendResource(resources.ModelResource):
    class Meta(BaseMeta):
        queryset = modelstatus.core.models.ServiceBackend.objects.all()
        resource_name = 'service_backend'


class VariableResource(resources.ModelResource):
    class Meta(BaseMeta):
        queryset = modelstatus.core.models.Variable.objects.all()


class PersonResource(resources.ModelResource):
    class Meta(BaseMeta):
        queryset = modelstatus.core.models.Person.objects.all()


class InstitutionResource(resources.ModelResource):
    class Meta(BaseMeta):
        queryset = modelstatus.core.models.Institution.objects.all()


class ProjectionResource(resources.ModelResource):
    class Meta(BaseMeta):
        queryset = modelstatus.core.models.Projection.objects.all()
