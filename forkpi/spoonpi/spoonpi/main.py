from forkpi_db import ForkpiDB
from lockout_table import LockoutTable
from door_lock import DoorLock

from fingerprint.fingerprint_thread import FingerprintThread
from oled import OLED
from rfid.rfid_thread import RfidThread
from keypad.keypad_thread import KeypadThread

import time
from math import ceil
from threading import Timer

class SpoonPi:

    def __init__(self):
        print('Loading the ForkPi database...')
        self.db = ForkpiDB()
        
        print('Loading options...')
        attempt_limit = self.load_option('attempt_limit')
        lockout_time = self.load_option('lockout_time_minutes')
        self.lockout_table = LockoutTable(attempt_limit, lockout_time)
        self.keypad_timeout = self.load_option('keypad_timeout_seconds')
        self.max_transaction_time = self.load_option('max_transaction_time_seconds')
        self.lock_release_time = self.load_option('lock_release_time_seconds')

        print('Loading (F)ingerprint Scanner...')
        self.fingerprint_thread = FingerprintThread(lambda: ForkpiDB())
        print('Loading (O)LED...')
        self.led = OLED()
        print('Loading (R)FID Reader...')
        self.rfid_thread = RfidThread()
        print('Loading (K)eypad...')
        self.keypad_thread = KeypadThread()

        print('Connecting to (dummy) door lock...')
        self.door_lock = DoorLock()

        # maps RFID UIDs to incorrect streak and remaining lockout time
        self.transaction_timer = self.new_timer()

        # start polling for cards and fingers
        self.rfid_thread.start()
        self.fingerprint_thread.start()
        self.keypad_thread.start()

    def new_timer(self):
        # ends a pending transaction after a timer if the current self.factors are not enough to be authenticated
        # call the function `deny_then_end_transaction` after `max_transaction_time` seconds have elapsed
        return Timer(self.max_transaction_time, self.deny_then_end_transaction, kwargs={'reason':'insufficient credentials'})

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

        self.door_lock.unlock()
        self.led.clear_then_puts("Access\n granted")
        time.sleep(self.lock_release_time)
        self.door_lock.lock()

    def deny_access(self, reason, led_message="Access\n denied", *args, **kwargs):
        assert len(args) == 0
        print("> %s" % led_message.replace('\n ', ' '), kwargs)
        self.db.log_denied(reason=reason, **kwargs)
        self.led.clear_then_puts(led_message)
        time.sleep(0.5)

    def single_factor_authentication(self, *args, **kwargs):
        assert len(args) == 0
        assert len(kwargs.keys()) == 1

        is_authorized, names = self.db.authenticate(pin='', **kwargs)
        if is_authorized:
            self.allow_access(names=names, pin='', **kwargs)
        return is_authorized

    def two_factor_authentication(self, *args, **kwargs):
        assert len(args) == 0
        assert len(kwargs) == 2

        use_lockout_table = False
        if 'pin' in kwargs and 'rfid_uid' in kwargs:
            use_lockout_table = True

        if use_lockout_table:
            rfid_uid = kwargs['rfid_uid']
            is_locked_out, time_left = self.lockout_table.get_lockout(rfid_uid)
            if is_locked_out:
                self.deny_access(
                    reason="locked out",
                    led_message="Locked out\n for %sm" % time_left,
                    **kwargs
                )
                return False

        is_authorized, names = self.db.authenticate(**kwargs)
        if is_authorized:
            self.allow_access(names=names, **kwargs)
            if use_lockout_table:
                self.lockout_table.reset_streak(rfid_uid)
        else:
            self.deny_access(reason='invalid key pair', **kwargs)
            if use_lockout_table:
                self.lockout_table.failed_attempt(rfid_uid)
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
                
                self.lockout_table.update_timers()

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