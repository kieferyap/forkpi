# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0020_auto_20150402_2156'),
    ]

    operations = [
        migrations.AddField(
            model_name='log',
            name='is_fingerprint_used',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
