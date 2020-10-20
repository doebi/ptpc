#! /usr/bin/env python

import sys
import time
from bluepy import btle


class PlaymobilRacer:

    CHARACTERISTIC_UUID = '06d1e5e7-79ad-4a71-8faa-373789f7d93c'

    def __init__(self, addr=None, name=None, rssi=None):
        self.addr = addr
        self.name = name
        self.rssi = rssi
        self.device = None
        self.handle = None
        self.rotation = 0
        self.direction = 0
        self.last_pressed = None

    def __del__(self):
        self.disconnect()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.disconnect()

    def __eq__(self, other):
        return self.addr == other.addr

    def __lt__(self, other):
        return self.rssi < other.rssi

    def __str__(self):
        return '%s - %s' % (self.addr, self.name)

    def connect(self, btdev=0):
        self.device = btle.Peripheral(self.addr, iface=btdev)
        handles = self.device.getCharacteristics(uuid=self.CHARACTERISTIC_UUID)
        if handles:
            self.handle = handles[0]

    def disconnect(self):
        if self.device:
            self.device.disconnect()
            self.device = None
            self.handle = None

    def _send(self, command, value, retry=True):
        if not self.handle:
            self.connect()
        try:
            self.handle.write(command + bytes([int(value)]) + b'\x0f')
        except btle.BTLEDisconnectError:
            self.handle = None
            if retry:
                self._send(command, value, False)

    def _send_int8(self, command, int8):
        int8 = max(int8, -127)
        int8 = min(int8, 128)
        self._send(command, int8 + 127)

    def light(self, state=True):
        self._send(b'\x24', 2 if state else 1)

    def turn(self, direction=0):
        self._send_int8(b'\x40', direction)
        self.direction = direction

    def speed(self, level=5):
        level = max(level, 1)
        level = min(level, 5)
        self._send(b'\x25', level)

    def motor(self, rotation=0):
        self._send_int8(b'\x23', rotation)
        self.rotation = rotation

    def stop(self):
        self.turn(0)
        self.motor(0)
        self.light(False)

    def key(self, pressed):
        if not bool(pressed) and not bool(self.last_pressed):
            return
        self.last_pressed = pressed
        try:
            # handle speed setting
            if "1" in pressed:
                self.speed(1)
            if "2" in pressed:
                self.speed(2)
            if "3" in pressed:
                self.speed(3)
            if "4" in pressed:
                self.speed(4)
            if "5" in pressed:
                self.speed(5)

            # handle acceleration and motor control
            if "w" in pressed:
                self.motor(128)
            elif "s" in pressed:
                self.motor(-127)
            else:
                self.motor(0)

            # handle steering
            if "d" in pressed:
                self.turn(128)
            elif "a" in pressed:
                self.turn(-127)
            else:
                self.turn(0)
        except:
            print("whoopsie")
