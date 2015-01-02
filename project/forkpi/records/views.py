from django.shortcuts import render
from django.shortcuts import redirect, render, HttpResponse
from django.http import HttpResponseNotFound
from django.contrib import messages
from django.db import connection

import datetime
import hashlib
import sqlite3
from spoonpi import aes
from spoonpi.nfc_reader import NFCReader
from spoonpi import forkpi_db

import reportlab
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet

from records.models import Users, Kiefers, Logs

is_polling = False

def index(request):
	if request.session.get('userid'):
		return redirect('/keypairs')
	else:
		return redirect('/login')

####################
# Session Handling #
####################

def getLoginText(request):
	if request.session.get('userid'):
		return "Welcome back, "+request.session.get('username')
	else:
		return "You are not logged in."

def getUserActions(request):
	if request.session.get('userid'):

		userActions = {}
		userActions[0] = {}
		userActions[0]["name"] = "Logs"
		userActions[0]["url"] = "logs"
		userActions[1] = {}
		userActions[1]["name"] = "My Keypairs"
		userActions[1]["url"] = "keypairs"
		userActions[2] = {}
		userActions[2]["name"] = "Logout"
		userActions[2]["url"] = "logout"

		return userActions
	else:
		userActions = {}
		userActions[0] = {}
		userActions[0]["name"] = "Login"
		userActions[0]["url"] = "login"
		userActions[1] = {}
		userActions[1]["name"] = "Signup"
		userActions[1]["url"] = "signup"	
		return userActions
	
# Login display
def login(request):
	if request.session.get('userid'):
		messages.add_message(request, messages.ERROR, 'You have already logged in. Kindly log out first to access the login page.')
		return redirect('/keypairs')
	else:
		
		userActions = getUserActions(request)
		loginText = getLoginText(request)
		return render(request, 'login.html', {'loginText': loginText, 'userActions': userActions})

# Logging the user in
def loggingin(request):
	username = request.POST['username']
	## Encode password in MD5
	hash_object = hashlib.md5(request.POST['password'].encode('utf-8') + username)
	password_md5 = str(hash_object.hexdigest())

	## Check if user is in the database	
	try:
		user = Users.objects.get(username=username, password=password_md5)
	except Users.DoesNotExist:
		loginText = "You are not logged in."
		userActions = getUserActions(request)
		messages.add_message(request, messages.ERROR, 'I don\'t seem to recognize your username-password combination...')
		return redirect('/login')
	else:
		## Session handling
		request.session['userid'] = user.userid
		request.session['username'] = user.username

		loginText = getLoginText(request)
		userActions = getUserActions(request)

		messages.add_message(request, messages.SUCCESS, 'Awesome! Your login was successful.')
		return redirect('/keypairs')


#####################
# Signup Controller #
#####################

# Signup display
def signup(request):
	if request.session.get('userid'):
		messages.add_message(request, messages.ERROR, 'You have already logged in. Kindly log out first to access the signup page.')
		return redirect('/keypairs')
	else:
		userActions = getUserActions(request)
		loginText = getLoginText(request)
		return render(request, 'signup.html', {'loginText': loginText, 'userActions': userActions})

# Adding a user
def adduser(request):
	username = request.POST['username']
	password = request.POST['password']
	email = request.POST['email']
	## If the user didn't put in all the details...
	if(username.strip() == '' or password.strip() == '' or email.strip() == ''):
		messages.add_message(request, messages.ERROR, 'All the fields are required.')
		return redirect('/signup')

	## If the user already has an entry in the database...
	byUsername = Users.objects.all().filter(username = username)
	byEmailAdd = Users.objects.all().filter(email = email)
	if(len(byUsername) > 0 or len(byEmailAdd) > 0):
		messages.add_message(request, messages.ERROR, 'Hmm. It looks like you already have an entry in my database...')
		return redirect('/signup')

	## Not the most secure, but for our purposes, password is encoded in MD5, with salting! :D
	hash_object = hashlib.md5(password.encode('utf-8') + username)
	password_md5 = str(hash_object.hexdigest())

	## Insert user into database
	Users.objects.create(
		username = username,
		email = email,
		password = password_md5
	)

	messages.add_message(request, messages.SUCCESS, 'Congratulations! Your sign up was successful. Time to log in with those credentials!')
	return redirect('/login')


#####################
# Logout Controller #
#####################

# Logout display
def logout(request):
	try:
		del request.session['userid']
		messages.add_message(request, messages.SUCCESS, 'Logout successful.')
	except KeyError:
		messages.add_message(request, messages.ERROR, 'Logout unsuccessful. Gee, I wonder why...')

	userActions = getUserActions(request)
	loginText = getLoginText(request)

	return render(request, 'login.html', {'loginText': loginText, 'userActions': userActions})


######################
# Keypair Controller #
######################

def keypairs(request):
	if not request.session.get('userid'):
		return HttpResponseNotFound('<h1>Page not found</h1>')

	userActions = getUserActions(request)
	loginText = getLoginText(request)

	keypairs = Kiefers.objects.all()
	for keypair in keypairs:
		cipher = aes.AES(keypair.name)
		keypair.pin = cipher.decrypt(keypair.pin)
		keypair.rfid_uid = cipher.decrypt(keypair.rfid_uid)
	return render(request, 'keypairs.html',  {'loginText': loginText, 'userActions': userActions, 'keypairs': keypairs})

def addrfid(request):
	global is_polling
	if not is_polling:
		is_polling = True
		uid = NFCReader().read_tag()
		is_polling = False
		return HttpResponse(uid)
	return HttpResponse("Please try again at a later time. Sorry for the inconvenience.")

def addpair(request):
	name = request.POST['name']
	pin = request.POST['pin']
	rfid_uid = request.POST['rfid_uid']

	is_error = False

	if not (len(pin) == 0 or (len(pin) == 4 and pin.isdigit())):
		messages.add_message(request, messages.ERROR, 'PIN must be blank, or consists of 4 digits.')
		is_error = True

	if not rfid_uid:
		messages.add_message(request, messages.ERROR, 'The RFID UID must not be empty.')
		is_error = True

	if is_error:
		return redirect('/keypairs')	

	cipher = aes.AES(name)
	encrypted_pin = cipher.encrypt(pin)
	encrypted_rfid_uid = cipher.encrypt(rfid_uid)

	Kiefers.objects.create(
		name = name,
		pin = encrypted_pin,
		rfid_uid = encrypted_rfid_uid
	)
	messages.add_message(request, messages.SUCCESS, 'Pair addition successful.')
	return redirect('/keypairs')

def editname(request):
	old = Kiefers.objects.get(id = request.POST['kid'])
	old_name = old.name

	name = request.POST['value']
	Kiefers.objects.filter(id = request.POST['kid']).update(name = name)
	keypair = Kiefers.objects.get(id = request.POST['kid'])

	cipher = aes.AES(old_name)
	rfid_uid = cipher.decrypt(keypair.rfid_uid)
	pin = cipher.decrypt(keypair.pin)

	cipher = aes.AES(name)
	keypair.pin = cipher.encrypt(pin)
	keypair.rfid_uid = cipher.encrypt(rfid_uid)
		
	keypair.save()

	return HttpResponse("Successful.")

def editpin(request):
	pin = request.POST['value']

	if not (len(pin) == 0 or (len(pin) == 4 and pin.isdigit())):
		response = HttpResponse("Invalid PIN")
		messages.add_message(request, messages.ERROR, 'PIN must be blank, or consists of 4 digits.')
		response.status_code = 400
		return response

	keypair = Kiefers.objects.get(id = request.POST['kid'])
	cipher = aes.AES(keypair.name)
	keypair.pin = cipher.encrypt(pin)
		
	keypair.save()
	return HttpResponse("Successful.")

def edituid(request):
	keypair = Kiefers.objects.get(id = request.POST['kid'])
	cipher = aes.AES(keypair.name)
	keypair.rfid_uid = cipher.encrypt(request.POST['value'])
	keypair.save()
	return HttpResponse("Successful.")

def deletekeypair(request):
	Kiefers.objects.filter(id = request.POST['kid']).delete()
	return HttpResponse("Successful.")


# Attempt: print as PDF
def pdflist(request):
	# Create the HttpResponse object with the appropriate PDF headers.
	response = HttpResponse(content_type='application/pdf')
	response['Content-Disposition'] = 'attachment; filename="forkpi_keypairs.pdf"'

	doc = SimpleDocTemplate(response, pagesize=letter)
	elements = []
	styles = getSampleStyleSheet()

	keypairs = Kiefers.objects.all()

	data = []
	data.append(['Name', 'PIN', 'RFID UID'])

	for keypair in keypairs:
		data.append([Paragraph(str(keypair.name), styles['Normal']), keypair.pin, keypair.rfid_uid])
	
	t = Table(data, colWidths=[300, 80, 100])
	t.setStyle(TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),('BOX', (0,0), (-1,-1), 0.25, colors.black),]))

	elements.append(t)
	doc.build(elements)

	return response

def logs(request):
	"""
	http://stackoverflow.com/questions/8432926/aggregate-difference-between-datetime-fields-in-djano
	It is apparently not possible to do time differences in Django models.
	"""

	## Method 1: Raw SQL
	## Status: Failure. Nothing happened!
	# Logs.objects.raw("DELETE FROM records_logs WHERE julianday('now') - julianday(created_on) > 30")

	## Method 2: Use the code from forkpi_db
	## Status: Failure. It couldn't find records_logs
	# with conn:
	# 	c = conn.cursor()
	# 	c.execute("DELETE FROM records_logs WHERE julianday('now') - julianday(created_on) > 30")

	## Method 3: Import and execute 
	## Status: Failure. Apparently, it couldn't find records_logs, just like Method 2
	# forkpi_db.delete_logs()

	## Method 4: Another direct SQL trial.
	## Status: Worked!
	cursor = connection.cursor()	
	cursor.execute("DELETE FROM records_logs WHERE julianday('now') - julianday(created_on) > 30")
	# cursor.execute("SELECT *, julianday('now'), julianday(created_on), julianday('now') - julianday(created_on) FROM records_logs")
	# print cursor.fetchone()
	
	if not request.session.get('userid'):
		return HttpResponseNotFound('<h1>Page not found</h1>')

	userActions = getUserActions(request)
	loginText = getLoginText(request)


	logs = Logs.objects.all()
	return render(request, 'logs.html', {'logs': logs, 'loginText': loginText, 'userActions': userActions})