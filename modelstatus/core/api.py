from tastypie import fields, resources, authentication, authorization, serializers

import dateutil.tz

import modelstatus.core.models


class Serializer(serializers.Serializer):
    formats = ['json']

    def format_datetime(self, data):
        """
        Strange behavior: unless this method is overridden, Tastypie will
        return a naive datetime object. (???)
        """
        return data.astimezone(tz=dateutil.tz.tzutc())


class BaseResource(resources.ModelResource):
    """
    All resource classes should inherit this base class, which ensures that the
    `id` property can never be set manually.
    """

    def hydrate(self, bundle):
        """
        Only copy the supplied ID into the destination object if it already
        exists in the database. Otherwise, use an auto-generated UUID.
        """
        if 'id' in bundle.data:
            bundle.data['id'] = bundle.obj.id
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
    serializer = Serializer()


class ProductResource(BaseResource):
    parents = fields.ManyToManyField('modelstatus.core.api.ProductResource', 'parents', null=True)
    projection = fields.ForeignKey('modelstatus.core.api.ProjectionResource', 'projection', null=True)
    contact = fields.ForeignKey('modelstatus.core.api.PersonResource', 'contact')
    institution = fields.ForeignKey('modelstatus.core.api.InstitutionResource', 'institution')
    license = fields.ForeignKey('modelstatus.core.api.LicenseResource', 'license')

    class Meta(BaseMeta):
        queryset = modelstatus.core.models.Product.objects.all()
        filtering = {
            'name': ['exact'],
            'wdb_data_provider': ['exact'],
            'grib_center': ['exact'],
            'grib_generating_process_id': ['exact'],
            'lft': resources.ALL,
            'rght': resources.ALL,
        }


class ProductInstanceResource(BaseResource):
    product = fields.ForeignKey('modelstatus.core.api.ProductResource', 'product')
    version = fields.IntegerField(attribute='version', readonly=True)

    class Meta(BaseMeta):
        queryset = modelstatus.core.models.ProductInstance.objects.all()
        filtering = {
            'product': ['exact'],
            'reference_time': resources.ALL,
            'version': resources.ALL,
        }
        ordering = [
            'reference_time',
            'version',
        ]


class DataResource(BaseResource):
    productinstance = fields.ForeignKey('modelstatus.core.api.ProductInstanceResource', 'product_instance')
    variables = fields.ManyToManyField('modelstatus.core.api.VariableResource', 'variables', null=True)

    class Meta(BaseMeta):
        queryset = modelstatus.core.models.Data.objects.all()
        filtering = {
            'productinstance': ['exact'],
            'time_period_begin': resources.ALL,
            'time_period_end': resources.ALL,
        }


class DataInstanceResource(BaseResource):
    data = fields.ForeignKey('modelstatus.core.api.DataResource', 'data')
    format = fields.ForeignKey('modelstatus.core.api.DataFormatResource', 'format')
    servicebackend = fields.ForeignKey('modelstatus.core.api.ServiceBackendResource', 'service_backend')

    class Meta(BaseMeta):
        queryset = modelstatus.core.models.DataInstance.objects.all()
        filtering = {
            'data': ['exact'],
            'servicebackend': ['exact'],
            'format': ['exact'],
            'expires': resources.ALL,
            'lft': resources.ALL,
            'rght': resources.ALL,
        }


class DataFormatResource(BaseResource):
    class Meta(BaseMeta):
        queryset = modelstatus.core.models.DataFormat.objects.all()
        filtering = {
            'name': resources.ALL,
        }


class ServiceBackendResource(BaseResource):
    class Meta(BaseMeta):
        queryset = modelstatus.core.models.ServiceBackend.objects.all()


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


class LicenseResource(BaseResource):
    class Meta(BaseMeta):
        queryset = modelstatus.core.models.License.objects.all()
