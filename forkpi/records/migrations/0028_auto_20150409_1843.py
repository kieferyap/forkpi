# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0027_auto_20150409_1709'),
    ]

    operations = [
        migrations.RenameField(
            model_name='log',
            old_name='is_fingerprint_used',
            new_name='used_fingerprint',
        ),
    ]
