# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0012_auto_20150227_0527'),
    ]

    operations = [
        migrations.DeleteModel(
            name='User',
        ),
    ]
