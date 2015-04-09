# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0026_auto_20150409_1655'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='keypair',
            name='_fingerprint_template',
        ),
        migrations.AddField(
            model_name='keypair',
            name='fingerprint_template',
            field=models.TextField(default='', null=True, blank=True),
            preserve_default=True,
        ),
    ]
