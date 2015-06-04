from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import HttpResponse
from django.http import JsonResponse

from records.views import render
from records.models import Door, Keypair

@login_required
def doors_page(request):
	doors = Door.objects.all().order_by('name')
	for door in doors:
		keypairs = []
		for keypair in door.keypair_set.all():
			keypairs.append({'id':keypair.id, 'name':keypair.name})
		door.keypairs_json = keypairs
	return render(request, 'doors.html',  {'doors': doors})

def is_valid_name(name, id=None):
	name_exists = Door.objects.filter(name=name).exclude(id=id).count() > 0
	return len(name)!=0 and not name_exists

@login_required
def edit_door_name(request):
	did = request.POST['id']
	name = request.POST['value']

	if is_valid_name(name, id=did):
		door = Door.objects.get(id=did)
		door.name = name
		door.save()
		return HttpResponse("Successful.")
	else:
		messages.add_message(request, messages.ERROR, 'Name must be unique and not blank.')
		response = HttpResponse('Invalid name')
		response.status_code = 400
		return response

@login_required
def link_keypair_to_door(request):
	door = Door.objects.get(id = request.POST['my_id'])
	keypair_id = request.POST['link_id']

	door.keypair_set.add(keypair_id)
	door.save()
	return HttpResponse("Successful.")

@login_required
def unlink_keypair_from_door(request):
	door = Door.objects.get(id = request.POST['my_id'])
	keypair_id = request.POST['link_id']

	door.keypair_set.remove(keypair_id)
	door.save()
	return HttpResponse("Successful.")

@login_required
def search_doors(request):
	name = request.GET.get('q', '')
	results = []
	doors = Door.objects.filter(name__icontains=name)
	for door in doors:
		results.append({'id':door.id, 'name':door.name})
	return JsonResponse(results, safe=False)