from tastypie import fields, resources, authentication, authorization, serializers
from django.conf import settings

import dateutil.tz
import tastypie.exceptions

import productstatus.core.models


class DjangoAuthorization(authorization.DjangoAuthorization):
    """
    Authorizes every authenticated user to perform GET, for all others
    performs DjangoAuthorization.
    """

    def read_detail(self, object_list, bundle):
        if bundle.request.method == 'GET':
            return True
        return super(DjangoAuthorization, self).read_detail(object_list, bundle)

    def read_list(self, object_list, bundle):
        if bundle.request.method == 'GET':
            return object_list
        return super(DjangoAuthorization, self).read_list(object_list, bundle)


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
    All resource classes should inherit this base class.
    """
    pass


class BaseMeta:
    """
    Use the same authentication and authorization mechanism on all resources.
    """
    authentication = authentication.MultiAuthentication(
        authentication.ApiKeyAuthentication(),
        authentication.Authentication(),
    )
    authorization = DjangoAuthorization()
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
            'id': resources.ALL,
            'parents': resources.ALL,
            'name': ['exact'],
            'slug': ['exact'],
            'wdb_data_provider': ['exact'],
            'source': resources.ALL_WITH_RELATIONS,
            'source_key': ['exact'],
        }


class ProductInstanceResource(BaseResource):
    product = fields.ForeignKey('productstatus.core.api.ProductResource', 'product')
    version = fields.IntegerField(attribute='version')
    complete = fields.DictField(readonly=True, attribute='complete')

    class Meta(BaseMeta):
        queryset = productstatus.core.models.ProductInstance.objects.all()
        filtering = {
            'id': resources.ALL,
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
            'id': resources.ALL,
            'productinstance': resources.ALL_WITH_RELATIONS,
            'time_period_begin': resources.ALL_WITH_RELATIONS,
            'time_period_end': resources.ALL_WITH_RELATIONS,
        }


class DataInstanceResource(BaseResource):
    data = fields.ForeignKey('productstatus.core.api.DataResource', 'data')
    format = fields.ForeignKey('productstatus.core.api.DataFormatResource', 'format')
    servicebackend = fields.ForeignKey('productstatus.core.api.ServiceBackendResource', 'service_backend')

    class Meta(BaseMeta):
        queryset = productstatus.core.models.DataInstance.objects.all()
        filtering = {
            'id': resources.ALL,
            'data': resources.ALL_WITH_RELATIONS,
            'servicebackend': resources.ALL_WITH_RELATIONS,
            'format': resources.ALL_WITH_RELATIONS,
            'expires': resources.ALL,
            'deleted': resources.ALL,
            'url': resources.ALL,
            'partial': resources.ALL,
        }
        ordering = [
            'created',
            'modified',
            'expires',
            'partial',
        ]


class DataFormatResource(BaseResource):
    class Meta(BaseMeta):
        queryset = productstatus.core.models.DataFormat.objects.all()
        filtering = {
            'id': resources.ALL,
            'name': resources.ALL,
            'slug': resources.ALL,
        }


class ServiceBackendResource(BaseResource):
    class Meta(BaseMeta):
        queryset = productstatus.core.models.ServiceBackend.objects.all()
        filtering = {
            'id': resources.ALL,
            'name': resources.ALL,
            'slug': resources.ALL,
        }


class VariableResource(BaseResource):
    class Meta(BaseMeta):
        queryset = productstatus.core.models.Variable.objects.all()
        filtering = {
            'id': resources.ALL,
            'name': resources.ALL,
            'slug': resources.ALL,
        }


class PersonResource(BaseResource):
    class Meta(BaseMeta):
        queryset = productstatus.core.models.Person.objects.all()
        filtering = {
            'id': resources.ALL,
            'name': resources.ALL,
            'slug': resources.ALL,
        }


class InstitutionResource(BaseResource):
    class Meta(BaseMeta):
        queryset = productstatus.core.models.Institution.objects.all()
        filtering = {
            'id': resources.ALL,
            'name': resources.ALL,
            'slug': resources.ALL,
        }


class ProjectionResource(BaseResource):
    class Meta(BaseMeta):
        queryset = productstatus.core.models.Projection.objects.all()
        filtering = {
            'id': resources.ALL,
            'name': resources.ALL,
            'slug': resources.ALL,
        }


class LicenseResource(BaseResource):
    class Meta(BaseMeta):
        queryset = productstatus.core.models.License.objects.all()
        filtering = {
            'id': resources.ALL,
            'name': resources.ALL,
            'slug': resources.ALL,
        }


class KafkaConfiguration(object):
    def __init__(self, initial=None):
        self.__dict__['_data'] = {}

        if hasattr(initial, 'items'):
            self.__dict__['_data'] = initial

    def __getattr__(self, name):
        return self._data.get(name, None)

    def __setattr__(self, name, value):
        self.__dict__['_data'][name] = value

    def to_dict(self):
        return self._data


class KafkaObject(object):
    """!
    @brief A representation of Kafka broker settings.
    """
    id = settings.KAFKA_SINGLETON_PK
    topic = settings.KAFKA_TOPIC
    brokers = settings.KAFKA_BROKERS
    ssl = settings.KAFKA_SSL
    ssl_verify = settings.KAFKA_SSL_VERIFY


class KafkaResource(resources.Resource):
    """!
    @brief A read-only, singleton resource that will return connection details
    to this Productstatus server's Kafka brokers and topic.
    """
    id = fields.CharField(attribute='id', readonly=True)
    brokers = fields.ListField(attribute='brokers', readonly=True)
    topic = fields.CharField(attribute='topic', readonly=True)
    ssl = fields.BooleanField(attribute='ssl', readonly=True)
    ssl_verify = fields.BooleanField(attribute='ssl_verify', readonly=True)

    class Meta:
        allowed_methods = ['get']
        resource_name = 'kafka'
        object_class = KafkaConfiguration
        authentication = authentication.Authentication()
        serializer = Serializer()

    def detail_uri_kwargs(self, bundle_or_obj):
        return {'pk': settings.KAFKA_SINGLETON_PK}

    def get_object_list(self, *args, **kwargs):
        return [self.obj_get(pk=settings.KAFKA_SINGLETON_PK)]

    def obj_get_list(self, bundle, **kwargs):
        return self.get_object_list()

    def obj_get(self, *args, **kwargs):
        if kwargs['pk'] != settings.KAFKA_SINGLETON_PK:
            raise tastypie.exceptions.NotFound('The Kafka resource is only available as "%s"' % settings.KAFKA_SINGLETON_PK)
        return KafkaObject()

    def rollback(self, *args, **kwargs):
        pass
