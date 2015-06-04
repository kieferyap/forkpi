# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0032_auto_20150413_1213'),
    ]

    operations = [
        migrations.AddField(
            model_name='option',
            name='description',
            field=models.TextField(default=''),
            preserve_default=True,
        ),
    ]
