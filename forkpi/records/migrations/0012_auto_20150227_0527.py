# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0011_option'),
    ]

    operations = [
        migrations.AlterField(
            model_name='option',
            name='value',
            field=models.TextField(default=b''),
            preserve_default=True,
        ),
    ]
