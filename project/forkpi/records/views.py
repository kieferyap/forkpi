from django.shortcuts import redirect, render
from django.core.urlresolvers import reverse 

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
		userActions.append({'name':'Options', 'url':'/options/'})
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


from subviews.keypairs import *
from subviews.session import login_page, loggingin, logout, mustbeloggedin
from subviews.signup import signup_page, adduser
from subviews.logs import logs_page
from subviews.options import options_page

