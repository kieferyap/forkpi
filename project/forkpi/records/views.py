from django.shortcuts import redirect, render, HttpResponse
from django.core.urlresolvers import reverse 
from django.http import HttpResponseNotFound
from django.contrib import messages
from django.db import connection

import datetime
import hashlib
from spoonpi.nfc_reader import NFCReader

import reportlab

from records.models import User, Keypair, Log
from django.contrib import auth
from django.contrib.auth.decorators import login_required

is_polling = False

def index_page(request):
	if request.user.is_authenticated():
		return redirect('/keypairs/')
	else:
		return redirect('/login/?next=keypairs')

####################
# Session Handling #
####################

def getLoginText(request):
	if request.user.is_authenticated():
		return "Welcome back, " + request.user.username
	else:
		return "You are not logged in."

def getUserActions(request):
	if request.user.is_authenticated():
		userActions = list()
		userActions.append({'name':'Keypairs', 'url':'/keypairs/'})
		userActions.append({'name':'Logs', 'url':'/logs/'})
		userActions.append({'name':'Logout', 'url':'/logout'})
		return userActions
	else:
		userActions = list()
		userActions.append({'name':'Login', 'url':'/login/'})
		userActions.append({'name':'Signup', 'url':'/signup/'})
		return userActions
	
def renderWithLoginTextAndUserActions(request, template, passVars=dict()):
	passVars['loginText'] = getLoginText(request)
	passVars['userActions'] = getUserActions(request)
	return render(request, template, passVars)

# Login display
def login_page(request):
	if request.user.is_authenticated():
		messages.add_message(request, messages.ERROR, 'You have already logged in. Kindly log out first to access the login page.')
		return redirect('/keypairs/')
	else:
		return renderWithLoginTextAndUserActions(request, 'login.html')

# Logging the user in
def loggingin(request):
	username = request.POST['username']
	password = request.POST['password']

	user = auth.authenticate(username=username, password=password)
	if user is not None:
		if user.is_superuser:
			auth.login(request, user)
			messages.add_message(request, messages.SUCCESS, 'Awesome! Your login was successful.')
			return redirect('/keypairs/')
		else:
			messages.add_message(request, messages.ERROR, 'Sorry, your account is still awaiting admin approval.')
			return redirect('/login/')
	else:
		messages.add_message(request, messages.ERROR, 'I don\'t seem to recognize your username-password combination...')
		return redirect('/login/')

def logout(request):
	if request.user.is_authenticated():
		auth.logout(request)
		messages.add_message(request, messages.SUCCESS, 'Logged out successfully.')
		return redirect('/')
	else:
		messages.add_message(request, messages.ERROR, "If you're not logged in, how can you log out?")
		return redirect('/login/')


#####################
# Signup Controller #
#####################

# Signup display
def signup_page(request):
	if request.user.is_authenticated():
		messages.add_message(request, messages.ERROR, 'You have already logged in. Kindly log out first to access the signup page.')
		return redirect('/keypairs/')
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
		return redirect('/signup/')

	## If the user already has an entry in the database...
	byUsername = User.objects.all().filter(username = username)
	byEmailAdd = User.objects.all().filter(email = email)
	if(len(byUsername) > 0 or len(byEmailAdd) > 0):
		messages.add_message(request, messages.ERROR, 'Hmm. It looks like you already have an entry in my database...')
		return redirect('/signup/')

	## Insert user into database
	User.objects.create_user(username = username, password = password, email = email)

	messages.add_message(request, messages.SUCCESS, 'Your sign up was successful and is now awaiting admin approval.')
	return redirect('/login/')

######################
# Keypair Controller #
######################
@login_required
def keypairs_page(request):
	keypairs = Keypair.objects.all()
	return renderWithLoginTextAndUserActions(request, 'keypairs.html',  {'keypairs': keypairs})

@login_required
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

@login_required
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
		return redirect('/keypairs/')

	Keypair.objects.create(name = name, pin = pin, rfid_uid = rfid_uid)
	messages.add_message(request, messages.SUCCESS, 'Pair addition successful.')
	return redirect('/keypairs/')

@login_required
def editname(request):
	name = request.POST['value']
	Keypair.objects.filter(id = request.POST['kid']).update(name=name)
	return HttpResponse("Successful.")

@login_required
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

@login_required
def edituid(request):
	Keypair.objects.filter(id = request.POST['kid']).update(rfid_uid=request.POST['value'])
	return HttpResponse("Successful.")

@login_required
def deletekeypair(request):
	Keypair.objects.filter(id = request.POST['kid']).delete()
	return HttpResponse("Successful.")

@login_required
def toggleactivekeypair(request):
	keypair = Keypair.objects.get(id = request.POST['kid'])
	keypair.is_active = not keypair.is_active
	keypair.save()
	return HttpResponse("Successful.")	

@login_required
def printpdf(request):
	from reportlab.lib import colors
	from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
	from reportlab.lib.pagesizes import letter
	from reportlab.lib.styles import getSampleStyleSheet

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

@login_required
def logs_page(request):
	cursor = connection.cursor()	
	cursor.execute("DELETE FROM records_log WHERE now() - created_on > INTERVAL '30 days'")
	
	logs = Log.objects.all()
	return renderWithLoginTextAndUserActions(request, 'logs.html', {'logs': logs})