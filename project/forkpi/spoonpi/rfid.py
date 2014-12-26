from nfc_reader import NFCReader
nfc_reader = NFCReader()
correct_uid = "83bd1fd0"
uid = nfc_reader.read_tag()
print "Found uid:", uid
if uid == correct_uid:
	print "Access granted"
else:
	print "Access denied"