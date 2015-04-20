from django.shortcuts import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from records.views import render, redirect_to_name
from records.models import Option

from django.conf import settings
from forkpi import secret_key
from records.subviews import keypairs

@login_required
def options_page(request):
	if request.user.is_staff:
		options = Option.objects.all()
		return render(request, 'options.html', {'options': options})
	else:
		return redirect_to_name('index')

@login_required
def edit_option_value(request):
	value = request.POST['value']
	Option.objects.filter(id = request.POST['id']).update(value=value)
	return HttpResponse("Successful.")

@login_required
def regenerate_secret_key(request):
	old_key = settings.SECRET_KEY
	new_key = secret_key.regenerate_secret_key(settings.SECRET_KEY_PATH)
	keypairs.reencrypt_keypairs(old_key, new_key)
	settings.SECRET_KEY = new_key
	messages.add_message(request, messages.SUCCESS, 'Successfully regenerated the secret key.')
	return redirect_to_name('index')