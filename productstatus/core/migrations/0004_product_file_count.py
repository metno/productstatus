# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_product_operational'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='file_count',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
