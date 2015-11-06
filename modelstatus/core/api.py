from tastypie import fields, resources, authentication, authorization

import modelstatus.core.models


class BaseResource(resources.ModelResource):
    """
    All resource classes should inherit this base class, which ensures that the
    `id` property can never be set manually.
    """

    id = fields.CharField(attribute='id', unique=True, readonly=True)

    def hydrate(self, bundle):
        if 'id' in bundle.data:
            bundle.obj.id = bundle.data['id']
        return bundle


class BaseMeta:
    """
    Use the same authentication and authorization mechanism on all resources.
    """
    authentication = authentication.MultiAuthentication(
        authentication.ApiKeyAuthentication(),
        authentication.Authentication(),
    )
    authorization = authorization.DjangoAuthorization()


class ModelResource(BaseResource):
    parent = fields.ForeignKey('modelstatus.core.api.ModelResource', 'parent', null=True)
    projection = fields.ForeignKey('modelstatus.core.api.ProjectionResource', 'projection')
    contact = fields.ForeignKey('modelstatus.core.api.PersonResource', 'contact')
    institution = fields.ForeignKey('modelstatus.core.api.InstitutionResource', 'institution')

    class Meta(BaseMeta):
        queryset = modelstatus.core.models.Model.objects.all()
        filtering = {
            'wdb_data_provider': ['exact'],
            'lft': resources.ALL,
            'rght': resources.ALL,
        }


class ModelRunResource(BaseResource):
    model = fields.ForeignKey('modelstatus.core.api.ModelResource', 'model')
    version = fields.IntegerField(attribute='version', readonly=True)

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


class DataResource(BaseResource):
    model_run = fields.ForeignKey('modelstatus.core.api.ModelRunResource', 'model_run')
    variables = fields.ManyToManyField('modelstatus.core.api.VariableResource', 'variables', null=True)

    class Meta(BaseMeta):
        queryset = modelstatus.core.models.Data.objects.all()
        filtering = {
            'model_run': ['exact'],
            'time_period_begin': resources.ALL,
            'time_period_end': resources.ALL,
        }


class DataFileResource(BaseResource):
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


class DataFormatResource(BaseResource):
    class Meta(BaseMeta):
        queryset = modelstatus.core.models.DataFormat.objects.all()
        resource_name = 'data_format'
        filtering = {
            'name': resources.ALL,
        }


class ServiceBackendResource(BaseResource):
    class Meta(BaseMeta):
        queryset = modelstatus.core.models.ServiceBackend.objects.all()
        resource_name = 'service_backend'


class VariableResource(BaseResource):
    class Meta(BaseMeta):
        queryset = modelstatus.core.models.Variable.objects.all()


class PersonResource(BaseResource):
    class Meta(BaseMeta):
        queryset = modelstatus.core.models.Person.objects.all()


class InstitutionResource(BaseResource):
    class Meta(BaseMeta):
        queryset = modelstatus.core.models.Institution.objects.all()


class ProjectionResource(BaseResource):
    class Meta(BaseMeta):
        queryset = modelstatus.core.models.Projection.objects.all()
