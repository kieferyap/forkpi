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
def user_toggle_active(request):
	user = User.objects.get(id = request.POST['id'])
	user.is_active = not user.is_active
	user.save()
	return HttpResponse("Successful.")

@login_required
def user_toggle_staff(request):
	user = User.objects.get(id = request.POST['id'])
	user.is_staff = not user.is_staff
	user.save()
	return HttpResponse("Successful.")

@login_required
def approve_user(request):
	user = User.objects.get(id = request.POST['id'])
	user.is_superuser = True
	user.save()
	return HttpResponse("Successful.")

@login_required
def delete_user(request):
	User.objects.filter(id = request.POST['id']).delete()
	return HttpResponse("Successful.")