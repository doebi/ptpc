#! /usr/bin/env python

import sys
import time
import keyboard
from bluepy import btle
from time import sleep


class PlaymobilRacerScan(btle.Scanner):

    NAME_PREFIX = 'PM-RC '

    def __init__(self, btdev=0):
        self.started = False
        super().__init__(btdev)

    def __del__(self):
        self.stop()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.stop()

    def start(self, passive=False):
        super().start(passive)
        self.started = True
        return self

    def stop(self):
        if self.started:
            self.started = False
            super().stop()

    def process(self, timeout=1):
        super().process(timeout)
        cars = []
        for device in self.getDevices():
            if not device.connectable:
                continue
            name = None
            for data in device.getScanData():
                if data[0] == 9:
                    name = data[2]
                    break
            if not name or not name.startswith(self.NAME_PREFIX):
                continue
            cars.append(PlaymobilRacer(device.addr, name, device.rssi))
        return cars

    @staticmethod
    def multry(times):
        with PlaymobilRacerScan() as scan:
            for timeout in times:
                cars = scan.process(timeout)
                if cars:
                    break
        return cars


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

        keyboard.hook(self.key_cb)

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

    def key_cb(self, event):
        # handle acceleration and motor control
        if keyboard.is_pressed("w"):
            print("+")
            self.motor(128)
        elif keyboard.is_pressed("s"):
            self.motor(-127)
        else:
            self.motor(0)

        # handle steering
        if keyboard.is_pressed("d"):
            self.turn(128)
        elif keyboard.is_pressed("a"):
            self.turn(-127)
        else:
            self.turn(0)
            self.motor(self.rotation)


def demo(mac=None):
    if mac:
        car = PlaymobilRacer(mac)
    else:
        cars = PlaymobilRacerScan.multry([0.1, 0.3, 1, 3])
        if not cars:
            sys.exit("Not found any Playmobil Racer car!")
        car = max(cars)  # select closest one
        for found in cars:
            print("%c %s" % ('*' if found == car else ' ', found))
    with car:
        car.light()
        car.speed()
        car.motor(128)
        car.turn(128)



def live(mac=None):
    if mac:
        car = PlaymobilRacer(mac)
    else:
        cars = PlaymobilRacerScan.multry([0.1, 0.3, 1, 3])
        if not cars:
            sys.exit("Not found any Playmobil Racer car!")
        car = max(cars)  # select closest one
        for found in cars:
            print("%c %s" % ('*' if found == car else ' ', found))
    with car:
        car.speed(3)
        while True:
            car.key_cb(None)
            sleep(0.1)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        live(sys.argv[1])
    else:
        live()
