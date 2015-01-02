from django.db import models
from datetime import datetime

class Users(models.Model):
	userid = models.AutoField(primary_key=True)
	username = models.TextField(default='')
	email = models.TextField(default='')
	password = models.CharField(max_length=32)

class Kiefers(models.Model):
	name = models.TextField(default="")
	pin = models.CharField(max_length=4)
	rfid_uid = models.CharField(max_length=8)

class Logs(models.Model):
	created_on = models.DateTimeField(auto_now_add=True, default=datetime.now)
	text = models.TextField(default="")