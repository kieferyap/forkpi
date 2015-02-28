from django.db import connection
from django.contrib.auth.decorators import login_required

from records.views import render
from records.models import Log

@login_required
def logs_page(request):
	cursor = connection.cursor()	
	cursor.execute("DELETE FROM records_log WHERE now() - created_on > INTERVAL '30 days'")
	
	logs = Log.objects.all()
	return render(request, 'logs.html', {'logs': logs})