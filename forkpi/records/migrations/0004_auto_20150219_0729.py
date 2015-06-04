# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0003_kiefers_is_active'),
    ]

    operations = [
        migrations.RenameField(
            model_name='kiefers',
            old_name='is_active',
            new_name='is_actives',
        ),
    ]
