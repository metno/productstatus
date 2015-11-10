from django.db import models

import uuid
import mptt.models


class Model(mptt.models.MPTTModel):
    """
    A unique weather model.
    """
    LENGTH_UNITS = (('m', 'meters'), ('deg', 'degrees'))

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent = mptt.models.TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)
    name = models.CharField(max_length=255, unique=True)
    grid_resolution = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True)
    grid_resolution_unit = models.CharField(max_length=16, choices=LENGTH_UNITS, null=True, blank=True)
    prognosis_length = models.IntegerField(null=True, blank=True)
    time_steps = models.IntegerField(null=True, blank=True)
    projection = models.ForeignKey('Projection', null=True, blank=True)
    bounding_box = models.CharField(max_length=255, null=True, blank=True)
    wdb_data_provider = models.CharField(max_length=255, null=True, blank=True)
    grib_center = models.CharField(max_length=255, null=True, blank=True)
    grib_generating_process_id = models.CharField(max_length=255, null=True, blank=True)
    contact = models.ForeignKey('Person')
    institution = models.ForeignKey('Institution')
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)
    # TODO: transformations - is this model derived from other models?

    def __unicode__(self):
        return self.name


class ModelRun(models.Model):
    """
    A single calculation of a weather model.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference_time = models.DateTimeField()
    model = models.ForeignKey('Model')
    version = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    def save(self, *args, **kwargs):
        """
        Ensure that the 'version' field remains untouched when saving an
        existing model run, and auto-increment that field when creating a model
        run with a reference time and model combination that already exists.
        """
        existing = ModelRun.objects.filter(id=self.id)
        if existing.count() == 1:
            self.version = existing[0].version
        else:
            qs = ModelRun.objects.filter(model=self.model,
                                         reference_time=self.reference_time,
                                         ).order_by('-version')
            if qs.count() == 0:
                self.version = 1
            else:
                self.version = qs[0].version + 1
        return super(ModelRun, self).save(*args, **kwargs)

    class Meta:
        unique_together = ('reference_time', 'model', 'version',)

    def __unicode__(self):
        return u'%(model)s at %(rtime)s version %(version)s' % {
            'model': unicode(self.model),
            'rtime': unicode(self.reference_time),
            'version': self.version,
        }


class Data(models.Model):
    """
    A set of variables for a specific time period within a single model run.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    model_run = models.ForeignKey('ModelRun')
    time_period_begin = models.DateTimeField(null=True, blank=True)
    time_period_end = models.DateTimeField(null=True, blank=True)
    variables = models.ManyToManyField('Variable', blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return u'Data from %(begin)s to %(end)s for model run %(modelrun)s' % {
            'begin': unicode(self.time_period_begin),
            'end': unicode(self.time_period_end),
            'modelrun': unicode(self.model_run),
        }


class DataFile(mptt.models.MPTTModel):
    """
    A data file or service containing specific data dictated by the Data class.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent = mptt.models.TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)
    data = models.ForeignKey('Data')
    url = models.CharField(max_length=1024)
    format = models.ForeignKey('DataFormat')
    expires = models.DateTimeField(null=True, blank=True)
    service_backend = models.ForeignKey('ServiceBackend')
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)
    # TODO: transformations

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
