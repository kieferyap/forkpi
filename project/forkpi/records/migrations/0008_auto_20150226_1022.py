# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0007_auto_20150225_0936'),
    ]

    operations = [
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_on', models.DateTimeField(default=datetime.datetime.now, auto_now_add=True)),
                ('action', models.TextField(default=b'')),
                ('details', models.TextField(default=b'')),
                ('pin', models.TextField(default=b'')),
                ('rfid_uid', models.CharField(default=b'', max_length=8)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RenameModel(
            old_name='Kiefers',
            new_name='Keypair',
        ),
        migrations.RenameModel(
            old_name='Users',
            new_name='User',
        ),
        migrations.DeleteModel(
            name='Logs',
        ),
    ]
