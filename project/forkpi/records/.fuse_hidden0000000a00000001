from django.db.models import *
from django.contrib.auth.models import User
from datetime import datetime
# from encryption import EncryptedCharField, EncryptedTextField
# P, R, F: PR, PF, FR, R, F, PFR

class Keypair(Model):
	name = TextField(default='')
	pin = TextField(default='', null=True, blank=True)
	rfid_uid = TextField(default='', null=True, blank=True)
	fingerprint_template = TextField(default='', null=True, blank=True)
	hash_pin_rfid = TextField(default='')
	hash_pin_finger = TextField(default='')
	hash_finger_rfid = TextField(default='')
	hash_all = TextField(default='')
	hash_finger = TextField(default='')
	hash_rfid = TextField(default='')
	is_active = BooleanField(default=True)

class Log(Model):
	created_on = DateTimeField(auto_now_add=True, default=datetime.now)
	action = TextField(default='')
	details = TextField(default='', null=True, blank=True)
	pin = TextField(default='', null=True, blank=True)
	rfid_uid = TextField(default='', null=True, blank=True)
	is_fingerprint_used = BooleanField(default=False)

class Option(Model):
	name = TextField(unique=True)
	value = TextField(default='')
	default = TextField()
	flavor_text = TextField(default='')

class Door(Model):
	name = TextField(default='', unique=True)
	serial = TextField(unique=True)

class Keypair_Door(Model):
	keypair_id = ForeignKey('Keypair')
	door_id = ForeignKey('Door')