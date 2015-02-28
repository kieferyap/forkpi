from django.contrib import auth, messages
from django.shortcuts import redirect
from records.views import renderWithLoginTextAndUserActions

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

def mustbeloggedin(request):
	messages.add_message(request, messages.ERROR, 'You must be logged in to access that page.')
	return redirect('/login/')

