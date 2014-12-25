# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0002_users_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='keypairs',
            name='id',
            field=models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True, default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='keypairs',
            name='name',
            field=models.TextField(default=''),
            preserve_default=True,
        ),
    ]
