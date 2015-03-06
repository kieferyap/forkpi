from django.db.models import *
from django.contrib.auth.models import User
from datetime import datetime
# from encryption import EncryptedCharField, EncryptedTextField

class Keypair(Model):
	name = TextField(default='')
	pin = TextField(default='', null=True, blank=True)
	rfid_uid = TextField(default='', null=True, blank=True)
	hashpass = TextField()
	is_active = BooleanField(default=True)

class Log(Model):
	created_on = DateTimeField(auto_now_add=True, default=datetime.now)
	action = TextField(default='')
	details = TextField(default='', null=True, blank=True)
	pin = TextField(default='', null=True, blank=True)
	rfid_uid = TextField(default='', null=True, blank=True)

class Option(Model):
	name = TextField(unique=True)
	value = TextField(default='')
	default = TextField()