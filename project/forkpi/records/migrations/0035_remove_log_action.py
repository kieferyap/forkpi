# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0034_log_was_allowed'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='log',
            name='action',
        ),
    ]
