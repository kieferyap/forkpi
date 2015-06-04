# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0018_option_default'),
    ]

    operations = [
        migrations.AddField(
            model_name='option',
            name='flavor_text',
            field=models.TextField(default=''),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='keypair',
            name='name',
            field=models.TextField(default=''),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='keypair',
            name='pin',
            field=models.TextField(default='', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='keypair',
            name='rfid_uid',
            field=models.TextField(default='', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='log',
            name='action',
            field=models.TextField(default=''),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='log',
            name='details',
            field=models.TextField(default='', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='log',
            name='pin',
            field=models.TextField(default='', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='log',
            name='rfid_uid',
            field=models.TextField(default='', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='option',
            name='value',
            field=models.TextField(default=''),
            preserve_default=True,
        ),
    ]
