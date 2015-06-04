import threading
from .keypad import Keypad

class KeypadThread(threading.Thread):

    def __init__(self):
        super(KeypadThread, self).__init__()
        self.keypad = Keypad()
        self.key = '' # The key pressed

    def start_polling(self):
        self.is_polling = True
        self.key_pressed = False # True if a new key has been pressed

    def stop_polling(self):
        self.is_polling = False

    def run(self):
        self.start_polling()
        while True:
            while self.is_polling and not self.key_pressed:
                self.key = self.keypad.getch(timeout=None)
                self._print('Key was pressed!')
                self.key_pressed = True

    def _print(self, *args):
        print('  [KeypadThread]', *args)

    def get_key(self):
        self.key_pressed = False
        return self.key

    def getch(self, timeout):
        return self.keypad.getch(timeout)