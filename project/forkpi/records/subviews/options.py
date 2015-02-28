from django.contrib.auth.decorators import login_required

from records.views import renderWithLoginTextAndUserActions
from records.models import Option


@login_required
def options_page(request):
	from records.views import renderWithLoginTextAndUserActions
	options = Option.objects.all()
	return renderWithLoginTextAndUserActions(request, 'options.html', {'options': options})