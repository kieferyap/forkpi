from django.db import connection
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from records.views import render, redirect_to_name
from records.models import Log

@login_required
def logs_page(request):
	cursor = connection.cursor()
	
	logs = Log.objects.all().order_by('-created_on')
	return render(request, 'logs.html', {'logs': logs})

@login_required
def delete_logs_older_than(request):
	days = request.POST['days']
	if days.isdigit():
		days = int(days)
		cursor = connection.cursor()	
		cursor.execute("DELETE FROM records_log WHERE now() - created_on > INTERVAL '%s days'" % days)
		messages.add_message(request, messages.SUCCESS, '%d old logs successfully deleted.' % cursor.rowcount)
	else:
		messages.add_message(request, messages.ERROR, 'Number of days must be numeric')
	return redirect_to_name('logs')

