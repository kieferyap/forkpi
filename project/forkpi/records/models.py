from django.db.models import *
from django.contrib.auth.models import User
from datetime import datetime

class Keypair(Model):
	name = TextField(default='')
	pin = TextField(default='', null=True, blank=True)
	rfid_uid = CharField(max_length=8)
	is_active = BooleanField(default=True)

class Log(Model):
	created_on = DateTimeField(auto_now_add=True, default=datetime.now)
	action = TextField(default='')
	details = TextField(default='', null=True, blank=True)
	pin = TextField(default='', null=True, blank=True)
	rfid_uid = CharField(max_length=8, default='')

class Option(Model):
	name = TextField(unique=True)
	value = TextField(default='')