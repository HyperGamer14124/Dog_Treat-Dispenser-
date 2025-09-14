from machine import Pin
from time import sleep

class LCD:
    def __init__(self, rs, en, d4, d5, d6, d7):
        # Convert GPIO numbers into Pin objects
        self.rs = Pin(rs, Pin.OUT)
        self.en = Pin(en, Pin.OUT)
        self.data_pins = [
            Pin(d4, Pin.OUT),
            Pin(d5, Pin.OUT),
            Pin(d6, Pin.OUT),
            Pin(d7, Pin.OUT)
        ]
        self._init_lcd()

    def _pulse_enable(self):
        self.en.value(0)
        sleep(0.01)  # Increased delay
        self.en.value(1)
        sleep(0.01)
        self.en.value(0)
        sleep(0.01)

    def _send_nibble(self, nibble):
        for i in range(4):
            self.data_pins[i].value((nibble >> i) & 1)
        self._pulse_enable()

    def _send_byte(self, data, rs_mode):
        self.rs.value(rs_mode)
        self._send_nibble(data >> 4)
        self._send_nibble(data & 0x0F)

    def _init_lcd(self):
        sleep(0.2)  # Longer startup delay
        self._send_nibble(0x03)
        sleep(0.01)
        self._send_nibble(0x03)
        sleep(0.01)
        self._send_nibble(0x03)
        sleep(0.01)
        self._send_nibble(0x02)
        sleep(0.01)

        self._send_byte(0x28, 0)  # 4-bit mode, 2 line, 5x7 dots
        sleep(0.01)
        self._send_byte(0x0C, 0)  # Display on, cursor off
        sleep(0.01)
        self._send_byte(0x06, 0)  # Entry mode
        sleep(0.01)
        self.clear()

    def clear(self):
        self._send_byte(0x01, 0)
        sleep(0.002)

    def move_to(self, col, row):
        row_offsets = [0x00, 0x40]
        self._send_byte(0x80 | (col + row_offsets[row]), 0)

    def putstr(self, string):
        for char in string:
            self._send_byte(ord(char), 1)

