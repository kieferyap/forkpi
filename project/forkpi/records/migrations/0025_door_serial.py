# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0024_auto_20150409_1354'),
    ]

    operations = [
        migrations.AddField(
            model_name='door',
            name='serial',
            field=models.TextField(default=123, unique=True),
            preserve_default=False,
        ),
    ]
