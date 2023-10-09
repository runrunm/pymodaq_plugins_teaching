# -*- coding: utf-8 -*-
"""
Created the 16/10/2022

@author: Sebastien Weber
"""

import pyfirmata
import time
from pymodaq.utils.logger import set_logger, get_module_name
import serial
from serial.tools.list_ports import comports


COMPORTS = [port.name for port in comports()]
logger = set_logger(get_module_name(__file__))


class PinError(Exception):
    pass


class ServoError(Exception):
    pass


class Servo:
    def __init__(self):
        self._com_port = None
        self._board = None
        self._servo_pin = -1
        self._angle = None
        self.info = 'Servo driver v0.0.1'

    def open_communication(self, comport: str = 'COM15'):
        if comport in COMPORTS:
            self._com_port = comport
            HIGH = True  # Create a high state for turn on led
            LOW = False  # Create a low state for turn off led
            self._board = pyfirmata.Arduino(comport)  # Initialize the communication with the Arduino card
            time.sleep(1)
            return True
        else:
            return False

    def close_communication(self):
        if self._board is not None:
            self._board.exit()

    @property
    def servo_pin(self):
        return self._servo_pin

    @servo_pin.setter
    def servo_pin(self, pin: int):
        if not isinstance(pin, int) or not(0 <= pin <= 13):
            raise PinError(f'Pin number should be an integer between 0 and 13')
        else:
            self._servo_pin = pin
            self._board.digital[pin].mode = pyfirmata.SERVO

    def set_angle(self, angle: int):
        self._board.digital[self._servo_pin].write(angle)
        self.angle = int(angle)
        time.sleep(0.015)

    @property
    def angle(self):
        if self._angle is None:
            self.set_angle(0)
            self._angle = 0
        return self._angle

    @angle.setter
    def angle(self, angle: int):
        if not isinstance(angle, int) and not(0 <= angle <= 180):
            raise ServoError(f'Invalid angle set for the servo on pin {self._servo_pin}')
        else:
            self._angle = angle

