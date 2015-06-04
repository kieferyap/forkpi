# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0006_auto_20150225_0920'),
    ]

    operations = [
        migrations.RenameField(
            model_name='logs',
            old_name='text',
            new_name='action',
        ),
        migrations.AddField(
            model_name='logs',
            name='details',
            field=models.TextField(default=b''),
            preserve_default=True,
        ),
    ]
