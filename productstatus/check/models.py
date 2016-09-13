"""!
@brief Check definition models for Productstatus products.

This module provides a framework where an administrator can provide an
authoritative answer of what constitutes a working dataset.
"""


from django.db import models

import django.core.validators

import uuid
import datetime

import productstatus
import productstatus.check
import productstatus.core.models


class Check(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(unique=True, max_length=255)
    product = models.ForeignKey(productstatus.core.models.Product)

    def execute(self):
        """!
        @brief Run a check and return its results as a CheckResult object.
        """
        result = productstatus.check.CheckResult()
        [result.add_part(x.execute()) for x in self.checks()]
        return result

    def checks(self):
        c = []
        for check in self._meta.related_objects:
            c += list(getattr(self, check.get_accessor_name()).all())
        return c

    def __str__(self):
        return self.name


class CheckCondition(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    check_id = models.ForeignKey(Check)

    class Meta:
        abstract = True

    def execute(self):
        """!
        @brief Return a check condition result.
        @returns productstatus.check.CheckResultPart
        """
        result = productstatus.check.CheckResultPart()
        self.run_check(result)
        return result

    def run_check(self, result):
        """!
        @brief Populate a check condition result with check data.
        """
        raise NotImplementedError('Please implement the "run_check" function in your CheckCondition subclass.')


class CheckConditionDataInstance(CheckCondition):
    service_backend = models.ForeignKey(productstatus.core.models.ServiceBackend, help_text='Required ServiceBackend')
    format = models.ForeignKey(productstatus.core.models.DataFormat, help_text='Required DataFormat')
    count = models.IntegerField('Required number of DataInstance objects', default=1)
    grace_time = models.IntegerField('Pass test on less than required number of DataInstance objects for this many minutes, counted from reference time', default=0)
    terms = models.CharField('Which terms to run this check for, as comma-separated integers',
                             validators=[django.core.validators.validate_comma_separated_integer_list],
                             max_length=255,
                             null=True,
                             blank=True)

    def terms_list(self):
        """!
        @brief Return a list of integers, defined in the terms field
        """
        if not self.terms:
            return []
        return [int(x.strip()) for x in self.terms.split(',')]

    def reference_time_in_terms(self, reference_time):
        """!
        @brief Return True if reference time hour exists in the terms field, or
        if the terms field is empty. Returns False otherwise.
        """
        if not self.terms:
            return True
        return reference_time.hour in self.terms_list()

    def run_check(self, result):
        """!
        @brief Check that a certain number of DataInstances exists on the
        latest ProductInstance, with matching ServiceBackend and DataFormat.
        """
        product_instance = self.check_id.product.latest_product_instance()
        if not product_instance:
            return result.critical('No product instances found for product %s' % self.check_id.product.name)
        base_text = '%s %s files on %s' % (self.check_id.product.name, self.format.name, self.service_backend.name)
        if not self.reference_time_in_terms(product_instance.reference_time):
            return result.ok('%s: skipping subcheck only defined for term %02d' % (base_text, product_instance.reference_time.hour))
        time_delta = datetime.timedelta(minutes=self.grace_time)
        now = productstatus.now_with_timezone()
        remaining = (product_instance.reference_time + time_delta) - now
        remaining_seconds = remaining.total_seconds()
        data_instance_count = product_instance.data_instances_with_data_format_on_service_backend(self.format, self.service_backend).count()
        data_instance_delta = self.count - data_instance_count
        if data_instance_delta != 0:
            if data_instance_delta > 0:
                text = '%d data instances missing' % data_instance_delta
            else:
                text = '%d extraneous data instances' % -data_instance_delta
            if remaining_seconds > 0:
                return result.ok('%s: %s, but still %s remaining to fulfill requirements' % (base_text, text, str(remaining)))
            return result.critical('%s: %s' % (base_text, text))
        return result.ok('%s: %d data instances, just as expected' % (base_text, data_instance_count))

    def __str__(self):
        return 'Check that %d instances of data format %s exists on %s' % (self.count, self.format, self.service_backend)


class CheckConditionAge(CheckCondition):
    maximum_age = models.IntegerField("Maximum age of the current reference time, in minutes")

    def run_check(self, result):
        """!
        @brief Check that the latest ProductInstance's reference time is more
        recent than the specified threshold.
        """
        product_instance = self.check_id.product.latest_product_instance()
        if not product_instance:
            result.critical('No product instances found for product %s' % self.check_id.product.name)
            return
        time_delta = datetime.timedelta(minutes=self.maximum_age)
        now = productstatus.now_with_timezone()
        remaining = (product_instance.reference_time + time_delta) - now
        remaining_seconds = remaining.total_seconds()
        if remaining_seconds > 0:
            result.ok('%s latest reference time is %s, still valid for %s' % (self.check_id.product.name, str(product_instance.reference_time), str(remaining)))
            return
        result.critical('%s latest reference time is %s, expected a new data set at least %s ago' % (self.check_id.product.name, str(product_instance.reference_time), str(-remaining)))

    def __str__(self):
        return 'Check that the current reference time is no older than %d minutes' % self.maximum_age
