# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0015_delete_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='keypair',
            name='rfid_uid',
            field=models.TextField(default=b'', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='log',
            name='rfid_uid',
            field=models.TextField(default=b'', null=True, blank=True),
            preserve_default=True,
        ),
    ]
