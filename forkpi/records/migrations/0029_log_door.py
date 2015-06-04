# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0028_auto_20150409_1843'),
    ]

    operations = [
        migrations.AddField(
            model_name='log',
            name='door',
            field=models.ForeignKey(default=12, to='records.Door'),
            preserve_default=False,
        ),
    ]
