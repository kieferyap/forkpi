from django.shortcuts import render
from django.shortcuts import redirect, render, HttpResponse
from django.http import HttpResponseNotFound
from django.contrib import messages

import datetime
import hashlib
import reportlab

from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet

from records.models import Users
from records.models import Kiefers

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
		userActions[0]["name"] = "My Keypairs"
		userActions[0]["url"] = "keypairs"
		userActions[1] = {}
		userActions[1]["name"] = "Logout"
		userActions[1]["url"] = "logout"

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
	

	## Encode password in MD5
	hash_object = hashlib.md5(request.POST['password'].encode('utf-8'))
	password_md5 = str(hash_object.hexdigest())

	## Check if user is in the database	
	try:
		user = Users.objects.get(username=request.POST['username'], password=password_md5)
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
	## If the user didn't put in all the details...
	if(request.POST['username'].strip() == '' or request.POST['password'].strip() == '' or request.POST['email'].strip() == ''):
		messages.add_message(request, messages.ERROR, 'All the fields are required.')
		return redirect('/signup')

	## If the user already has an entry in the database...
	byUsername = Users.objects.all().filter(username = request.POST['username'])
	byEmailAdd = Users.objects.all().filter(email = request.POST['email'])
	if(len(byUsername) > 0 or len(byEmailAdd) > 0):
		messages.add_message(request, messages.ERROR, 'Hmm. It looks like you already have an entry in my database...')
		return redirect('/signup')

	## Not the most secure, but for our purposes, password is encoded in MD5
	hash_object = hashlib.md5(request.POST['password'].encode('utf-8'))
	password_md5 = str(hash_object.hexdigest())

	## Insert user into database
	Users.objects.create(
		username = request.POST['username'],
		email = request.POST['email'],
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
	return render(request, 'keypairs.html',  {'loginText': loginText, 'userActions': userActions, 'keypairs': keypairs})

def addpair(request):
	Kiefers.objects.create(
		name = request.POST['name'],
		pin = request.POST['pin'],
		rfid_uid = request.POST['uid']
	)
	return redirect('/keypairs')

def editname(request):
	Kiefers.objects.filter(id = request.POST['kid']).update(name = request.POST['value'])
	return HttpResponse("Successful.")

def editpin(request):
	Kiefers.objects.filter(id = request.POST['kid']).update(pin = request.POST['value'])
	return HttpResponse("Successful.")

def edituid(request):
	Kiefers.objects.filter(id = request.POST['kid']).update(rfid_uid = request.POST['value'])
	return HttpResponse("Successful.")

def deletekeypair(request):
	Kiefers.objects.filter(id = request.POST['kid']).delete()
	return HttpResponse("Successful.")

# Attempt: print as PDF
def pdflist(request):
	# Create the HttpResponse object with the appropriate PDF headers.
	response = HttpResponse(content_type='application/pdf')
	response['Content-Disposition'] = 'attachment; filename="mylist.pdf"'

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