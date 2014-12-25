# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0003_auto_20141223_0746'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='keypairs',
            name='id',
        ),
        migrations.AddField(
            model_name='keypairs',
            name='kid',
            field=models.AutoField(default=1, serialize=False, primary_key=True),
            preserve_default=False,
        ),
    ]
