# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0004_auto_20150219_0729'),
    ]

    operations = [
        migrations.RenameField(
            model_name='kiefers',
            old_name='is_actives',
            new_name='is_active',
        ),
    ]
