# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_product_file_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='datainstance',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
    ]
