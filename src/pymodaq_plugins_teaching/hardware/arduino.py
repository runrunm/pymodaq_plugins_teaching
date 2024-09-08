import numbers
from pyvisa import ResourceManager

from pymodaq.utils.data import DataRaw, Axis
from pymodaq.utils.math_utils import np, gauss1D


VISA_rm = ResourceManager()

COM_PORTS = []
for name, rinfo in VISA_rm.list_resources_info().items():
    if rinfo.alias is not None:
        COM_PORTS.append(rinfo.alias)
    else:
        COM_PORTS.append(name)

SIZE = 256
LAMBDA_RED = 650
LAMBDA_GREEN = 515
LAMBDA_BLUE = 450


class Arduino:
    COM_PORTS = COM_PORTS

    led_pins = {'red': 9, 'green': 10, 'blue': 11}
    servo_pin = 3

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pin_values_output = {9: 0, 10: 0, 11: 0, 3: 80}

    @staticmethod
    def round_value(value):
        return max(0, min(255, int(value)))

    def set_pins_output_to(self, value: int):
        for pin in self.pin_values_output:
            self.analog_write(pin, int(value))

    def get_output_pin_value(self, pin: int) -> numbers.Number:
        value = self.pin_values_output.get(pin, 0)
        return value

    def analog_write(self, pin: int, value: numbers.Number):
        """fake method mimicking the telemetrix library
        to set a voltage to a given pin using PWM"""
        value = self.round_value(value)
        self.pin_values_output[pin] = value

    def servo_write(self, pin, value: int):
        """fake method mimicking the telemetrix library
        to set a position of a servo motor connected to pin: pin"""
        value = self.round_value(value)
        self.pin_values_output[pin] = value

    def get_spectrometer_axis(self) -> np.ndarray:
        return np.linspace(400, 800, SIZE, endpoint=True)

    def generate_spectrum(self) -> np.ndarray:
        """ Grab a spectrum revealing the content of the RGB LED"""

        axis = self.get_spectrometer_axis()
        data_array = np.zeros((SIZE,))
        if self.pin_values_output[self.servo_pin] > 70:
            data_array += (gauss1D(axis, LAMBDA_RED, 15) *
                           self.pin_values_output[self.led_pins['red']])
            data_array += (gauss1D(axis, LAMBDA_GREEN, 12) *
                           self.pin_values_output[self.led_pins['green']])
            data_array += (gauss1D(axis, LAMBDA_BLUE, 15) *
                           self.pin_values_output[self.led_pins['blue']])

        return data_array

    def close(self):
        pass
