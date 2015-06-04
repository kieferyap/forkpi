# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0021_log_is_fingerprint_used'),
    ]

    operations = [
        migrations.RenameField(
            model_name='keypair',
            old_name='hash_all',
            new_name='hash_pin',
        ),
        migrations.RemoveField(
            model_name='keypair',
            name='hash_finger',
        ),
        migrations.RemoveField(
            model_name='keypair',
            name='hash_finger_rfid',
        ),
        migrations.RemoveField(
            model_name='keypair',
            name='hash_pin_finger',
        ),
        migrations.RemoveField(
            model_name='keypair',
            name='hash_pin_rfid',
        ),
    ]
