from django.db import models

import mptt.models


class Model(mptt.models.MPTTModel):
    """
    A unique weather model.
    """
    LENGTH_UNITS = (('m', 'meters'), ('deg', 'degrees'))

    parent = mptt.models.TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)
    name = models.CharField(max_length=255, unique=True)
    grid_resolution = models.DecimalField(max_digits=10, decimal_places=5)
    grid_resolution_unit = models.CharField(max_length=16, choices=LENGTH_UNITS)
    prognosis_length = models.IntegerField()
    time_steps = models.IntegerField()
    projection = models.ForeignKey('Projection')
    bounding_box = models.CharField(max_length=255)
    wdb_data_provider = models.CharField(max_length=255, unique=True)
    contact = models.ForeignKey('Person')
    institution = models.ForeignKey('Institution')
    # TODO: transformations - is this model derived from other models?

    def __unicode__(self):
        return self.name


class ModelRun(models.Model):
    """
    A single calculation of a weather model.
    """
    reference_time = models.DateTimeField()
    model = models.ForeignKey('Model')
    version = models.IntegerField()

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
    uri = models.CharField(primary_key=True, max_length=1024)
    model_run = models.ForeignKey('ModelRun')
    time_period_begin = models.DateTimeField()
    time_period_end = models.DateTimeField()
    variables = models.ManyToManyField('Variable')

    def __unicode__(self):
        return u'%(uri)s: data from %(begin)s to %(end)s for model run #%(modelrun)d' % {
            'uri': self.uri,
            'begin': unicode(self.time_period_begin),
            'end': unicode(self.time_period_end),
            'modelrun': self.model_run.id,
        }


class DataFile(mptt.models.MPTTModel):
    """
    A data file or service containing specific data dictated by the Data class.
    """
    parent = mptt.models.TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)
    uri = models.ForeignKey('Data')
    url = models.CharField(max_length=1024)
    format = models.ForeignKey('DataFormat')
    expires = models.DateTimeField()
    service_backend = models.ForeignKey('ServiceBackend')
    # TODO: transformations

    def __unicode__(self):
        return u'%(url)s: data file for %(uri)s in format %(format)s' % {
            'url': self.url,
            'uri': self.uri.uri,
            'format': unicode(self.format),
        }


class DataFormat(models.Model):
    """
    A data format, e.g. NetCDF, GRIB, web service, etc.
    """
    name = models.CharField(unique=True, max_length=255)

    def __unicode__(self):
        return self.name


class ServiceBackend(models.Model):
    """
    A service providing a data file.
    """
    name = models.CharField(unique=True, max_length=255)
    documentation_url = models.URLField(max_length=1024)

    def __unicode__(self):
        return self.name


class Variable(models.Model):
    """
    A standardized CF variable name.
    """
    name = models.CharField(primary_key=True, max_length=255)

    def __unicode__(self):
        return self.name


class Person(models.Model):
    """
    A single human being.
    """
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

    def __unicode__(self):
        return u'%(name)s <%(email)s>' % {
            'name': self.name,
            'email': self.email,
        }


class Institution(models.Model):
    """
    A single institution.
    """
    name = models.CharField(unique=True, max_length=255)

    def __unicode__(self):
        return self.name


class Projection(models.Model):
    """
    A geographic projection, as defined by proj.
    """
    id = models.CharField(primary_key=True, max_length=255)
    definition = models.CharField(unique=True, max_length=1024)

    def __unicode__(self):
        return self.id
