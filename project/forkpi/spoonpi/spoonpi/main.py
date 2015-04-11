from forkpi_db import ForkpiDB

from fingerprint.fingerprint_thread import FingerprintThread
from oled import OLED
from rfid.rfid_thread import RfidThread
from keypad.keypad_thread import KeypadThread

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
        self.keypad_thread = KeypadThread()

        # maps RFID UIDs to incorrect streak and remaining lockout time
        self.lockout_table = list()
        # ends a pending transaction after a timer if the current self.factors are not enough to be authenticated
        self.new_timer = lambda: Timer(3, self.deny_then_end_transaction, kwargs={'reason':'insufficient credentials'})
        self.transaction_timer = self.new_timer()
        # start polling for cards and fingers
        self.rfid_thread.start()
        self.fingerprint_thread.start()
        self.keypad_thread.start()

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
        print("> Allowed %s" % names)
        self.db.log_allowed(names=names, **kwargs)
        self.led.clear_then_puts("Access\n granted")
        time.sleep(2)

    def deny_access(self, reason, led_message="Access\n denied", *args, **kwargs):
        assert len(args) == 0
        print("> %s" % led_message.replace('\n ', ' '), kwargs)
        self.db.log_denied(reason=reason, **kwargs)
        self.led.clear_then_puts(led_message)
        time.sleep(0.5)

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

        is_authorized, names = self.db.authenticate(pin='', **kwargs)
        if is_authorized:
            self.allow_access(names=names, pin='', **kwargs)
        return is_authorized

    def two_factor_authentication(self, *args, **kwargs):
        assert len(args) == 0
        assert len(kwargs.keys()) == 2

        is_authorized, names = self.db.authenticate(**kwargs)
        if is_authorized:
            self.allow_access(names=names, **kwargs)
        else:
            self.deny_access(reason='invalid keypair', **kwargs)
        return is_authorized

    def pin_authentication(self):
        '''
        Returns (pin, timeout) where
          pin = the pin entered (string)
          timeout = whether the keypad timed out (boolean)
        '''
        pin = ''
        self.led.clear_then_puts("Enter PIN:\n")
        # First key that triggered this pin authentication
        key = self.keypad_thread.get_key()

        while True:
            if key is None: # timed out!
                return pin, True
            elif key.isdigit():
                pin += str(key)
                self.led.puts('*')
            elif key == '*': # backspace
                pin = pin[:-1]
                self.led.puts('\b')
            elif key == '#': # enter
                return pin, False
            key = self.keypad_thread.getch(timeout=self.keypad_timeout)

    def start_transaction_timer(self):
        self.transaction_timer = self.new_timer()
        self.transaction_timer.start()

    def stop_transaction_timer(self):
        self.transaction_timer.cancel()

    def deny_then_end_transaction(self, reason):
        self.deny_access(reason=reason, **self.factors)
        self.end_transaction()

    def end_transaction(self):
        self.is_transacting = False
        self.stop_transaction_timer()

    def new_transaction(self):
        self.is_transacting = True

        self.factors = dict()

        self.led.clear_then_puts("Swipe, scan,\nor push key")

        self.rfid_thread.start_polling()
        self.fingerprint_thread.start_polling()
        self.keypad_thread.start_polling()

        while self.is_transacting:

            if self.rfid_thread.tag_swiped:
                self.stop_transaction_timer()

                self.rfid_thread.stop_polling()
                self.factors['rfid_uid'] = self.rfid_thread.get_rfid_uid()

                if self.single_factor_authentication(rfid_uid=self.factors['rfid_uid']):
                    # single factor succeeded; end transaction
                    self.end_transaction()
                elif len(self.factors) == 1:
                    # single factor failed; wait for another factor
                    self.led.clear_then_puts("RFID tag\n swiped!")
                    self.start_transaction_timer()
                else: # len(self.factors) == 2
                    self.two_factor_authentication(**self.factors)
                    self.end_transaction()

            elif self.fingerprint_thread.finger_scanned:
                self.stop_transaction_timer()

                self.fingerprint_thread.stop_polling()
                self.factors['fingerprint_matches'] = self.fingerprint_thread.get_matches()

                if self.single_factor_authentication(fingerprint_matches=self.factors['fingerprint_matches']):
                    # single factor succeeded; end transaction
                    self.end_transaction()
                elif len(self.factors) == 1:
                    # single factor failed; wait for another factor
                    self.led.clear_then_puts("Finger\n scanned!")
                    self.start_transaction_timer()
                else: # len(self.factors) == 2
                    self.two_factor_authentication(**self.factors)
                    self.end_transaction()

            elif self.keypad_thread.key_pressed:
                self.stop_transaction_timer()

                self.keypad_thread.stop_polling()
                self.factors['pin'], timed_out = self.pin_authentication()

                if timed_out:
                    self.deny_then_end_transaction(reason='keypad timeout')
                # pin was entered correctly
                elif len(self.factors) == 1:
                    # wait for another factor
                    self.led.clear_then_puts("PIN\n entered!")
                    self.start_transaction_timer()
                else: # len(self.factors) == 2
                    self.stop_transaction_timer()
                    self.two_factor_authentication(**self.factors)
                    self.end_transaction()

if __name__ == '__main__':
    spoonpi = SpoonPi()
    while True:
        print('-------------New Transaction-------------')
        spoonpi.new_transaction()
        print('-------------End Transaction-------------')