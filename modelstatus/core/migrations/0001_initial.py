# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
import mptt.fields
import uuid


class Migration(migrations.Migration):

    replaces = [(b'core', '0001_initial'), (b'core', '0002_auto_20151028_1615'), (b'core', '0003_auto_20151028_1618'), (b'core', '0004_auto_20151028_1620')]

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Data',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('time_period_begin', models.DateTimeField()),
                ('time_period_end', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='DataFile',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('url', models.CharField(max_length=1024)),
                ('expires', models.DateTimeField()),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DataFormat',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('created', models.DateTimeField(default=datetime.datetime(2015, 10, 28, 16, 18, 23, 511871), auto_now_add=True)),
                ('modified', models.DateTimeField(default=datetime.datetime(2015, 10, 28, 16, 18, 24, 567871), auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Institution',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('created', models.DateTimeField(default=datetime.datetime(2015, 10, 28, 16, 18, 27, 15980), auto_now_add=True)),
                ('modified', models.DateTimeField(default=datetime.datetime(2015, 10, 28, 16, 18, 28, 431918), auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Model',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('grid_resolution', models.DecimalField(max_digits=10, decimal_places=5)),
                ('grid_resolution_unit', models.CharField(max_length=16, choices=[(b'm', b'meters'), (b'deg', b'degrees')])),
                ('prognosis_length', models.IntegerField()),
                ('time_steps', models.IntegerField()),
                ('bounding_box', models.CharField(max_length=255)),
                ('wdb_data_provider', models.CharField(unique=True, max_length=255)),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ModelRun',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('reference_time', models.DateTimeField()),
                ('version', models.IntegerField()),
                ('model', models.ForeignKey(to='core.Model')),
            ],
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(unique=True, max_length=254)),
                ('created', models.DateTimeField(default=datetime.datetime(2015, 10, 28, 16, 18, 34, 848035), auto_now_add=True)),
                ('modified', models.DateTimeField(default=datetime.datetime(2015, 10, 28, 16, 18, 36, 440068), auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Projection',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('definition', models.CharField(unique=True, max_length=1024)),
                ('created', models.DateTimeField(default=datetime.datetime(2015, 10, 28, 16, 18, 37, 616027), auto_now_add=True)),
                ('modified', models.DateTimeField(default=datetime.datetime(2015, 10, 28, 16, 18, 39, 96064), auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='ServiceBackend',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('documentation_url', models.URLField(max_length=1024)),
                ('created', models.DateTimeField(default=datetime.datetime(2015, 10, 28, 16, 18, 40, 104098), auto_now_add=True)),
                ('modified', models.DateTimeField(default=datetime.datetime(2015, 10, 28, 16, 18, 41, 152094), auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Variable',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('created', models.DateTimeField(default=datetime.datetime(2015, 10, 28, 16, 18, 42, 360165), auto_now_add=True)),
                ('modified', models.DateTimeField(default=datetime.datetime(2015, 10, 28, 16, 18, 43, 472129), auto_now=True)),
            ],
        ),
        migrations.AddField(
            model_name='model',
            name='contact',
            field=models.ForeignKey(to='core.Person'),
        ),
        migrations.AddField(
            model_name='model',
            name='institution',
            field=models.ForeignKey(to='core.Institution'),
        ),
        migrations.AddField(
            model_name='model',
            name='parent',
            field=mptt.fields.TreeForeignKey(related_name='children', blank=True, to='core.Model', null=True),
        ),
        migrations.AddField(
            model_name='model',
            name='projection',
            field=models.ForeignKey(blank=True, to='core.Projection', null=True),
        ),
        migrations.AddField(
            model_name='datafile',
            name='format',
            field=models.ForeignKey(to='core.DataFormat'),
        ),
        migrations.AddField(
            model_name='datafile',
            name='parent',
            field=mptt.fields.TreeForeignKey(related_name='children', blank=True, to='core.DataFile', null=True),
        ),
        migrations.AddField(
            model_name='datafile',
            name='service_backend',
            field=models.ForeignKey(to='core.ServiceBackend'),
        ),
        migrations.AddField(
            model_name='datafile',
            name='data',
            field=models.ForeignKey(to='core.Data'),
        ),
        migrations.AddField(
            model_name='data',
            name='model_run',
            field=models.ForeignKey(to='core.ModelRun'),
        ),
        migrations.AddField(
            model_name='data',
            name='variables',
            field=models.ManyToManyField(to=b'core.Variable', blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='modelrun',
            unique_together=set([('reference_time', 'model', 'version')]),
        ),
        migrations.AlterField(
            model_name='datafile',
            name='expires',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='model',
            name='bounding_box',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='model',
            name='grid_resolution',
            field=models.DecimalField(null=True, max_digits=10, decimal_places=5, blank=True),
        ),
        migrations.AlterField(
            model_name='model',
            name='grid_resolution_unit',
            field=models.CharField(blank=True, max_length=16, null=True, choices=[(b'm', b'meters'), (b'deg', b'degrees')]),
        ),
        migrations.AlterField(
            model_name='model',
            name='prognosis_length',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='model',
            name='time_steps',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='model',
            name='wdb_data_provider',
            field=models.CharField(max_length=255, unique=True, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='data',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2015, 10, 28, 16, 18, 14, 191879), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='data',
            name='modified',
            field=models.DateTimeField(default=datetime.datetime(2015, 10, 28, 16, 18, 15, 415804), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='datafile',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2015, 10, 28, 16, 18, 19, 495904), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='datafile',
            name='modified',
            field=models.DateTimeField(default=datetime.datetime(2015, 10, 28, 16, 18, 22, 279850), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='model',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2015, 10, 28, 16, 18, 30, 704007), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='model',
            name='modified',
            field=models.DateTimeField(default=datetime.datetime(2015, 10, 28, 16, 18, 31, 823996), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='modelrun',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2015, 10, 28, 16, 18, 32, 880001), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='modelrun',
            name='modified',
            field=models.DateTimeField(default=datetime.datetime(2015, 10, 28, 16, 18, 33, 864015), auto_now=True),
            preserve_default=False,
        ),
    ]
