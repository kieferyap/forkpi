from django.contrib import messages

from records.views import render, redirect_to_name
from records.models import User

# Signup display
def signup_page(request):
	if request.user.is_authenticated():
		messages.add_message(request, messages.ERROR, 'You have already logged in. Kindly log out first to access the signup page.')
		return redirect_to_name('keypairs')
	else:
		return render(request, 'signup.html')

# Adding a user
def add_user(request):
	username = request.POST['username']
	password = request.POST['password']
	email = request.POST['email']
	## If the user didn't put in all the details...
	if(username.strip() == '' or password.strip() == '' or email.strip() == ''):
		messages.add_message(request, messages.ERROR, 'All the fields are required.')
		return redirect_to_name('signup')

	## If the user already has an entry in the database...
	byUsername = User.objects.filter(username = username)
	byEmailAdd = User.objects.filter(email = email)
	if(len(byUsername) > 0 or len(byEmailAdd) > 0):
		messages.add_message(request, messages.ERROR, 'Hmm. It looks like you already have an entry in my database...')
		return redirect_to_name('signup')

	## Insert user into database
	user = User.objects.create_user(username=username, password=password, email=email)

	## If this is the only user in the database, make this user a staff superuser
	if User.objects.count() == 1:
		user.is_superuser = True
		user.is_staff = True
		user.save()
		messages.add_message(request, messages.SUCCESS, 'Sign-up successful! You may log in now.')
	else:
		messages.add_message(request, messages.SUCCESS, 'Your sign up was successful and is now awaiting admin approval.')
	return redirect_to_name('login')
