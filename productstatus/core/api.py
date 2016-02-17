from tastypie import fields, resources, authentication, authorization, serializers

import dateutil.tz

import productstatus.core.models


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
    parents = fields.ManyToManyField('productstatus.core.api.ProductResource', 'parents', null=True)
    projection = fields.ForeignKey('productstatus.core.api.ProjectionResource', 'projection', null=True)
    source = fields.ForeignKey('productstatus.core.api.InstitutionResource', 'source', null=True)
    contact = fields.ForeignKey('productstatus.core.api.PersonResource', 'contact')
    institution = fields.ForeignKey('productstatus.core.api.InstitutionResource', 'institution')
    license = fields.ForeignKey('productstatus.core.api.LicenseResource', 'license')

    class Meta(BaseMeta):
        queryset = productstatus.core.models.Product.objects.all()
        filtering = {
            'parents': resources.ALL,
            'name': ['exact'],
            'wdb_data_provider': ['exact'],
            'source': resources.ALL_WITH_RELATIONS,
            'source_key': ['exact'],
        }


class ProductInstanceResource(BaseResource):
    product = fields.ForeignKey('productstatus.core.api.ProductResource', 'product')
    version = fields.IntegerField(attribute='version')

    class Meta(BaseMeta):
        queryset = productstatus.core.models.ProductInstance.objects.all()
        filtering = {
            'product': resources.ALL_WITH_RELATIONS,
            'reference_time': resources.ALL,
            'version': resources.ALL,
        }
        ordering = [
            'reference_time',
            'version',
        ]


class DataResource(BaseResource):
    productinstance = fields.ForeignKey('productstatus.core.api.ProductInstanceResource', 'product_instance')
    variables = fields.ManyToManyField('productstatus.core.api.VariableResource', 'variables', null=True)

    class Meta(BaseMeta):
        queryset = productstatus.core.models.Data.objects.all()
        filtering = {
            'productinstance': resources.ALL_WITH_RELATIONS,
            'time_period_begin': resources.ALL,
            'time_period_end': resources.ALL,
        }


class DataInstanceResource(BaseResource):
    data = fields.ForeignKey('productstatus.core.api.DataResource', 'data')
    format = fields.ForeignKey('productstatus.core.api.DataFormatResource', 'format')
    servicebackend = fields.ForeignKey('productstatus.core.api.ServiceBackendResource', 'service_backend')

    class Meta(BaseMeta):
        queryset = productstatus.core.models.DataInstance.objects.all()
        filtering = {
            'data': resources.ALL_WITH_RELATIONS,
            'servicebackend': resources.ALL_WITH_RELATIONS,
            'format': resources.ALL_WITH_RELATIONS,
            'expires': resources.ALL,
        }
        ordering = [
            'created',
            'modified',
        ]


class DataFormatResource(BaseResource):
    class Meta(BaseMeta):
        queryset = productstatus.core.models.DataFormat.objects.all()
        filtering = {
            'name': resources.ALL,
        }


class ServiceBackendResource(BaseResource):
    class Meta(BaseMeta):
        queryset = productstatus.core.models.ServiceBackend.objects.all()


class VariableResource(BaseResource):
    class Meta(BaseMeta):
        queryset = productstatus.core.models.Variable.objects.all()


class PersonResource(BaseResource):
    class Meta(BaseMeta):
        queryset = productstatus.core.models.Person.objects.all()


class InstitutionResource(BaseResource):
    class Meta(BaseMeta):
        queryset = productstatus.core.models.Institution.objects.all()


class ProjectionResource(BaseResource):
    class Meta(BaseMeta):
        queryset = productstatus.core.models.Projection.objects.all()


class LicenseResource(BaseResource):
    class Meta(BaseMeta):
        queryset = productstatus.core.models.License.objects.all()
