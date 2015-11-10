# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20151110_1011'),
    ]

    operations = [
        migrations.AlterField(
            model_name='data',
            name='time_period_begin',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='data',
            name='time_period_end',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
