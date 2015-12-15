# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='ecmwf_stream_name',
            new_name='source_key',
        ),
        migrations.RemoveField(
            model_name='productinstance',
            name='state',
        ),
        migrations.AddField(
            model_name='product',
            name='source',
            field=models.ForeignKey(related_name='source_for', blank=True, to='core.Institution', null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='institution',
            field=models.ForeignKey(related_name='institution_for', to='core.Institution'),
        ),
        migrations.AlterField(
            model_name='product',
            name='parents',
            field=models.ManyToManyField(related_name='children', to='core.Product', blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='product',
            unique_together=set([('source', 'source_key')]),
        ),
    ]
