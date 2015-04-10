from forkpi_db import ForkpiDB

from fingerprint.fingerprint_thread import FingerprintThread
from oled import OLED
from rfid.rfid_thread import RfidThread
from keypad import Keypad

import time
from math import ceil
from threading import Timer

class SpoonPi:
    # LOCKOUT TABLE columns [rfid_uid, incorrect_streak, lockout]
    COL_UID, COL_STREAK, COL_TIME_LEFT = list(range(3))

    def __init__(self):
        print('Loading the ForkPi database...')
        self.db = ForkpiDB()
        print('Loading options...')
        self.attempt_limit = self.load_option('attempt_limit')
        self.lockout_time = self.load_option('lockout_time_minutes') * 60
        self.keypad_timeout = self.load_option('keypad_timeout_seconds')

        print('Loading Fingerprint Scanner...')
        self.fingerprint_thread = FingerprintThread(lambda: ForkpiDB())
        print('Loading OLED...')
        self.led = OLED()
        print('Loading RFID Reader...')
        self.rfid_thread = RfidThread()
        print('Loading Keypad...')
        self.keypad = Keypad()
        # maps RFID UIDs to incorrect streak and remaining lockout time
        self.lockout_table = list()
        # ends a pending transaction after a timer if the current factors are not enough to be authenticated
        self.transaction_timer = None
        # start polling for cards and fingers
        self.rfid_thread.start()
        self.fingerprint_thread.start()

    def load_option(self, name):
        value, default = self.db.fetch_option(name)
        if value.isdigit() and value != default:
            print('  custom : {} = {}'.format(name, value))
            return int(value)
        else:
            print('  default: {} = {}'.format(name, default))
            return int(default)

    def allow_access(self, names, *args, **kwargs):
        assert len(args) == 0
        if 'pin' in kwargs.keys():
            # convert pin to asterisks so pin is not exposed in the logs
            kwargs['pin'] = '*' * len(kwargs['pin'])
        names = ', '.join(names)
        print("Allowed %s" % names)
        self.db.log_allowed(names=names, **kwargs)
        self.led.clear_display()
        self.led.puts("Access\ngranted")

    def deny_access(self, reason, led_message="Access\ndenied", *args, **kwargs):
        assert len(args) == 0
        print(led_message.replace('\n', ' '))
        self.db.log_denied(reason=reason, **kwargs)
        self.led.clear_display()
        self.led.puts(led_message)

    def pin_authentication(self):
        '''
        Returns (pin, timeout) where
          pin = the pin entered (string)
          timeout = whether the keypad timed out (boolean)
        '''
        pin = ''
        self.led.clear_display()
        self.led.puts("Enter PIN:\n")

        while True:
            key = self.keypad.getch(timeout=self.keypad_timeout)
            if key == Keypad.TIMEOUT:
                return pin, True
            elif key.isdigit():
                pin += str(key)
                self.led.puts('*')
            elif key == '*': # backspace
                pin = pin[:-1]
                self.led.puts('\b')
            elif key == '#': # enter
                return pin, False

    def find_lockout_row(self, rfid_uid):
        lockout_row = None
        for row in self.lockout_table:
            if row[0] == rfid_uid:
                lockout_row = row
        if lockout_row is None:
            lockout_row = [rfid_uid, 0, 0]
            self.lockout_table.append(lockout_row)
        return lockout_row

    def update_lockout_timers(self, time_elapsed):
        for row in self.lockout_table:
            lockout_time_left = row[SpoonPi.COL_TIME_LEFT]
            was_locked_out = (lockout_time_left > 0)
            row[SpoonPi.COL_TIME_LEFT] = max(0, lockout_time_left - time_elapsed)
            if was_locked_out and row[SpoonPi.COL_TIME_LEFT] == 0:
                row[SpoonPi.COL_STREAK] = 0

    def single_factor_authentication(self, *args, **kwargs):
        assert len(args) == 0
        assert len(kwargs.keys()) == 1

        is_authorized, names = self.db.authorize(pin='', **kwargs)
        if is_authorized:
            self.allow_access(names=names, pin='', **kwargs)
        return is_authorized

    def two_factor_authentication(self, *args, **kwargs):
        assert len(args) == 0
        assert len(kwargs.keys()) == 2

        is_authorized, names = self.db.authorize(**kwargs)
        if is_authorized:
            self.allow_access(names=names, **kwargs)
        else:
            self.deny_access(names=names, **kwargs)
        return is_authorized

    def start_transaction_timer(self):
        self.transaction_timer = Timer(3, self.end_transaction)
        self.transaction_timer.start()

    def stop_transaction_timer(self):
        self.transaction_timer.cancel()

    def end_transaction(self):
        self.is_transacting = False

    def new_transaction(self):
        self.is_transacting = True

        factors = dict()

        self.led.clear_display()
        self.led.puts("Swipe RFID\nor Finger")

        self.rfid_thread.reset()
        self.fingerprint_thread.reset()

        self.rfid_thread.start_polling()
        self.fingerprint_thread.start_polling()

        while self.is_transacting:

            if self.rfid_thread.is_found:
                self.led.clear_display()
                self.led.puts("RFID\nswiped!")

                factors['rfid_uid'] = self.rfid_thread.rfid_uid
                # we don't want to detect the same card again, and we want rfid to stop polling for new cards
                self.rfid_thread.reset()
                if len(factors) == 1:
                    if self.single_factor_authentication(**factors):
                        # if single factor succeeded, end transaction
                        self.end_transaction()
                    else:
                        # single factor failed; wait 3s for another factor
                        # if another factor is not entered by then, deny and proceed to next transaction
                        self.start_transaction_timer()
                else: # len(factors) == 2
                    self.stop_transaction_timer()
                    self.two_factor_authentication(**factors)
                    self.end_transaction()

            elif self.fingerprint_thread.is_found:
                self.led.clear_display()
                self.led.puts("Finger\nscanned!")

                factors['fingerprint_matches'] = self.fingerprint_thread.matches
                # we don't want to detect the same finger again, and we want to stop polling for new fingers
                self.fingerprint_thread.reset()
                if len(factors) == 1:
                    if self.single_factor_authentication(**factors):
                        # if single factor succeeded, end transaction
                        self.end_transaction()
                    else:
                        # single factor failed; wait 3s for another factor
                        # if another factor is not entered by then, deny and proceed to next transaction
                        self.start_transaction_timer()
                else: # len(factors) == 2
                    self.stop_transaction_timer()
                    self.two_factor_authentication(**factors)
                    self.end_transaction()

                # else:
                #     self.rfid_thread.stop_polling()
                #     pin, timeout = self.pin_authentication()
                #     if not timeout:
                #         self.two_factor_authentication(fingerprint_matches=fingerprint_matches, pin=pin)
        time.sleep(1.5)


    def run(self):
        """
        Flow:
            Ask for RFID or Fingerprint
            If the RFID or Fingerprint is authorized, access granted.
            Else, ask for PIN, then check for auth.
            Notice that there's no three-factor auth.
            Because fuck that shit.
        """
        # Start polling for fingerprints and rfids
        self.fingerprint_thread.start()
        self.rfid_thread.start()

        self.next_transaction()





        # Some initializations
        is_ask_for_pin = False
        is_resetting = False
        finger_id = 0
        rfid_uid = 0

        # LED initializations
        self.led.clear_display()
        self.led.puts("Swipe RFID\nor Finger")

        while True:

            # If the RFID thread goes: "An RFID card has been swiped!"
            if rfid_thread.is_found:
                # Ask the fingerprint thread to stop polling
                fingerprint_thread.is_polling = False
                # Fetch the UID
                rfid_uid = rfid_thread.rfid_uid
                # Do single-factor RFID authentication check:
                is_authorized, names = self.db.authorize(pin='', rfid_uid=rfid_uid)

                # If authorized, allow entry. else: Set the ask_for_pin flag = True
                if is_authorized:
                    self.allow_access(names=names, pin='', rfid_uid=rfid_uid)
                    is_resetting = True
                else:
                    is_ask_for_pin = True

            # If the Fingerprint thread goes: "A new fingerprint has been found!"
            if fingerprint_thread.is_found:
                # Ask the RFID thread to stop polling
                rfid_thread.is_polling = False
                # Fetch the IDs of the keypairs whose prints match the found print
                fingerprint_matches = fingerprint_thread.matches
                # Do single-factor fingerprint authentication check
                is_authorized, names = self.db.authorize(pin='', fingerprint_matches=fingerprint_matches)

                if is_authorized:
                    self.allow_access(names=names, pin='', used_fingerprint=True)
                    is_resetting = True
                # Else, ask for PIN.
                else:
                    is_ask_for_pin = True

            # If somebody's asking for the PIN
            if is_ask_for_pin:

                # Grab the pin and do an authorization check
                pin, timed_out = self.pin_authentication()

                # TODO: Incorporate fingerprint in the authorization
                is_authorized, names = self.db.authorize(pin=pin, rfid_uid=rfid_uid)

                # If authorized, Allow entry. Else: Access denied.
                if is_authorized:
                    self.allow_access(names=names, pin=pin, rfid_uid=rfid_uid)
                else:
                    self.deny_access(reason="wrong pin", pin=pin, rfid_uid=rfid_uid)
                    is_authenticated = False
            
                # Set reset flag to true
                is_resetting = True

            if is_resetting:
                time.sleep(1.5)
                
                # Poll for the next RFID and Fingerprint
                fingerprint_thread.is_polling = True
                fingerprint_thread.is_found = False
                rfid_thread.is_polling = True
                rfid_thread.is_found = False
                is_ask_for_pin = False

                # LED: "Swipe RFID or Finger"
                self.led.clear_display()
                self.led.puts("Swipe RFID\nor Finger")

                # Set flag to false
                is_resetting = False


if __name__ == '__main__':
    spoonpi = SpoonPi()
    while True:
        spoonpi.new_transaction()