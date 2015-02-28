from django.shortcuts import render as django_render
from django.shortcuts import redirect as django_redirect
from django.core.urlresolvers import reverse

def index_page(request):
	if request.user.is_authenticated():
		return redirect_to_name('keypairs')
	else:
		return redirect_to_name('login')

def get_login_text(request):
	if request.user.is_authenticated():
		return "Welcome back, " + request.user.username
	else:
		return "You are not logged in."

def get_user_actions(request):
	if request.user.is_authenticated():
		userActions = list()
		userActions.append({'name':'Keypairs', 'url':reverse('keypairs')})
		userActions.append({'name':'Logs',     'url':reverse('logs')})
		userActions.append({'name':'Options',  'url':reverse('options')})
		userActions.append({'name':'Logout',   'url':reverse('logout')})
		return userActions
	else:
		userActions = list()
		userActions.append({'name':'Login',    'url':reverse('login')})
		userActions.append({'name':'Signup',   'url':reverse('signup')})
		return userActions
	
def render(request, template, passVars=dict()):
	passVars['loginText'] = get_login_text(request)
	passVars['userActions'] = get_user_actions(request)
	return django_render(request, template, passVars)

def redirect_to_name(name):
	return django_redirect(reverse(name))


from subviews.keypairs import *
from subviews.session import login_page, loggingin, logout, mustbeloggedin
from subviews.signup import signup_page, adduser
from subviews.logs import logs_page
from subviews.options import options_page

