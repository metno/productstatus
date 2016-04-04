# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_datainstance_deleted'),
    ]

    operations = [
        migrations.AddField(
            model_name='datainstance',
            name='partial',
            field=models.BooleanField(default=False),
        ),
    ]
