from django.db.models import *
from django.contrib.auth.models import User

from datetime import datetime

class Keypair(Model):
	name = TextField(default='')
	pin = TextField(default='', null=True, blank=True)
	rfid_uid = TextField(default='', null=True, blank=True)
	fingerprint_template = TextField(default='', null=True, blank=True)
	hash_pin = TextField(default='')
	hash_rfid = TextField(default='')
	is_active = BooleanField(default=True)
	doors = ManyToManyField('Door')


class Log(Model):
	created_on = DateTimeField(auto_now_add=True, default=datetime.now)
	door = ForeignKey('Door')
	action = TextField(default='')
	details = TextField(default='', null=True, blank=True)
	pin = TextField(default='', null=True, blank=True)
	rfid_uid = TextField(default='', null=True, blank=True)
	used_fingerprint = BooleanField(default=False)

class Option(Model):
	name = TextField(unique=True)
	value = TextField(default='')
	default = TextField()
	flavor_text = TextField(default='')

class Door(Model):
	name = TextField(default='', unique=True)
	serial = TextField(unique=True)

# class Keypair_Door(Model):
# 	keypair = ForeignKey('Keypair')
# 	door = ForeignKey('Door')