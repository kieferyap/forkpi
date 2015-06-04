import gaugette.ssd1306
import time
import sys
import re

class OLED:
    line_height = 16
    line_size = 2
    
    def __init__(self, reset_pin=6, dc_pin=11, n_lines=2):
        self.led = gaugette.ssd1306.SSD1306(reset_pin=reset_pin, dc_pin=dc_pin)
        self.led.begin()
        self.n_lines = n_lines
        self.lines = [""]
        self.clear_display()

    def apply_backspaces(self, s):
        char_backspace = re.compile("[^\b]\b") # Don't use a raw string here
        any_backspaces = re.compile("\b+") # or here
        while True:
            t = char_backspace.sub("", s)
            if len(s) == len(t):
                # remove any backspaces which may start a line
                return any_backspaces.sub("", t)
            s = t
    
    def puts(self, text):
        # different from self.clear_display() !
        self.led.clear_display()
        # split new text into separate lines
        new_text = text.split('\n')
        # append first line of new text to last line of existing text
        self.lines[-1] += new_text[0]
        # add new lines of new text
        self.lines.extend(new_text[1:])
        # limit number of lines to n_lines
        self.lines = self.lines[-self.n_lines:]
        
        for i, line in enumerate(self.lines):
            line = self.apply_backspaces(line) # parse \b as backspace
            y = i * OLED.line_height
            self.led.draw_text2(0, y, line, OLED.line_size)
        self.led.display()
    
    def clear_display(self):
        self.lines = [""]
        self.led.clear_display()

    def clear_then_puts(self, text):
        self.clear_display()
        self.puts(text)
