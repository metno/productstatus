# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Data',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('time_period_begin', models.DateTimeField(null=True, blank=True)),
                ('time_period_end', models.DateTimeField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='DataFormat',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='DataInstance',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('url', models.CharField(max_length=1024)),
                ('expires', models.DateTimeField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('data', models.ForeignKey(to='core.Data')),
                ('format', models.ForeignKey(to='core.DataFormat')),
            ],
        ),
        migrations.CreateModel(
            name='Institution',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='License',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('description', models.CharField(max_length=1024, null=True, blank=True)),
                ('url', models.URLField(max_length=1024, null=True, blank=True)),
                ('public', models.BooleanField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(unique=True, max_length=254)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('grid_resolution', models.DecimalField(null=True, max_digits=10, decimal_places=5, blank=True)),
                ('grid_resolution_unit', models.CharField(blank=True, max_length=16, null=True, choices=[(b'm', b'meters'), (b'deg', b'degrees')])),
                ('prognosis_length', models.IntegerField(null=True, blank=True)),
                ('time_steps', models.IntegerField(null=True, blank=True)),
                ('bounding_box', models.CharField(max_length=255, null=True, blank=True)),
                ('wdb_data_provider', models.CharField(max_length=255, null=True, blank=True)),
                ('ecmwf_stream_name', models.CharField(max_length=255, null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('contact', models.ForeignKey(to='core.Person')),
                ('institution', models.ForeignKey(to='core.Institution')),
                ('license', models.ForeignKey(to='core.License')),
                ('parents', models.ManyToManyField(related_name='children', to='core.Product')),
            ],
        ),
        migrations.CreateModel(
            name='ProductInstance',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('state', models.IntegerField(choices=[(0, b'incomplete'), (1, b'complete'), (2, b'error')])),
                ('reference_time', models.DateTimeField()),
                ('version', models.IntegerField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('product', models.ForeignKey(to='core.Product')),
            ],
        ),
        migrations.CreateModel(
            name='Projection',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('definition', models.CharField(unique=True, max_length=1024)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='ServiceBackend',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('documentation_url', models.URLField(max_length=1024)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Variable',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='projection',
            field=models.ForeignKey(blank=True, to='core.Projection', null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='variables',
            field=models.ManyToManyField(to='core.Variable', blank=True),
        ),
        migrations.AddField(
            model_name='datainstance',
            name='service_backend',
            field=models.ForeignKey(to='core.ServiceBackend'),
        ),
        migrations.AddField(
            model_name='data',
            name='product_instance',
            field=models.ForeignKey(to='core.ProductInstance'),
        ),
        migrations.AddField(
            model_name='data',
            name='variables',
            field=models.ManyToManyField(to='core.Variable', blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='productinstance',
            unique_together=set([('reference_time', 'product', 'version')]),
        ),
    ]
