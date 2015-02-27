from django.shortcuts import render
from django.shortcuts import redirect, render, HttpResponse
from django.http import HttpResponseNotFound
from django.contrib import messages
from django.db import connection

import datetime
import hashlib
from spoonpi.nfc_reader import NFCReader

import reportlab
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet

from records.models import User, Keypair, Log

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
		userActions = list()
		userActions.append({'name':'Keypairs', 'url':'keypairs'})
		userActions.append({'name':'Logs', 'url':'logs'})
		userActions.append({'name':'Logout', 'url':'logout'})
		return userActions
	else:
		userActions = dict()
		userActions.append({'name':'Login', 'url':'login'})
		userActions.append({'name':'Signup', 'url':'signup'})
		return userActions
	
def renderWithLoginTextAndUserActions(request, template, passVars=dict()):
	passVars['loginText'] = getLoginText(request)
	passVars['userActions'] = getUserActions(request)
	return render(request, template, passVars)

# Login display
def login(request):
	if request.session.get('userid'):
		messages.add_message(request, messages.ERROR, 'You have already logged in. Kindly log out first to access the login page.')
		return redirect('/keypairs')
	else:
		return renderWithLoginTextAndUserActions(request, 'login.html')

# Logging the user in
def loggingin(request):
	username = request.POST['username']
	## Encode password in MD5
	hash_object = hashlib.md5(request.POST['password'].encode('utf-8') + username)
	password_md5 = str(hash_object.hexdigest())

	## Check if user is in the database	
	try:
		user = User.objects.get(username=username, password=password_md5)
	except User.DoesNotExist:
		messages.add_message(request, messages.ERROR, 'I don\'t seem to recognize your username-password combination...')
		return redirect('/login')
	else:
		## Session handling
		request.session['userid'] = user.userid
		request.session['username'] = user.username

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
		return renderWithLoginTextAndUserActions(request, 'signup.html')

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
	byUsername = User.objects.all().filter(username = username)
	byEmailAdd = User.objects.all().filter(email = email)
	if(len(byUsername) > 0 or len(byEmailAdd) > 0):
		messages.add_message(request, messages.ERROR, 'Hmm. It looks like you already have an entry in my database...')
		return redirect('/signup')

	## Not the most secure, but for our purposes, password is encoded in MD5, with salting! :D
	hash_object = hashlib.md5(password.encode('utf-8') + username)
	password_md5 = str(hash_object.hexdigest())

	## Insert user into database
	User.objects.create(
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

	return renderWithLoginTextAndUserActions(request, 'login.html')


######################
# Keypair Controller #
######################

def keypairs(request):
	if not request.session.get('userid'):
		return HttpResponseNotFound('<h1>Page not found</h1>')

	keypairs = Keypair.objects.all()
	return renderWithLoginTextAndUserActions(request, 'keypairs.html',  {'keypairs': keypairs})

def addrfid(request):
	global is_polling
	if not is_polling:
		is_polling = True
		uid = NFCReader().read_tag()
		is_polling = False
		return HttpResponse(uid)
	else:
		response = HttpResponse("Please try again at a later time. Sorry for the inconvenience.")
		response.status_code = 400
		return response

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

	Keypair.objects.create(name = name, pin = pin, rfid_uid = rfid_uid)
	messages.add_message(request, messages.SUCCESS, 'Pair addition successful.')
	return redirect('/keypairs')

def editname(request):
	name = request.POST['value']
	Keypair.objects.filter(id = request.POST['kid']).update(name=name)
	return HttpResponse("Successful.")

def editpin(request):
	pin = request.POST['value']

	if not (len(pin) == 0 or (len(pin) == 4 and pin.isdigit())):
		messages.add_message(request, messages.ERROR, 'PIN must be blank, or consist of 4 digits.')
		response = HttpResponse("Invalid PIN")
		response.status_code = 400
		return response
	else:
		Keypair.objects.filter(id = request.POST['kid']).update(pin=pin)
		return HttpResponse("Successful.")

def edituid(request):
	Keypair.objects.filter(id = request.POST['kid']).update(rfid_uid=request.POST['value'])
	return HttpResponse("Successful.")

def deletekeypair(request):
	Keypair.objects.filter(id = request.POST['kid']).delete()
	return HttpResponse("Successful.")

def toggleactivekeypair(request):
	keypair = Keypair.objects.get(id = request.POST['kid'])
	keypair.is_active = not keypair.is_active
	keypair.save()
	return HttpResponse("Successful.")	

def printpdf(request):
	response = HttpResponse(content_type='application/pdf')
	response['Content-Disposition'] = 'attachment; filename="forkpi_keypairs.pdf"'

	doc = SimpleDocTemplate(response, pagesize=letter)
	elements = []
	styles = getSampleStyleSheet()
	style = styles['Normal']
	keypairs = Keypair.objects.all()

	data = []
	data.append(['Name', 'RFID UID'])

	for keypair in keypairs:
		if keypair.is_active:
			style.textColor = colors.black
		else:
			style.textColor = colors.gray
		data.append([Paragraph(str(keypair.name), style), Paragraph(str(keypair.rfid_uid), style)])
	
	t = Table(data, colWidths=[300, 100])
	t.setStyle(TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),('BOX', (0,0), (-1,-1), 0.25, colors.black),]))
	elements.append(t)
	doc.build(elements)
	return response

def logs(request):
	cursor = connection.cursor()	
	cursor.execute("DELETE FROM records_log WHERE now() - created_on > INTERVAL '30 days'")
	
	if not request.session.get('userid'):
		return HttpResponseNotFound('<h1>Page not found</h1>')

	logs = Log.objects.all()
	return renderWithLoginTextAndUserActions(request, 'logs.html', {'logs': logs})