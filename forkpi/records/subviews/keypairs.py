from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse

import hashlib
import base64

from records.views import render, redirect_to_name
from records.models import Keypair, Door
from records.aes import AES

from spoonpi.spoonpi.rfid.rfid_reader import RfidReader
from spoonpi.spoonpi.fingerprint.fingerprint_scanner import FingerprintScanner


def encrypt(value, key=None):
	if not key:
		key = settings.SECRET_KEY
	return AES(key).encrypt(value)

def decrypt(value, key=None):
	if not key:
		key = settings.SECRET_KEY
	return AES(key).decrypt(value)

def hash_string(value):
	return hashlib.sha1(value.encode()).hexdigest()

@login_required
def keypairs_page(request):
	keypairs = Keypair.objects.filter(is_active=True).order_by('-last_edited_on')
	deactivated_keypairs = Keypair.objects.filter(is_active=False).order_by('-last_edited_on')
	
	for keypair in keypairs:
		keypair.pin = decrypt(keypair.pin)
		keypair.rfid_uid = decrypt(keypair.rfid_uid)
		doors = []
		for door in keypair.doors.all():
			doors.append({'id':door.id, 'name':door.name})
		keypair.doors_json = doors

	for keypair in deactivated_keypairs:
		keypair.pin = decrypt(keypair.pin)
		keypair.rfid_uid = decrypt(keypair.rfid_uid)
		doors = []
		for door in keypair.doors.all():
			doors.append({'id':door.id, 'name':door.name})
		keypair.doors_json = doors

	return render(request, 'keypairs.html',  {'keypairs': keypairs, 'deactivated_keypairs': deactivated_keypairs})

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
	rfid_uid = RfidReader().read_tag(blocking=False)
	if rfid_uid:
		return HttpResponse(rfid_uid)
	else:
		response = HttpResponse('No RFID tag detected')
		response.status_code = 400
		return response

@login_required
def scan_fingerprint_3x(request):
	fps = FingerprintScanner(debug=True)
	stage = int(request.POST['stage'])
	ret = fps.enroll(stage=stage)
	if ret is False:
		response = HttpResponse('No finger detected')
		response.status_code = 400
		return response
	elif stage == 3:
		template = base64.b64encode(ret)		
		return HttpResponse(template)
	else:
		return HttpResponse('')

@login_required
def wait_to_remove_finger(request):
	fps = FingerprintScanner(debug=False)
	fps.wait_to_remove_finger()
	return HttpResponse('')

@login_required
def scan_fingerprint_1x(request):
	fps = FingerprintScanner(debug=False)
	template = fps.make_template(tries=2)
	fps.backlight_off()
	if template:
		template = base64.b64encode(template)
		return HttpResponse(template)
	else:
		response = HttpResponse("No finger detected")
		response.status_code = 400
		return response


def is_valid_name(name, id=None):
	name_exists = Keypair.objects.filter(name=name).exclude(id=id).count() > 0
	return len(name)!=0 and not name_exists

def is_valid_pin(pin):
	return len(pin)>=4 and pin.isdigit()

def is_valid_keypair_rfid(kid):
	return not Keypair.objects.filter(id=kid, fingerprint_template='').count() > 0

def is_valid_keypair_fingerprint(kid):
	return not Keypair.objects.filter(id=kid, hash_rfid=hash_string('')).count() > 0

@login_required
def new_keypair(request):
	name = request.POST['name']
	pin = request.POST['pin']
	rfid_uid = request.POST['rfid_uid']
	fingerprint_template = request.POST['fingerprint_template']
	door_ids = request.POST['doors']

	is_error = False

	if not is_valid_name(name):
		messages.add_message(request, messages.ERROR, 'Name must be unique and not blank.')
		is_error = True
	if pin and not is_valid_pin(pin):
		messages.add_message(request, messages.ERROR, 'PIN must be at least 4 numeric characters.')
		is_error = True
	if not(rfid_uid or fingerprint_template):
		messages.add_message(request, messages.ERROR, 'A fingerprint template OR an RFID card must be entered.')
		is_error = True

	if is_error:
		return redirect_to_name('keypairs')

	hashpin = hash_string(pin)
	hashrfid = hash_string(rfid_uid)

	keypair = Keypair.objects.create(name=name, pin=encrypt(pin), rfid_uid=encrypt(rfid_uid),
			hash_pin=hashpin, hash_rfid=hashrfid, fingerprint_template=fingerprint_template, last_edited_by=request.user)
	if door_ids:
		door_ids = door_ids.split(',')
		keypair.doors.add(*door_ids)
	messages.add_message(request, messages.SUCCESS, 'Pair addition successful.')
	return redirect_to_name('keypairs')

@login_required
def edit_keypair_name(request):
	kid = request.POST['id']
	name = request.POST['value']

	if is_valid_name(name, id=kid):
		keypair = Keypair.objects.get(id=kid)
		keypair.last_edited_by = request.user
		keypair.name = name
		keypair.save()
		return HttpResponse("Successful.")
	else:
		messages.add_message(request, messages.ERROR, 'Name must be unique and not blank.')
		response = HttpResponse('Invalid name')
		response.status_code = 400
		return response

@login_required
def edit_keypair_pin(request):
	pin = request.POST['value']

	if is_valid_pin(pin):
		keypair = Keypair.objects.get(id = request.POST['id'])
		keypair.last_edited_by = request.user
		keypair.pin = encrypt(pin)
		keypair.hash_pin = hash_string(pin)
		keypair.save()
		return HttpResponse("Successful.")
	else:
		messages.add_message(request, messages.ERROR, 'PIN must be at least 4 numeric characters.')
		response = HttpResponse("Invalid PIN: PIN must be at least 4 numeric characters.")
		response.status_code = 400
		return response

@login_required
def edit_keypair_rfid(request):
	rfid_uid = request.POST['value']
	kid = request.POST['id']
	keypair = Keypair.objects.get(id = kid)

	if rfid_uid == '' and not is_valid_keypair_rfid(kid):
		messages.add_message(request, messages.ERROR, 'A fingerprint template OR an RFID card must be entered.')
		response = HttpResponse("Error: A fingerprint template OR an RFID card must be entered.")
		response.status_code = 400
		return response

	keypair.last_edited_by = request.user
	keypair.rfid_uid = encrypt(rfid_uid)
	keypair.hash_rfid = hash_string(rfid_uid)
	keypair.save()
	return HttpResponse("Successful.")

@login_required
def edit_keypair_fingerprint(request):
	kid = request.POST['id']
	fingerprint_template = request.POST['value']
	keypair = Keypair.objects.get(id = kid)

	if fingerprint_template == '' and not is_valid_keypair_fingerprint(kid):
		messages.add_message(request, messages.ERROR, 'A fingerprint template OR an RFID card must be entered.')
		response = HttpResponse("Error: A fingerprint template OR an RFID card must be entered.")
		response.status_code = 400
		return response

	keypair.last_edited_by = request.user
	keypair.fingerprint_template = fingerprint_template
	keypair.save()
	return HttpResponse("Successful.")	

@login_required
def delete_keypair(request):
	Keypair.objects.filter(id = request.POST['id']).delete()
	return HttpResponse("Successful.")

@login_required
def keypair_toggle_active(request):
	keypair = Keypair.objects.get(id = request.POST['id'])

	keypair.last_edited_by = request.user
	keypair.is_active = not keypair.is_active
	keypair.save()
	return HttpResponse("Successful.")

@login_required
def link_door_to_keypair(request):
	keypair = Keypair.objects.get(id = request.POST['my_id'])
	door_id = request.POST['link_id']

	keypair.last_edited_by = request.user
	keypair.doors.add(door_id)
	keypair.save()
	return HttpResponse("Successful.")

@login_required
def unlink_door_from_keypair(request):
	keypair = Keypair.objects.get(id = request.POST['my_id'])
	door_id = request.POST['link_id']

	keypair.last_edited_by = request.user
	keypair.doors.remove(door_id)
	keypair.save()

	return HttpResponse("Successful.")

@login_required
def search_keypairs(request):
	name = request.GET.get('q', '')
	results = []
	keypairs = Keypair.objects.filter(name__icontains=name)
	for keypair in keypairs:
		results.append({'id':keypair.id, 'name':keypair.name})
	return JsonResponse(results, safe=False)

@login_required
def authenticate_credential(request):
	kid = request.POST['id']
	auth_val = request.POST['val']
	auth_type = request.POST['type']

	try:
		if auth_type == 'pin':
			# raises an error if not found
			keypair = Keypair.objects.get(hash_pin=hash_string(auth_val), id=kid)
		elif auth_type == 'rfid':
			keypair = Keypair.objects.get(hash_rfid=hash_string(auth_val), id=kid)
		elif auth_type == 'fingerprint':
			keypair = Keypair.objects.get(id=kid)

			template = keypair.fingerprint_template
			if len(auth_val) != 664 or len(template) != 664:
				raise ValueError("Template must be 664 characters long")

			fps = FingerprintScanner(debug=False)
			fps.delete_template(tid=0)

			# raises an error if it contains invalid characters
			template = base64.b64decode(bytes(template, 'utf-8'), validate=True)
			fps.upload_template(tid=0, template=template)

			# raises an error if it contains invalid characters
			auth_val = base64.b64decode(bytes(auth_val, 'utf-8'), validate=True)
			if fps.verify_template(tid=0, template=auth_val):
				# templates match, verification ok
				pass
			else:
				raise Exception("Templates do not match")

		response_text = {'pin':decrypt(keypair.pin), 'rfid_uid':decrypt(keypair.rfid_uid), 'fingerprint_template':keypair.fingerprint_template}
		return JsonResponse(response_text, safe=False)
	except Exception as e:
		response = HttpResponse("incorrect credentials")
		response.status_code = 400
		return response
