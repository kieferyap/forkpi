"""
Module for the Sparkfun fingerprint scanner
Product Page: https://www.sparkfun.com/products/11792
Datasheet: http://cdn.sparkfun.com/datasheets/Sensors/Biometric/GT-511C3_datasheet_V1%201_20130411%5B4%5D.pdf
"""
import serial
import time

from .command_packet import CommandPacket
from .response_packet import ResponsePacket
from .data_packet import DataPacket

class FingerprintScanner(object):
    
    def __init__(self, debug=False, little_endian=False):
        self.debug = debug
        self.little_endian = little_endian
        try:
            self._serial = serial.Serial(port='/dev/ttyAMA0', baudrate=9600, timeout=None)
            self.open(timeout=0.1)

            if self.open(): # baud rate 9600 succeeded -> change to 115200
                self.change_baudrate(115200)
            else: # baud rate 9600 failed; maybe already set to 115200?
                self._serial.setBaudrate(115200)
                if self.open(): # baud rate 115200 succeeded
                    self._serial.flush()
                else: # baud rate 115200 failed
                    raise serial.SerialException()

        except serial.SerialException as e:
            raise Exception("Failed to connect to the fingerprint scanner!")

    def wait(self, seconds):
        time.sleep(seconds)

    def open(self, timeout=2):
        """
            Initializes communication with the scanner
        """
        self._send_command('Open')
        response = self._receive_response(timeout=timeout)
        if response is None:
            return False
        else:
            return response.ack

    def close(self):
        """
            Ends communication with the scanner
            Does not actually do anything (according to the datasheet)
        """
        response = self._run_command('Close')
        self._serial.close()
        return response.ack

    def set_backlight(self, on):
        """
            Turns on or off the LED backlight
            LED must be on to see fingerprints
            Parameter: True turns on the backlight, False turns it off
        """
        response = self._run_command('CmosLed', parameter = 1 if on else 0)
        return response.ack

    def backlight_on(self):
        return self.set_backlight(on=True)

    def backlight_off(self):
        return self.set_backlight(on=False)

    def change_baudrate(self, baudrate):
        """
            Changes the baud rate of the connection
            Parameter: 9600 - 115200
            Returns: True if success, False if invalid baud
        """
        if baudrate != self._serial.getBaudrate():
            if self._run_command('ChangeBaudrate', parameter=baudrate):
                if self.debug:
                    print('Changed baud rate from %s to %s' % (self._serial.getBaudrate(), baudrate))
                self._serial.setBaudrate(baudrate)
                return True
            else:
                return False
        else:
            return True

    def get_enroll_count(self):
        """
            Returns: The total number of enrolled fingerprints
        """
        response = self._run_command('GetEnrollCount')
        return response.parameter

    def is_enrolled(self, tid):
        """
            Parameter: The ID to be checked
            Returns: True if the ID is enrolled, False if not
        """
        response = self._run_command('CheckEnrolled', parameter=tid)
        return response.ack

    def find_free_tid(self):
        """
            Returns: The first free ID, -1 if db is full
        """
        for tid in range(200):
            if not self.is_enrolled(tid):
                return tid
        return -1

    def enroll_template(self, tries=3, delay=1.5):

        if self.start_enroll(tid=-1, tries=tries, delay=1.5):
            if self.debug:
                print('Enrolling template')
            template = self.complete_enroll(tid=-1, tries=tries)
            if self.debug and template:
                print('Enroll successful')
            return template

    def enroll_finger(self, tid=None, tries=3, delay=1.5):
        """
            The entire three-stage enrollment process
            Parameter: The ID to be enrolled (auto-searches for a free ID if not specified)
            Returns: The ID enrolled if successful, -1 if not
        """
        if self.debug:
            print('Place your finger on the scanner')

        if tid: # user specified an ID
            if self.is_enrolled(tid): # ID is already enrolled
                if self.debug:
                    print('ID %s is already enrolled' % tid)
                return -1
        else:
            tid = self.find_free_tid()
            if tid < 0: # database is full
                return -1

        if self.start_enroll(tid=tid, tries=tries, delay=1.5):
            if self.debug:
                print('Enrolling with id %s' % tid)
            if self.complete_enroll(tid, tries=tries):
                if self.debug:
                    print('Enroll successful')
                return tid

        return -1

    def start_enroll(self, tid, tries=3, delay=1.5):
        """
            First and second stage of enrollment process
            Parameter: The ID to be enrolled
            Returns: True if successful, False if not
        """
        if self._run_command('EnrollStart', parameter=tid): # Enroll start success
            if self._enroll(1, tries):
                self.wait(delay)
                if self._enroll(2, tries):
                    self.wait(delay)
                    return True
        return False

    def complete_enroll(self, tid, tries=3):
        """
            Third stage of enrollment process
            Parameter: The ID to be enrolled
            Returns: If tid >= 0, boolean success. If tid==-1, template data
        """
        if tid >= 0:
            ret = self._enroll(3, tries)
        else: # id == -1
            if self._capture_finger(tries):
                self._send_command('Enroll3')
                response = self._receive_response()
                ret = self._receive_data(data_length=498)

        self.backlight_off()
        return ret


    def _enroll(self, stage, tries=3):
        """
            Returns: True if enrollment successfully finished, False if not
        """
        if self.debug:
            print('Place your finger on the scanner')
        ret = False
        if self._capture_finger(tries):
            response = self._run_command('Enroll' + str(stage))
            ret = response.ack
            if ret and self.debug:
                print('Remove your finger from the scanner')
        if not ret and self.debug:
            print('Enroll failed')
        self.backlight_off()
        return ret

    def is_finger_pressed(self):
        """
            Returns: True if there is a finger on the scanner, False if not
        """
        response = self._run_command('IsPressFinger')
        return response.parameter == 0

    def delete_template(self, tid):
        """
            Deletes the specified template ID from the database
            Returns: True if successful, False if position invalid
        """
        response = self._run_command('DeleteID', parameter=tid)
        return response.ack

    def delete_all(self):
        """
            Deletes all template IDs from the database
            Returns: True if successful, False if db is empty
        """
        response = self._run_command('DeleteAll')
        return response.ack

    def verify_finger(self, tid, tries=3):
        """
            Checks the currently pressed finger against a specific ID
            Parameter: 0-199 (id number to be checked)
            Returns: True if match, False if not
        """
        if self._capture_finger(high_quality=False, tries=tries):
            response = self._run_command('Verify1_1', parameter=tid)
            return response.ack
        else:
            return False
    
    def identify_finger(self, tries=3):
        """
            Checks the currently pressed finger against all enrolled fingerprints
            Returns:
                0-199: Matched with this ID
                -1   : Failed to find a match
        """
        if self._capture_finger(high_quality=False, tries=tries):
            response = self._run_command('Identify1_N')
            return response.parameter if response.ack else -1
        else:
            return -1

    def verify_template(self, tid, template):
        if self._run_command('VerifyTemplate1_1', parameter=tid):
            self._send_data(data=template)
            response = self._receive_response()
            return response.ack
        return False

    def identify_template(self, template):
        if self._run_command('IdentifyTemplate1_N'):
            self._send_data(data=template)
            response = self._receive_response()
            if response.ack:
                return response.parameter
        return -1

    def _capture_finger(self, high_quality=True, tries=3):
        """
            Captures the currently pressed finger onto the onboard ram
            Parameters: Set high quality = True for enrollment, and False for verification/identification
                        tries - # of times to try capturing finger
            Returns: True if successful, False if no finger pressed
        """
        self.backlight_on()
        for i in range(tries):
            if self._run_command('CaptureFinger', parameter = 1 if high_quality else 0):
                return True
            elif i == tries - 1: # give up
                return False
            else: # try again
                self.wait(1.5)

    def make_template(self, tries=3):
        if self._capture_finger(high_quality=True, tries=tries):
            if self._run_command('MakeTemplate'):
                data = self._receive_data(498)
                return data
        return None

    def make_image(self, tries=3):
        if self._capture_finger(high_quality=True, tries=tries):
            if self._run_command('GetImage'):
                data = self._receive_data(52116)
                return data
        return None

    def make_raw_image(self):
        self.backlight_on()
        if self._run_command('GetRawImage'):
            data = self._receive_data(19200)
            self.backlight_off()
            return data
        self.backlight_off()
        return None

    def download_template(self, tid):
        """
            Downloads a template from the database
            Parameter: 0-199 ID number
            Returns: the template requested (498 bytes)
        """
        if self._run_command('GetTemplate', parameter=tid):
            data = self._receive_data(498)
            return data
        return None

    def upload_template(self, tid, template):
        """
            Uploads a template to the database
            Parameter: 0-199 ID number, template (498 bytes)
            Returns: True if successful, False if not
        """
        # the addition of 0x00ff0000 below is so that duplication check is not performed
        if self._run_command('SetTemplate', parameter=0x00ff0000 + tid):
            self._send_data(data=template)
            response = self._receive_response()
            return response.ack
        return False

    def _run_command(self, *args, **kwargs):
        self._send_command(*args, **kwargs)
        response = self._receive_response()
        return response

    def _send_command(self, *args, **kwargs):
        command = CommandPacket(*args, **kwargs)
        if self.debug:
            print('\nCommand:', command.name)
            print('sent:', command.serialize_bytes(little_endian=self.little_endian))
        self._serial.write(bytes(command))

    def _receive_response(self, timeout=None):
        self._serial.setTimeout(timeout)
        bytes_ = self._serial.read(size=12)

        if len(bytes_) < 12:
            if self.debug:
                print('read:')
            return None
        
        response = ResponsePacket(bytes_)
        if self.debug:
            print('read:', response.serialize_bytes(little_endian=self.little_endian))
            if not response.ack:
                print('ERROR:', response.error)
        return response

    def _send_data(self, data):
        packet = DataPacket(data=data)
        if self.debug:
            print('data:', packet.serialize_bytes(little_endian=self.little_endian))
            print('dlen:', len(packet.data))
        self._serial.write(bytes(packet))

    def _receive_data(self, data_length, timeout=10):
        packet_length = data_length + 6 # the +6 comes from the other non-data parts of the packet

        self._serial.setTimeout(timeout)
        bytes_ = self._serial.read(size=packet_length)
        assert self._serial.inWaiting() == 0 # that should be all

        if len(bytes_) < packet_length:
            return None

        packet = DataPacket(bytes_=bytes_)
        if self.debug:
            print('data:', packet.serialize_bytes(little_endian=self.little_endian))
            print('dlen:', len(packet.data))
        return packet.data


if __name__ == '__main__':
    fps = FingerprintScanner(debug=True)
    # fps.backlight_on()
    # for i in range(10):
    #     print(fps.is_finger_pressed())
    #     time.sleep(1)
    # fps.backlight_off()

    # Enrollment
    # enroll_id = fps.enroll_finger(tid=None, tries=3)
    template = fps.enroll_template(tries=3)


    # Identification
    # identify_iid = fps.identify_finger(tries=3)
    # if identify_id >= 0:
    #     print('Match with id %s' % identify_id)
    # else:
    #    print('No match found')

    # for i in range(5):
    #     template = fps.download_template(tid=i)

    # fps.delete_all()
    # template = fps.make_template(tries=3)
    # fps.upload_template(tid=0, template=template)
    # print fps.verify_template(tid=4, template=template)

    # print fps.verify_finger(tid=4, tries=3)

    # fps.make_image()
    
    # from test_raw import SaveImage
    # SaveImage('fingerprint1.raw', fps.make_raw_image())
    # print(fps.make_raw_image())

    fps.close()
    print()