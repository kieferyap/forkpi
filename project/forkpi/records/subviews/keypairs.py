from django.shortcuts import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings

import hashlib

from records.views import render, redirect_to_name
from records.models import Keypair
from spoonpi.nfc_reader import NFCReader
from records.aes import AES

is_polling = False


def encrypt(value, key=None):
	if not key:
		key = settings.SECRET_KEY
	return AES(key).encrypt(value)

def decrypt(value, key=None):
	if not key:
		key = settings.SECRET_KEY
	return AES(key).decrypt(value)

def hash_keypair(pin, rfid_uid):
	return hashlib.sha1((pin + rfid_uid).encode()).hexdigest()

@login_required
def keypairs_page(request):
	keypairs = Keypair.objects.all()
	for keypair in keypairs:
		keypair.pin = decrypt(keypair.pin)
		keypair.rfid_uid = decrypt(keypair.rfid_uid)
	return render(request, 'keypairs.html',  {'keypairs': keypairs})

def reencrypt_keypairs(old_key, new_key):
	keypairs = Keypair.objects.all()
	for keypair in keypairs:
		keypair.pin = decrypt(keypair.pin, key=old_key)
		keypair.pin = encrypt(keypair.pin, key=new_key)
		keypair.rfid_uid = decrypt(keypair.rfid_uid, key=old_key)
		keypair.rfid_uid = encrypt(keypair.rfid_uid, key=new_key)
		keypair.save()


@login_required
def scan_rfid(request):
	global is_polling
	if not is_polling:
		is_polling = True
		uid = NFCReader().read_tag()
		is_polling = False
		return HttpResponse(uid)
	else:
		response = HttpResponse("Please try again at a later time. Sorry for the inconvenience.")
		response.status_code = 400
		return response

def is_valid_pin(pin):
	return len(pin)==0 or pin.isdigit()

@login_required
def new_keypair(request):
	name = request.POST['name']
	pin = request.POST['pin']
	rfid_uid = request.POST['rfid_uid']

	is_error = False

	if not is_valid_pin(pin):
		messages.add_message(request, messages.ERROR, 'PIN must be blank or numeric.')
		is_error = True

	if is_error:
		return redirect_to_name('keypairs')

	hashpass = hash_keypair(pin, rfid_uid)

	Keypair.objects.create(name=name, pin=encrypt(pin), rfid_uid=encrypt(rfid_uid), hash_pin_rfid=hashpass)
	messages.add_message(request, messages.SUCCESS, 'Pair addition successful.')
	return redirect_to_name('keypairs')

@login_required
def edit_keypair_name(request):
	name = request.POST['value']
	Keypair.objects.filter(id = request.POST['kid']).update(name=name)
	return HttpResponse("Successful.")

@login_required
def edit_keypair_pin(request):
	pin = request.POST['value']

	if is_valid_pin(pin):
		keypair = Keypair.objects.get(id = request.POST['kid'])
		keypair.pin = encrypt(pin)
		keypair.hashpass = hash_keypair(pin, decrypt(keypair.rfid_uid))
		keypair.save()
		return HttpResponse("Successful.")
	else:
		messages.add_message(request, messages.ERROR, 'PIN must be blank or numeric.')
		response = HttpResponse("Invalid PIN")
		response.status_code = 400
		return response

@login_required
def edit_keypair_uid(request):
	rfid_uid = request.POST['value']
	keypair = Keypair.objects.get(id = request.POST['kid'])
	keypair.rfid_uid = encrypt(rfid_uid)
	keypair.hashpass = hash_keypair(decrypt(keypair.pin), rfid_uid)
	keypair.save()
	return HttpResponse("Successful.")

@login_required
def delete_keypair(request):
	Keypair.objects.filter(id = request.POST['kid']).delete()
	return HttpResponse("Successful.")

@login_required
def keypair_toggle_active(request):
	keypair = Keypair.objects.get(id = request.POST['kid'])
	keypair.is_active = not keypair.is_active
	keypair.save()
	return HttpResponse("Successful.")

@login_required
def print_pdf(request):
	from reportlab.lib import colors
	from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
	from reportlab.lib.pagesizes import letter
	from reportlab.lib.styles import getSampleStyleSheet

	response = HttpResponse(content_type='application/pdf')
	response['Content-Disposition'] = 'attachment; filename="forkpi_keypairs.pdf"'

	doc = SimpleDocTemplate(response, pagesize=letter)
	elements = []
	styles = getSampleStyleSheet()
	style = styles['Normal']
	keypairs = Keypair.objects.all()

	data = []
	data.append(['Name', 'RFID UID'])

	for keypair in keypairs:
		if keypair.is_active:
			style.textColor = colors.black
		else:
			style.textColor = colors.gray
		data.append([Paragraph(str(keypair.name), style), Paragraph(str(keypair.rfid_uid), style)])
	
	t = Table(data, colWidths=[300, 100])
	t.setStyle(TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),('BOX', (0,0), (-1,-1), 0.25, colors.black),]))
	elements.append(t)
	doc.build(elements)
	return response