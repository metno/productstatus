# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_datainstance_partial'),
    ]

    operations = [
        migrations.AddField(
            model_name='datainstance',
            name='hash',
            field=models.CharField(max_length=512, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='datainstance',
            name='hash_type',
            field=models.CharField(max_length=32, null=True, blank=True),
        ),
    ]
