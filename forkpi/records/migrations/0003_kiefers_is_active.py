# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0002_remove_kiefers_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='kiefers',
            name='is_active',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
