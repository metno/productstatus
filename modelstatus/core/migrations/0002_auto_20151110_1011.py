# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='model',
            name='grib_center',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='model',
            name='grib_generating_process_id',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='dataformat',
            name='created',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='dataformat',
            name='modified',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='institution',
            name='created',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='institution',
            name='modified',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='model',
            name='wdb_data_provider',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='created',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='modified',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='projection',
            name='created',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='projection',
            name='modified',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='servicebackend',
            name='created',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='servicebackend',
            name='modified',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='variable',
            name='created',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='variable',
            name='modified',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
