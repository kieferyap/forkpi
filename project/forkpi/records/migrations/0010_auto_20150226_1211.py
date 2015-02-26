# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0009_auto_20150226_1043'),
    ]

    operations = [
        migrations.AlterField(
            model_name='keypair',
            name='pin',
            field=models.TextField(default=b'', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='keypair',
            name='rfid_uid',
            field=models.CharField(max_length=8),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='log',
            name='details',
            field=models.TextField(default=b'', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='log',
            name='pin',
            field=models.TextField(default=b'', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='log',
            name='rfid_uid',
            field=models.CharField(default=b'', max_length=8),
            preserve_default=True,
        ),
    ]
