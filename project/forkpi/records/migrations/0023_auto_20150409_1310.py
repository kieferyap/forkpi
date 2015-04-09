# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0022_auto_20150403_1237'),
    ]

    operations = [
        migrations.RenameField(
            model_name='keypair_door',
            old_name='door_id',
            new_name='door',
        ),
        migrations.RenameField(
            model_name='keypair_door',
            old_name='keypair_id',
            new_name='keypair',
        ),
    ]
