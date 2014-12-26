from nfc_reader import  NFCReader

if __name__ == '__main__':
    print "Please swipe an RFID tag"
    uid = NFCReader().read_tag()
    print "Found uid:", uid