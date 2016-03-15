#
# Productstatus data model
#
# Please update the image in the documentation when making changes here, see
# "Generating the data model graph" in README.md.
#

from django.db import models

import uuid


class Product(models.Model):
    """
    A unique data product created from one or more weather models.
    """
    LENGTH_UNITS = (('m', 'meters'), ('deg', 'degrees'))

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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

    def latest_product_instance(self):
        qs = self.productinstance_set.all().order_by('-reference_time', '-version')
        if qs.count() > 0:
            return qs[0]
        return None

    def __unicode__(self):
        return self.name


class ProductInstance(models.Model):
    """
    A single instance of a data product, typically having one or more data files.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey('Product')
    reference_time = models.DateTimeField()
    version = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

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
            qs = ProductInstance.objects.filter(product=self.product,
                                                reference_time=self.reference_time,
                                                ).order_by('-version')
            if qs.count() == 0:
                self.version = 1
            else:
                self.version = qs[0].version + 1
        return super(ProductInstance, self).save(*args, **kwargs)

    class Meta:
        unique_together = ('reference_time', 'product', 'version',)

    def data(self):
        return self.data_set.all().order_by('-time_period_begin', '-time_period_end')

    def __unicode__(self):
        return u'%(product)s at %(rtime)s version %(version)s' % {
            'product': unicode(self.product),
            'rtime': unicode(self.reference_time),
            'version': self.version,
        }


class Data(models.Model):
    """
    A set of variables for a specific time period within a single product instance.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product_instance = models.ForeignKey('ProductInstance')
    variables = models.ManyToManyField('Variable', blank=True)
    time_period_begin = models.DateTimeField(null=True, blank=True)
    time_period_end = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    def instances(self):
        return self.datainstance_set.all().order_by('url')

    def __unicode__(self):
        return u'Data for product instance: %(product_instance)s' % {
            'product_instance': unicode(self.product_instance),
        }


class DataInstance(models.Model):
    """
    A data file or service containing specific data dictated by the Data class.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    data = models.ForeignKey('Data')
    format = models.ForeignKey('DataFormat')
    service_backend = models.ForeignKey('ServiceBackend')
    url = models.CharField(max_length=1024)
    expires = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return u'%(url)s: %(format)s data file' % {
            'url': self.url,
            'format': unicode(self.format),
        }


class DataFormat(models.Model):
    """
    A data format, e.g. NetCDF, GRIB, web service, etc.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(unique=True, max_length=255)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return self.name


class ServiceBackend(models.Model):
    """
    A service providing a data file.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(unique=True, max_length=255)
    documentation_url = models.URLField(max_length=1024)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return self.name


class Variable(models.Model):
    """
    A standardized CF variable name.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(unique=True, max_length=255)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return self.name


class Person(models.Model):
    """
    A single human being.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return u'%(name)s <%(email)s>' % {
            'name': self.name,
            'email': self.email,
        }


class Institution(models.Model):
    """
    A single institution.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(unique=True, max_length=255)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return self.name


class Projection(models.Model):
    """
    A geographic projection, as defined by proj.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(unique=True, max_length=255)
    definition = models.CharField(unique=True, max_length=1024)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return self.name


class License(models.Model):
    """
    A data usage license.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(unique=True, max_length=255)
    description = models.CharField(max_length=1024, null=True, blank=True)
    url = models.URLField(max_length=1024, null=True, blank=True)
    public = models.BooleanField()
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return self.name
