# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0008_auto_20150226_1022'),
    ]

    operations = [
        migrations.AlterField(
            model_name='keypair',
            name='rfid_uid',
            field=models.CharField(max_length=80),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='log',
            name='rfid_uid',
            field=models.CharField(default=b'', max_length=80),
            preserve_default=True,
        ),
    ]
