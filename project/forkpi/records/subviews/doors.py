from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from records.models import Door

@login_required
def search_doors(request):
	name = request.GET.get('q', '')
	results = []
	doors = Door.objects.filter(name__icontains=name)
	for door in doors:
		results.append({'id':door.id, 'name':door.name})
	return JsonResponse(results, safe=False)