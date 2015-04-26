"""
Module for the Sparkfun fingerprint scanner GT-511C3
Product Page : https://www.sparkfun.com/products/11792
Datasheet : http://cdn.sparkfun.com/datasheets/Sensors/Biometric/GT-511C3_datasheet_V1%201_20130411%5B4%5D.pdf
"""
import serial
import time

from .command_packet import CommandPacket
from .response_packet import ResponsePacket
from .data_packet import DataPacket

class FingerprintScanner(object):
    """
    Encapsulates communication with the Sparkfun fingerprint scanner.
    Port : `/dev/ttyAMA0`
    Baudrate : 9600 (default), 115200 (to send/receive data packets)

    To use
    ------
    Connect a JST-SH pigtail to the FPS.
    Connect UART_TX to GPIO pin 10 (RX).
            UART_RX to GPIO pin  8 (TX).
            GND to a ground pin.
            Vin to a 5V pin (3.3V causes finger detection issues).

    Major functions
    ---------------
        High-accuracy and high-speed fingerprint identification
        1:1 verification, 1:N identification
        Downloading fingerprint images from the device
        Reading & writing fingerprint templates from/to the device

    Attributes
    ----------
    debug : bool
        True to print nack errors and packets sent to / received from FPS, False to print nothing.
    is_little_endian : bool
        True to print packets in little endian byte order, False for big endian.

    """
    
    def __init__(self, debug=False, is_little_endian=False):
        """
        Parameters
        ----------
        debug : bool, optional
            Set to True to print nack errors and packets sent to / received from FPS.
            Defaults to False (do not print).
        is_little_endian : bool, optional
            True to print packets in little endian byte order, False for big endian.
            Defaults to False (print in big endian).

        Raises
        ------
        SerialException
            If connection to the FPS failed.

        """
        self.debug = debug
        self.is_little_endian = is_little_endian
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

    def _wait(self, seconds):
        time.sleep(seconds)

    def open(self, timeout=2):
        """
        Initializes communication with the scanner.
        This is automatically called upon construction.

        Parameters
        ----------
        timeout : int, optional
            Number of seconds to wait for response before returning, defaults to 2s.

        Returns
        -------
        bool
            True if ack, False if nack or timeout.

        """
        self._send_command('Open')
        response = self._receive_response(timeout=timeout)
        if response is None:
            return False
        else:
            return response.ack

    def close(self):
        """
        Ends communication with the scanner.
        Does not actually do anything (according to the datasheet).

        Returns
        -------
        bool
            True if ack, False if nack.
        
        """
        response = self._run_command('Close')
        self._serial.close()
        return response.ack

    def set_backlight(self, on):
        """
        Turns the LED backlight on or off.

        Parameters
        ----------
        on : bool
            True turns on the backlight, False turns it off.

        Returns
        -------
        bool
            True if ack, False if nack.

        """
        response = self._run_command('CmosLed', parameter = 1 if on else 0)
        return response.ack

    def backlight_on(self):
        """
        Turns the LED backlight on.

        Parameters
        ----------
        on : bool
            True turns on the backlight, False turns it off.

        Returns
        -------
        bool
            True if ack, False if nack.

        """
        return self.set_backlight(on=True)

    def backlight_off(self):
        """
        Turns the LED backlight off.

        Parameters
        ----------
        on : bool
            True turns on the backlight, False turns it off.

        Returns
        -------
        bool
            True if ack, False if nack.

        """
        return self.set_backlight(on=False)

    def change_baudrate(self, baudrate):
        """
        Changes the baudrate of the serial connection.

        Parameters
        ----------
        baudrate : int
            Baudrate. Only 9600 or 115200 is recommended, but can be any integer in that range.
        
        Returns
        -------
        bool
            True if success, False if invalid baud.

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
        Returns
        -------
        int
            The total number of enrolled fingerprints.

        """
        response = self._run_command('GetEnrollCount')
        return response.parameter

    def is_enrolled(self, tid):
        """
        Parameters
        ----------
        tid : int
            The template ID to be checked, must be from 0-199.

        Returns
        -------
        bool
            True if the ID is enrolled, False if not (or invalid tid).

        """
        response = self._run_command('CheckEnrolled', parameter=tid)
        return response.ack

    def find_free_tid(self):
        """
        From 0 to 199, finds the first free (unenrolled) template ID.

        Returns
        -------
        int
            The first free ID, -1 if db is full.

        """
        for tid in range(200):
            if not self.is_enrolled(tid):
                return tid
        return -1

    def enroll_template(self, tries=3, delay=1.5):
        """
        Three-stage enrollment process.
        For each stage, the light is turned on, a finger is captured, and the light is turned off.
        At the end of stage 3, the three fingerprints are merged into one template, and returned.

        Notes
        -----
            You should present the same finger for all three stages.
            You should remove and re-place your finger for all three stages.
            This is to improve the quality of the merged template.

        Parameters
        ----------
        tries : int, optional
            For each stage, number of times to try capturing a finger, defaults to 3.
            If at any stage, the FPS failed to capture a finger for `tries` times, the enrollment is aborted.
        delay : float, optional
            Number of seconds to wait (do nothing) between stages, defaults to 1.5.
            The user should remove and re-place his/her finger during this time.

        Returns
        -------
        bytes (498)
            The merged template, None if enroll failed.
            Causes for failure: Exceeded number of tries.

        """
        if self.start_enroll(tid=-1, tries=tries, delay=1.5):
            if self.debug:
                print('Enrolling template')
            template = self.complete_enroll(tid=-1, tries=tries)
            if self.debug and template:
                print('Enroll successful')
            return template

    def enroll_finger(self, tid=None, tries=3, delay=1.5):
        """
        Three-stage enrollment process.
        For each stage, the light is turned on, a finger is captured, and the light is turned off.
        At the end of stage 3, the three fingerprints are merged into one template.
        The template is saved to the internal database.

        Notes
        -----
            You should present the same finger for all three stages.
            You should remove and re-place your finger for all three stages.
            This is to improve the quality of the merged template.

        Parameters
        ----------
        tid : int, optional
            The template ID to store the enrolled finger in, defaults to None, must be from 0-199.
            If None, tid is set to the first free template ID.
        tries : int, optional
            For each stage, number of times to try capturing a finger, defaults to 3.
            If at any stage, the FPS failed to capture a finger for `tries` times, the enrollment is aborted.
        delay : float, optional
            Number of seconds to wait (do nothing) between stages, defaults to 1.5.
            The user should remove and re-place his/her finger during this time.

        Returns
        -------
        int
            The template ID of the newly enrolled fingerprint if successful, -1 if failed.
            Causes for failure:
                specified tid is taken or invalid
                db is full (if tid is None)
                exceeded `tries`

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
        First and second stage of enrollment process.

        Parameters
        ----------
        tid : int
            The template ID to be enrolled, must be from -1 to 199.
            Set to -1 to return the template upon completion later (instead of saving to db).
        tries : int, optional
            For each stage, number of times to try capturing a finger, defaults to 3.
            If at any stage, the FPS failed to capture a finger for `tries` times, the enrollment is aborted.
        delay : float, optional
            Number of seconds to wait (do nothing) after each stage, defaults to 1.5.
            The user should remove and re-place his/her finger during this time.

        Returns
        -------
        bool
            True if successfully captured two fingers, False if not.

        """
        if self._run_command('EnrollStart', parameter=tid):
            if self._enroll(1, tries):
                self._wait(delay)
                if self._enroll(2, tries):
                    self._wait(delay)
                    return True
        return False

    def complete_enroll(self, tid, tries=3):
        """
        Third stage of enrollment process.

        Parameters
        ----------
        tid : int
            The template ID to be enrolled.
            This must be the same as the tid used in `start_enroll`.
        tries : int, optional
            Number of times to try capturing a finger, defaults to 3.

        Returns
        -------
        bytes (if tid == -1)
            The merged template, None if failed.
        bool (if tid >= 0)
            True if successfully saved to db, False if failed.

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
        Parameters
        ----------
        stage : int
            Defines what command to send to the FPS, must be from 1 to 3 only.
        tries : int, optional
            Number of times to try capturing a finger, defaults to 3.

        Returns
        -------
        bool
            True if successful, False if not.

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
        Notes
        -----
        LED backlight must be turned on to detect fingerprints.

        Returns
        -------
        bool
            True if there is a finger on the scanner, False if not.

        """
        response = self._run_command('IsPressFinger')
        return response.parameter == 0

    def delete_template(self, tid):
        """
        Parameters
        ----------
        tid : int
            The template ID to be deleted from the database, must be from 0-199.

        Returns
        -------
        bool
            True if successful, False if tid is invalid.

        """
        response = self._run_command('DeleteID', parameter=tid)
        return response.ack

    def delete_all(self):
        """
        Deletes all templates from the database.

        Returns
        -------
        bool
            True if successful, False if db is empty.

        """
        response = self._run_command('DeleteAll')
        return response.ack

    def verify_finger(self, tid, tries=3):
        """
        Captures a finger and verifies it against a specific template in the db.

        Parameters
        ----------
        tid : int
            The template ID to be verified against, must be from 0-199.
        tries : int, optional
            Number of times to try capturing a finger, defaults to 3.

        Returns
        -------
        bool
            True if fingerprints match, False if they don't (or capture failed).

        """
        if self._capture_finger(high_quality=False, tries=tries):
            response = self._run_command('Verify1_1', parameter=tid)
            return response.ack
        else:
            return False
    
    def identify_finger(self, tries=3):
        """
        Captures a finger and identifies it among all templates in the db.

        Parameters
        ----------
        tries : int, optional
            Number of times to try capturing a finger, defaults to 3.

        Returns
        -------
        int
            ID of the first template that matched, -1 if no match (or capture failed).

        """
        if self._capture_finger(high_quality=False, tries=tries):
            response = self._run_command('Identify1_N')
            return response.parameter if response.ack else -1
        else:
            return -1

    def verify_template(self, tid, template):
        """
        Verifies a given template against a specific template in the db.

        Parameters
        ----------
        tid : int
            The template ID to be verified against, must be from 0-199.
        template : bytes (498)
            The given template to be verified.

        Returns
        -------
        bool
            True if the templates match, False if they don't.

        """
        if self._run_command('VerifyTemplate1_1', parameter=tid):
            self._send_data(data=template)
            response = self._receive_response()
            return response.ack
        return False

    def identify_template(self, template):
        """
        Identifies a given template among all templates in the db.

        Parameters
        ----------
        template : bytes (498)
            The given template to be identified.

        Returns
        -------
        int
            ID of the first db template that matched, -1 if no match.

        """
        if self._run_command('IdentifyTemplate1_N'):
            self._send_data(data=template)
            response = self._receive_response()
            if response.ack:
                return response.parameter
        return -1

    def make_template(self, tries=3):
        """
        Captures a finger, then returns the template generated.

        Parameters
        ----------
        tries : int, optional
            Number of times to try capturing a finger, defaults to 3.

        Returns
        -------
        bytes (498)
            The template generated, None if capture failed.

        """
        if self._capture_finger(high_quality=True, tries=tries):
            if self._run_command('MakeTemplate'):
                data = self._receive_data(498)
                return data
        return None

    def make_image(self, tries=3):
        """
        Captures a finger, then returns the image generated.

        Parameters
        ----------
        tries : int, optional
            Number of times to try capturing a finger, defaults to 3.

        Returns
        -------
        bytes (52116)
            The image generated, None if capture failed.
            The image size is 258x202.

        """
        if self._capture_finger(high_quality=True, tries=tries):
            if self._run_command('GetImage'):
                data = self._receive_data(52116)
                return data
        return None

    def make_raw_image(self):
        """
        Scans the optical sensor, then returns the raw image generated.
        Does not check if a fingerprint is on the sensor.

        Returns
        -------
        bytes (19200)
            The raw image generated.
            The image is 160x120 QVGA.

        """
        self.backlight_on()
        if self._run_command('GetRawImage'):
            data = self._receive_data(19200)
            self.backlight_off()
            return data
        self.backlight_off()
        return None

    def download_template(self, tid):
        """
        Downloads a template from the fingerprint database.

        Parameters
        ----------
        tid : int
            The template ID to be downloaded, must be from 0-199.

        Returns
        -------
        bytes (498)
            The template requested, None if invalid position or tid is not used.
        
        """
        if self._run_command('GetTemplate', parameter=tid):
            data = self._receive_data(498)
            return data
        return None

    def upload_template(self, tid, template):
        """
        Uploads a template to the fingerprint database.

        Parameters
        ----------
        tid : int
            The template ID to be uploaded to, must be from 0-199.
        template : bytes (498)
            The template to be uploaded.

        Returns
        -------
        bool
            True if successful, False if tid is invalid.
        
        """
        # the addition of 0x00ff0000 below is so that duplication check is not performed
        if self._run_command('SetTemplate', parameter=0x00ff0000 + tid):
            self._send_data(data=template)
            response = self._receive_response()
            return response.ack
        return False

    def _capture_finger(self, high_quality=True, tries=3):
        """
        Captures the currently pressed finger onto the on-board memory.

        Parameters
        ----------
        high_quality : bool
            Set to True for enrollment, False for verification/identification.
        tries : int, optional
            Number of times to try capturing a finger, defaults to 3.

        Returns
        -------
        bool
            True if successful, False if no finger detected for `tries` times.
        
        """
        self.backlight_on()
        for i in range(tries):
            if self._run_command('CaptureFinger', parameter = 1 if high_quality else 0):
                return True
            elif i == tries - 1: # give up
                return False
            else: # try again
                self._wait(1.5)

    def _run_command(self, *args, **kwargs):
        """
        Sends a command packet then returns the response.

        Returns
        -------
        ResponsePacket
            The response received.
        
        """
        self._send_command(*args, **kwargs)
        response = self._receive_response()
        return response

    def _send_command(self, *args, **kwargs):
        """
        Creates a command packet from the arguments, then writes it to serial.

        Parameters
        ----------
        *args
        **kwargs
            Arguments to be passed to the CommandPacket constructor.

        Returns
        -------
        None
        
        """
        command = CommandPacket(*args, **kwargs)
        if self.debug:
            print('\nCommand:', command.name)
            print('sent:', command.serialize_bytes(is_little_endian=self.is_little_endian))
        self._serial.write(bytes(command))

    def _receive_response(self, timeout=None):
        """
        Reads 12 bytes from serial, then returns it as a ResponsePacket.

        Parameters
        ----------
        timeout : int, optional
            Number of seconds to wait for response, defaults to None.
            If None, do blocking read.

        Returns
        -------
        ResponsePacket
            The response received from the FPS, None if read timed out.
        
        """
        self._serial.setTimeout(timeout)
        bytes_ = self._serial.read(size=12)

        if len(bytes_) < 12:
            if self.debug:
                print('read:')
            return None
        
        response = ResponsePacket(bytes_)
        if self.debug:
            print('read:', response.serialize_bytes(is_little_endian=self.is_little_endian))
            if not response.ack:
                print('ERROR:', response.error)
        return response

    def _send_data(self, data):
        """
        Creates a data packet from the argument, then writes it to serial.

        Parameters
        ----------
        data : bytes
            Data of the data packet.

        Returns
        -------
        None
        
        """
        packet = DataPacket(data=data)
        if self.debug:
            print('data:', packet.serialize_bytes(is_little_endian=self.is_little_endian))
            print('dlen:', len(packet.data))
        self._serial.write(bytes(packet))

    def _receive_data(self, data_length, timeout=10):
        """
        Receives (`data_length` + 6) bytes from serial, then returns just the data.

        Parameters
        ----------
        data_length : int
            Length of the data expected.
        timeout : int, optional
            Number of seconds to wait for response, defaults to 10s.
            If None, do blocking read (wait forever).

        Returns
        -------
        bytes
            `data_length` bytes of data (not the entire packet) received.
        
        """
        packet_length = data_length + 6 # the +6 comes from the other non-data parts of the packet

        self._serial.setTimeout(timeout)
        bytes_ = self._serial.read(size=packet_length)

        if len(bytes_) < packet_length:
            return None

        packet = DataPacket(bytes_=bytes_)
        if self.debug:
            print('data:', packet.serialize_bytes(is_little_endian=self.is_little_endian))
            print('dlen:', len(packet.data))
        return packet.data


if __name__ == '__main__':
    fps = FingerprintScanner(debug=False)
    # fps.backlight_on()
    # for i in range(10):
    #     print(fps.is_finger_pressed())
    #     time.sleep(1)
    # fps.backlight_off()

    # Enrollment
    # enroll_id = fps.enroll_finger(tid=None, tries=3)
    # template = fps.enroll_template(tries=3)
    # fps = FingerprintScanner(debug=True)
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