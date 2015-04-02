# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0019_auto_20150401_2346'),
    ]

    operations = [
        migrations.CreateModel(
            name='Door',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(default='', unique=True)),
                ('serial', models.TextField(unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Keypair_Door',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('door_id', models.ForeignKey(to='records.Door')),
                ('keypair_id', models.ForeignKey(to='records.Keypair')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='keypair',
            name='hashpass',
        ),
        migrations.AddField(
            model_name='keypair',
            name='fingerprint_template',
            field=models.TextField(default='', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='keypair',
            name='hash_all',
            field=models.TextField(default=''),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='keypair',
            name='hash_finger',
            field=models.TextField(default=''),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='keypair',
            name='hash_finger_rfid',
            field=models.TextField(default=''),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='keypair',
            name='hash_pin_finger',
            field=models.TextField(default=''),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='keypair',
            name='hash_pin_rfid',
            field=models.TextField(default=''),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='keypair',
            name='hash_rfid',
            field=models.TextField(default=''),
            preserve_default=True,
        ),
    ]
