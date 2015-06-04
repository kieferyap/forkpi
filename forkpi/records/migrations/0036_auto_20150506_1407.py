# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0035_remove_log_action'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='was_allowed',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
