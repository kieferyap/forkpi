from django.contrib import auth, messages
from records.views import render, redirect_to_name

# Login display
def login_page(request):
	if request.user.is_authenticated():
		messages.add_message(request, messages.ERROR, 'You have already logged in. Kindly log out first to access the login page.')
		return redirect_to_name('keypairs')
	else:
		return render(request, 'login.html')

# Logging the user in
def logging_in(request):
	username = request.POST['username']
	password = request.POST['password']

	user = auth.authenticate(username=username, password=password)
	if user is not None:
		if user.is_superuser and user.is_active:
			auth.login(request, user)
			messages.add_message(request, messages.SUCCESS, 'Awesome! Your login was successful.')
			return redirect_to_name('keypairs')
		elif not user.is_superuser:
			messages.add_message(request, messages.ERROR, 'Sorry, your account is still awaiting admin approval.')
			return redirect_to_name('login')
		else:
			messages.add_message(request, messages.ERROR, 'Your account has been marked as inactive. '
				'Please contact the admin to activate it.')
			return redirect_to_name('login')
	else:
		messages.add_message(request, messages.ERROR, 'I don\'t seem to recognize your username-password combination...')
		return redirect_to_name('login')

def logout(request):
	if request.user.is_authenticated():
		auth.logout(request)
		messages.add_message(request, messages.SUCCESS, 'Logged out successfully.')
		return redirect_to_name('index')
	else:
		messages.add_message(request, messages.ERROR, "If you're not logged in, how can you log out?")
		return redirect_to_name('login')

def must_be_logged_in(request):
	messages.add_message(request, messages.ERROR, 'You must be logged in to access that page.')
	return redirect_to_name('login')

