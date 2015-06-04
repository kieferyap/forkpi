# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0033_option_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='log',
            name='was_allowed',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
