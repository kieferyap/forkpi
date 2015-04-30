from django.shortcuts import render as django_render
from django.shortcuts import redirect as django_redirect
from django.core.urlresolvers import reverse
from records.models import User

def index_page(request):
	if request.user.is_authenticated():
		return redirect_to_name('keypairs')
	else:
		return redirect_to_name('login')

def get_login_text(request):
	if request.user.is_authenticated():
		return "Logged in as " + request.user.username
	else:
		return "You are not logged in."

def get_user_actions(request):
	if request.user.is_authenticated():
		userActions = list()
		userActions.append({'name':'Keypairs', 'url':reverse('keypairs')})
		userActions.append({'name':'Doors', 'url':reverse('doors')})
		userActions.append({'name':'Logs',     'url':reverse('logs')})

		if request.user.is_staff:
			unapproved_count = User.objects.filter(is_superuser = False).count()
			unapproved_count = ' ('+str(unapproved_count)+')' if unapproved_count > 0 else ''

			userActions.append({'name':'Users' + unapproved_count,   'url':reverse('users')})
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


from .subviews.keypairs import (
	keypairs_page, scan_rfid, scan_fingerprint_3x, wait_to_remove_finger, scan_fingerprint_1x,
	new_keypair, delete_keypair,
	edit_keypair_name, edit_keypair_pin, edit_keypair_rfid, edit_keypair_fingerprint, keypair_toggle_active,
	link_door_to_keypair, unlink_door_from_keypair, search_keypairs,
	authenticate_credential)
from .subviews.doors import (doors_page, edit_door_name,
	link_keypair_to_door, unlink_keypair_from_door, search_doors)
from .subviews.session import (login_page, logging_in, logout, must_be_logged_in)
from .subviews.signup import (signup_page, add_user)
from .subviews.logs import (logs_page, delete_logs_older_than)
from .subviews.users import (all_users, user_toggle_active, user_toggle_staff, delete_user, approve_user)
from .subviews.options import (options_page, edit_option_value, regenerate_secret_key)

