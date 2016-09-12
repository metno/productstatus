#
# Productstatus data model
#
# Please update the image in the documentation when making changes here, see
# "Generating the data model graph" in README.md.
#

from django.db import models
from django.conf import settings

import django.db
import django.utils.text

import uuid
import json

import productstatus.core.kafkapublisher


class PendingMessage(models.Model):
    """!
    @brief This database table stores pending messages that should be sent on
    the Kafka queue.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField()

    @staticmethod
    def all_pending():
        return PendingMessage.objects.all().order_by('timestamp')

    @staticmethod
    def factory(instance):
        """!
        @brief Generate a PendingMessage object based on a BaseModel instance.
        """
        if not isinstance(instance, BaseModel):
            raise RuntimeError('PendingMessage objects can only be derived from children of BaseModel')
        p = PendingMessage()
        msg = productstatus.core.kafkapublisher.KafkaPublisher.resource_message(instance)
        p.id = uuid.UUID(msg['message_id'])
        p.message = json.dumps(msg).encode('utf-8')
        return p


class BaseModel(models.Model):
    """!
    @brief The BaseModel class provides message emitting functionality in the
    database save transaction, and URL generation.
    """

    class Meta:
        # Setting abstract to True ensures that Django will not alter the
        # database schema based on this base class.
        abstract = True

    def save(self, *args, **kwargs):
        """!
        @brief Wrap the model's save() method in a transaction that ensures
        that the record will only be saved if a message was successfully
        emitted to Kafka.
        """
        # Preserve NULL values when writing from the admin interface
        for var in vars(self):
            if not var.startswith('_'):
                if self.__dict__[var] == '':
                    self.__dict__[var] = None

        # Write data using a DB transaction
        with django.db.transaction.atomic():
            self.object_version += 1
            super(BaseModel, self).save(*args, **kwargs)
            if hasattr(self, 'deleted') and self.deleted is True:
                return
            message = PendingMessage.factory(self)
            message.save()

    def slugify(self):
        """!
        @returns an ASCII, spaceless id representation of the model instance name.
        """
        return django.utils.text.slugify(self.name)

    def resource_name(self):
        """!
        @returns The lowercase class name of the instance.
        """
        return self.__class__.__name__.lower()

    def full_url(self):
        """!
        @returns The full publicly accessible URL to this model instance's resource.
        """
        return "%s://%s%s" % (settings.PRODUCTSTATUS_PROTOCOL,
                              settings.PRODUCTSTATUS_HOST,
                              self.full_uri())

    def full_uri(self):
        """!
        @returns The URI to this model instance's resource.
        """
        return '%s/%s/%s/' % (settings.PRODUCTSTATUS_BASE_PATH,
                              self.resource_name(),
                              self.id)


class Product(BaseModel):
    """
    A unique data product created from one or more weather models.
    """
    LENGTH_UNITS = (('m', 'meters'), ('deg', 'degrees'))

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    object_version = models.IntegerField(default=0)
    slug = models.CharField(max_length=255, unique=True, default='slugify')
    parents = models.ManyToManyField('Product', related_name='children', blank=True)
    variables = models.ManyToManyField('Variable', blank=True)
    projection = models.ForeignKey('Projection', null=True, blank=True)
    contact = models.ForeignKey('Person')
    institution = models.ForeignKey('Institution', related_name='institution_for')
    license = models.ForeignKey('License')
    source = models.ForeignKey('Institution', related_name='source_for', null=True, blank=True)
    name = models.CharField(max_length=255, unique=True)
    operational = models.BooleanField()
    grid_resolution = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True)
    grid_resolution_unit = models.CharField(max_length=16, choices=LENGTH_UNITS, null=True, blank=True)
    prognosis_length = models.IntegerField(null=True, blank=True)
    time_steps = models.IntegerField(null=True, blank=True)
    bounding_box = models.CharField(max_length=255, null=True, blank=True)
    wdb_data_provider = models.CharField(max_length=255, null=True, blank=True)
    file_count = models.IntegerField(null=True, blank=True)
    source_key = models.CharField(max_length=255, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        unique_together = ('source', 'source_key',)

    def product_instances(self):
        """!
        @brief Return a QuerySet with an ordered list of ProductInstance
        objects belonging to this Product.
        """
        return self.productinstance_set.all().order_by('-reference_time', '-version')

    def latest_product_instance(self):
        """!
        @brief Return the latest ProductInstance belonging to this Product, or
        None if there are no ProductInstances found.
        """
        qs = self.product_instances()
        if qs.count() > 0:
            return qs[0]
        return None

    def __str__(self):
        return self.name


class ProductInstance(BaseModel):
    """
    A single instance of a data product, typically having one or more data files.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    object_version = models.IntegerField(default=0)
    product = models.ForeignKey('Product')
    reference_time = models.DateTimeField()
    version = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        unique_together = ('reference_time', 'product', 'version',)

    def save(self, *args, **kwargs):
        """
        Ensure that the 'version' field remains untouched when saving an
        existing product instance, and auto-increment that field when creating
        a product instance with a reference time and product combination that already exists.
        """
        existing = ProductInstance.objects.filter(id=self.id)
        if existing.count() == 1:
            self.version = existing[0].version
        elif not self.version:
            qs = self.similar().order_by('-version')
            if qs.count() == 0:
                self.version = 1
            else:
                self.version = qs[0].version + 1
        return super(ProductInstance, self).save(*args, **kwargs)

    def similar(self):
        """!
        @brief Return a QuerySet of all ProductInstance objects having the same
        reference time and Product as this ProductInstance.
        """
        return ProductInstance.objects.filter(
            product=self.product,
            reference_time=self.reference_time,
        )

    def previous(self):
        """!
        @brief Return the chronologically previous ProductInstance having the
        same reference time and Product as this ProductInstance, or None if
        there are no previous instance.
        """
        qs = ProductInstance.objects.filter(
            product=self.product,
            reference_time__lte=self.reference_time,
        )
        qs = qs.order_by('-reference_time', '-version')
        for instance in qs:
            if instance.reference_time == self.reference_time and instance.version >= self.version:
                continue
            return instance
        return None

    def next(self):
        """!
        @brief Return the chronologically next ProductInstance having the
        same reference time and Product as this ProductInstance, or None if
        there are no next instance.
        """
        qs = ProductInstance.objects.filter(
            product=self.product,
            reference_time__gte=self.reference_time,
        )
        qs = qs.order_by('reference_time', 'version')
        for instance in qs:
            if instance.reference_time == self.reference_time and instance.version <= self.version:
                continue
            return instance
        return None

    def data_instances(self):
        """!
        @brief Return a queryset of data instances that are connected to this
        ProductInstance.
        """
        return DataInstance.objects.filter(data__product_instance=self)

    def service_backends(self):
        """!
        @brief Return a queryset of service backends that has data related to
        this ProductInstance.
        """
        qs = self.data_instances()
        qs = qs.values('service_backend').distinct()
        return ServiceBackend.objects.filter(id__in=qs).order_by('name')

    def data_formats(self):
        """!
        @brief Return a queryset of data formats connected to this
        ProductInstance through a DataInstance.
        """
        qs = self.data_instances()
        qs = qs.values('format').distinct()
        return DataFormat.objects.filter(id__in=qs).order_by('name')

    def data_formats_on_service_backend(self, service_backend):
        """!
        @brief Return a queryset with data formats having the specified service
        backend and ultimately connected to this ProductInstance.
        """
        qs = self.data_instances().filter(service_backend=service_backend)
        qs = qs.values('format').distinct()
        return DataFormat.objects.filter(id__in=qs).order_by('name')

    def data_instances_with_data_format_on_service_backend(self, format, service_backend):
        """!
        @brief Return a queryset with data instances connected to this
        ProductInstance, having the specified service backend and data format.
        """
        qs = DataInstance.objects.filter(data__product_instance=self,
                                         deleted=False,
                                         service_backend=service_backend,
                                         format=format)
        qs = qs.order_by('version', 'data__time_period_begin', 'data__time_period_end')
        return qs

    def complete(self):
        """!
        @brief Return a list with a nested hash of service backends and data
        formats, with a boolean flag of whether or not all of the DataInstance
        resources belonging to this ProductInstance are present there.
        """
        list_ = {}
        backends = self.service_backends()
        formats = self.data_formats()
        for backend in backends:
            backend_uri = backend.full_uri()
            list_[backend_uri] = {}
            for format in formats:
                format_uri = format.full_uri()
                list_[backend_uri][format_uri] = {}
                instances = self.data_instances_with_data_format_on_service_backend(
                    format,
                    backend,
                )
                file_count = instances.count()
                is_complete = (self.product.file_count == file_count)
                list_[backend_uri][format_uri]['file_count'] = is_complete
        return list_

    def data(self):
        return self.data_set.all().order_by('time_period_begin', 'time_period_end')

    def __str__(self):
        return u'%(product)s at %(rtime)s version %(version)s' % {
            'product': str(self.product),
            'rtime': str(self.reference_time),
            'version': self.version,
        }


class Data(BaseModel):
    """
    A set of variables for a specific time period within a single product instance.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    object_version = models.IntegerField(default=0)
    product_instance = models.ForeignKey('ProductInstance')
    variables = models.ManyToManyField('Variable', blank=True)
    time_period_begin = models.DateTimeField(null=True, blank=True)
    time_period_end = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        unique_together = ('time_period_begin', 'time_period_end', 'product_instance')

    def instances(self):
        return self.datainstance_set.all().order_by('url')

    def __str__(self):
        return u'Data for product instance: %(product_instance)s' % {
            'product_instance': str(self.product_instance),
        }


class DataInstance(BaseModel):
    """
    A data file or service containing specific data dictated by the Data class.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    object_version = models.IntegerField(default=0)
    data = models.ForeignKey('Data')
    format = models.ForeignKey('DataFormat')
    service_backend = models.ForeignKey('ServiceBackend')
    # the `partial` field denotes whether or not this data instance is a data
    # segment in a file which also contains more data.
    partial = models.BooleanField(default=False)
    url = models.CharField(max_length=1024)
    hash_type = models.CharField(max_length=32, null=True, blank=True)
    hash = models.CharField(max_length=512, null=True, blank=True)
    expires = models.DateTimeField(null=True, blank=True)
    deleted = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return u'%(url)s: %(format)s data file' % {
            'url': self.url,
            'format': str(self.format),
        }


class DataFormat(BaseModel):
    """
    A data format, e.g. NetCDF, GRIB, web service, etc.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    object_version = models.IntegerField(default=0)
    slug = models.CharField(max_length=255, unique=True, default='slugify')
    name = models.CharField(unique=True, max_length=255)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return self.name


class ServiceBackend(BaseModel):
    """
    A service providing a data file.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    object_version = models.IntegerField(default=0)
    slug = models.CharField(max_length=255, unique=True, default='slugify')
    name = models.CharField(unique=True, max_length=255)
    documentation_url = models.URLField(max_length=1024)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return self.name


class Variable(BaseModel):
    """
    A standardized CF variable name.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    object_version = models.IntegerField(default=0)
    slug = models.CharField(max_length=255, unique=True, default='slugify')
    name = models.CharField(unique=True, max_length=255)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return self.name


class Person(BaseModel):
    """
    A single human being.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    object_version = models.IntegerField(default=0)
    slug = models.CharField(max_length=255, unique=True, default='slugify')
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return u'%(name)s <%(email)s>' % {
            'name': self.name,
            'email': self.email,
        }


class Institution(BaseModel):
    """
    A single institution.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    object_version = models.IntegerField(default=0)
    slug = models.CharField(max_length=255, unique=True, default='slugify')
    name = models.CharField(unique=True, max_length=255)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return self.name


class Projection(BaseModel):
    """
    A geographic projection, as defined by proj.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    object_version = models.IntegerField(default=0)
    slug = models.CharField(max_length=255, unique=True, default='slugify')
    name = models.CharField(unique=True, max_length=255)
    definition = models.CharField(unique=True, max_length=1024)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return self.name


class License(BaseModel):
    """
    A data usage license.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    object_version = models.IntegerField(default=0)
    slug = models.CharField(max_length=255, unique=True, default='slugify')
    name = models.CharField(unique=True, max_length=255)
    description = models.CharField(max_length=1024, null=True, blank=True)
    url = models.URLField(max_length=1024, null=True, blank=True)
    public = models.BooleanField()
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return self.name
