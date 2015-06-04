# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0023_auto_20150409_1310'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='keypair_door',
            name='door',
        ),
        migrations.RemoveField(
            model_name='keypair_door',
            name='keypair',
        ),
        migrations.DeleteModel(
            name='Keypair_Door',
        ),
        migrations.RemoveField(
            model_name='door',
            name='serial',
        ),
        migrations.AddField(
            model_name='keypair',
            name='doors',
            field=models.ManyToManyField(to='records.Door'),
            preserve_default=True,
        ),
    ]
