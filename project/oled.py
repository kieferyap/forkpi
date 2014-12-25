import gaugette.ssd1306
import time
import sys

class OLED:
    line_height = 16
    line_size = 2
    
    def __init__(self, reset_pin=8, dc_pin=9, n_lines=4):
        self.led = gaugette.ssd1306.SSD1306(reset_pin=reset_pin, dc_pin=dc_pin)
        self.led.begin()
        self.n_lines = n_lines
        self.lines = [""]
        self.clear_display()
    
    def puts(self, text):
        self.led.clear_display()
        lines = text.split('\n')
        if self.lines:
            self.lines[-1] += lines[0]
        self.lines.extend(lines[1:])
        self.lines = self.lines[-self.n_lines:]
        
        for i, line in enumerate(self.lines):
            y = i * OLED.line_height
            self.led.draw_text2(0, y, line, OLED.line_size)
        self.led.display()
    
    def clear_display(self):
        self.lines = [""]
        self.led.clear_display()
