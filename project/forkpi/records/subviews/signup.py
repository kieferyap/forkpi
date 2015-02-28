from django.contrib import messages
from django.shortcuts import redirect

from records.views import renderWithLoginTextAndUserActions
from records.models import User

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
	byUsername = User.objects.filter(username = username)
	byEmailAdd = User.objects.filter(email = email)
	if(len(byUsername) > 0 or len(byEmailAdd) > 0):
		messages.add_message(request, messages.ERROR, 'Hmm. It looks like you already have an entry in my database...')
		return redirect('/signup/')

	## Insert user into database
	User.objects.create_user(username = username, password = password, email = email)

	messages.add_message(request, messages.SUCCESS, 'Your sign up was successful and is now awaiting admin approval.')
	return redirect('/login/')
