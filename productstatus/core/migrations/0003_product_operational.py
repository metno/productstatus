# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20151215_0851'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='operational',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
