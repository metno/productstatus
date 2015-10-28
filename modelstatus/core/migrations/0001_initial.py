# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Data',
            fields=[
                ('uri', models.CharField(max_length=1024, serialize=False, primary_key=True)),
                ('time_period_begin', models.DateTimeField()),
                ('time_period_end', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='DataFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.CharField(max_length=1024)),
                ('expires', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='DataFormat',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Institution',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Model',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('grid_resolution', models.DecimalField(max_digits=10, decimal_places=5)),
                ('grid_resolution_unit', models.CharField(max_length=16, choices=[(b'm', b'meters'), (b'deg', b'degrees')])),
                ('prognosis_length', models.IntegerField()),
                ('time_steps', models.IntegerField()),
                ('bounding_box', models.CharField(max_length=255)),
                ('wdb_data_provider', models.CharField(unique=True, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='ModelRun',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('reference_time', models.DateTimeField()),
                ('version', models.IntegerField()),
                ('model', models.ForeignKey(to='core.Model')),
            ],
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(unique=True, max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name='Projection',
            fields=[
                ('id', models.CharField(max_length=255, serialize=False, primary_key=True)),
                ('definition', models.CharField(unique=True, max_length=1024)),
            ],
        ),
        migrations.CreateModel(
            name='ServiceBackend',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('documentation_url', models.URLField(max_length=1024)),
            ],
        ),
        migrations.CreateModel(
            name='Variable',
            fields=[
                ('name', models.CharField(max_length=255, serialize=False, primary_key=True)),
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
            name='projection',
            field=models.ForeignKey(to='core.Projection'),
        ),
        migrations.AddField(
            model_name='datafile',
            name='format',
            field=models.ForeignKey(to='core.DataFormat'),
        ),
        migrations.AddField(
            model_name='datafile',
            name='service_backend',
            field=models.ForeignKey(to='core.ServiceBackend'),
        ),
        migrations.AddField(
            model_name='datafile',
            name='uri',
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
            field=models.ManyToManyField(to='core.Variable'),
        ),
        migrations.AlterUniqueTogether(
            name='modelrun',
            unique_together=set([('reference_time', 'model', 'version')]),
        ),
    ]
