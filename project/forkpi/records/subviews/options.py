from django.shortcuts import HttpResponse
from django.contrib.auth.decorators import login_required

from records.views import render
from records.models import Option

@login_required
def options_page(request):
	options = Option.objects.all()
	return render(request, 'options.html', {'options': options})

@login_required
def edit_option_value(request):
	value = request.POST['value']
	Option.objects.filter(id = request.POST['kid']).update(value=value)
	return HttpResponse("Successful.")