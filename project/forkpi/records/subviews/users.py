from django.contrib import messages
from django.shortcuts import HttpResponse
from django.contrib.auth.decorators import login_required
from records.views import render, redirect_to_name
from records.models import User

@login_required
def all_users(request):
	if request.user.is_staff:
		users = User.objects.all()
		return render(request, 'users.html', {'users': users})
	else:
		return redirect_to_name('index')

@login_required
def user_toggle_staff(request):
	uid = int(request.POST['id'])

	if request.user.id == uid:
		messages.add_message(request, messages.ERROR, "You cannot demote yourself!")
		response = HttpResponse('Invalid action')
		response.status_code = 400
		return response
	else:
		user = User.objects.get(id=uid)
		user.is_staff = not user.is_staff
		user.save()
		return HttpResponse("Successful.")

@login_required
def user_toggle_active(request):
	uid = int(request.POST['id'])

	if request.user.id == uid:
		messages.add_message(request, messages.ERROR, "You cannot deactivate yourself!")
		response = HttpResponse('Invalid action')
		response.status_code = 400
		return response
	else:
		user = User.objects.get(id=uid)
		user.is_active = not user.is_active
		user.save()
		return HttpResponse("Successful.")

@login_required
def approve_user(request):
	user = User.objects.get(id = request.POST['id'])
	user.is_superuser = True
	user.save()
	messages.add_message(request, messages.SUCCESS, "Successfully approved '%s'." % user.username)
	return HttpResponse("Successful.")

@login_required
def delete_user(request):
	uid = int(request.POST['id'])

	if request.user.id == uid:
		messages.add_message(request, messages.ERROR, "You cannot delete yourself!")
		response = HttpResponse('Invalid action')
		response.status_code = 400
		return response
	else:
		User.objects.filter(id = uid).delete()
		return HttpResponse("Successful.")