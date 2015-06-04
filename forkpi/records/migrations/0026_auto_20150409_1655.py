# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0025_door_serial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='keypair',
            name='fingerprint_template',
        ),
        migrations.AddField(
            model_name='keypair',
            name='_fingerprint_template',
            field=models.TextField(default='', null=True, db_column='fingerprint_template', blank=True),
            preserve_default=True,
        ),
    ]
