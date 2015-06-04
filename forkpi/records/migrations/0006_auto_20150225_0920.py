# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0005_auto_20150219_0729'),
    ]

    operations = [
        migrations.AddField(
            model_name='logs',
            name='pin',
            field=models.TextField(default=b''),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='logs',
            name='rfid_uid',
            field=models.CharField(default=b'', max_length=8),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='kiefers',
            name='pin',
            field=models.TextField(),
            preserve_default=True,
        ),
    ]
