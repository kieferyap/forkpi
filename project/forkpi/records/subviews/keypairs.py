from django.shortcuts import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings

import hashlib
import binascii

from records.views import render, redirect_to_name
from records.models import Keypair
from records.aes import AES

from spoonpi.spoonpi.nfc_reader import NFCReader
from spoonpi.spoonpi.fingerprint import FingerprintScanner


def encrypt(value, key=None):
	if not key:
		key = settings.SECRET_KEY
	return AES(key).encrypt(value)

def decrypt(value, key=None):
	if not key:
		key = settings.SECRET_KEY
	return AES(key).decrypt(value)

def hash_string(value):
	return hashlib.sha1((value).encode()).hexdigest()

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
	uid = NFCReader().read_tag()
	return HttpResponse(uid)
	# TODO prevent multiple pollings from happening
	# response = HttpResponse("Please try again at a later time. Sorry for the inconvenience.")
	# response.status_code = 400
	# return response

@login_required
def scan_fingerprint(request):
	template = FingerprintScanner(debug=False).make_template()
	template = binascii.hexlify(template)
	return HttpResponse(template)

def is_valid_pin(pin):
	return len(pin)==0 or pin.isdigit()

@login_required
def new_keypair(request):
	name = request.POST['name']
	pin = request.POST['pin']
	rfid_uid = request.POST['rfid_uid']
	fingerprint_template = request.POST['fingerprint_template']

	is_error = False

	if not is_valid_pin(pin):
		messages.add_message(request, messages.ERROR, 'PIN must be blank or numeric.')
		is_error = True

	if is_error:
		return redirect_to_name('keypairs')

	hashpin = hash_string(pin)
	hashrfid = hash_string(rfid_uid)

	Keypair.objects.create(name=name, pin=encrypt(pin), rfid_uid=encrypt(rfid_uid), hash_pin=hashpin, hash_rfid=hashrfid, fingerprint_template=fingerprint_template)
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
		keypair.hash_pin = hash_string(pin)
		keypair.save()
		return HttpResponse("Successful.")
	else:
		messages.add_message(request, messages.ERROR, 'PIN must be blank or numeric.')
		response = HttpResponse("Invalid PIN")
		response.status_code = 400
		return response

@login_required
def edit_keypair_rfid(request):
	rfid_uid = request.POST['value']
	keypair = Keypair.objects.get(id = request.POST['kid'])
	keypair.rfid_uid = encrypt(rfid_uid)
	keypair.hash_rfid = hash_string(rfid_uid)
	keypair.save()
	return HttpResponse("Successful.")

@login_required
def edit_keypair_fingerprint(request):
	fingerprint_template = request.POST['value']
	keypair = Keypair.objects.get(id = request.POST['kid'])
	keypair.fingerprint_template = fingerprint_template
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