# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0016_auto_20150301_1819'),
    ]

    operations = [
        migrations.AddField(
            model_name='keypair',
            name='hashpass',
            field=models.TextField(default=1),
            preserve_default=False,
        ),
    ]
