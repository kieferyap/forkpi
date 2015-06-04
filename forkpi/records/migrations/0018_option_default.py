# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0017_keypair_hashpass'),
    ]

    operations = [
        migrations.AddField(
            model_name='option',
            name='default',
            field=models.TextField(default=5),
            preserve_default=False,
        ),
    ]
