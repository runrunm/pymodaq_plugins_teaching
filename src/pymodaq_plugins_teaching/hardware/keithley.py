# -*- coding: utf-8 -*-
"""
Created the 08/11/2023

@author: Sebastien Weber
"""
import warnings

from pymodaq_plugins_teaching.hardware.serial_addresses import SerialAddresses, BaseEnum
import random
from pylablib.core.devio import SCPI, interface
from pylablib.devices.Keithley.multimeter import TGenericFunctionParameters


class EnumParameterClass(interface.EnumParameterClass):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def names(self):
        list(self._get_alias_map().keys())


class Measurement(BaseEnum):
    volt_dc = 0
    curr_dc = 1
    freq_volt = 2


class ResourceManager:

    def __init__(self):
        pass

    def list_resources(self):
        """List all possible addresses"""
        return SerialAddresses.names()


class Keithley2110:
    """ Python Driver object to communicate with a 2100 Series Keithley Digital Multimeter

    This is simulating a fake instrument but follows the PyLabLib driver structure
    """

    _p_function = interface.EnumParameterClass("function",
                                               {"volt_dc": "VOLT:DC", "curr_dc": "CURR:DC",
                                                "freq_volt": "FREQ:VOLT", "none": "NONE"})


    measurement = Measurement['volt_dc']


    def __init__(self, address: str = None):

        self._resolution: float = 1e-5
        self._auto: bool = True
        self._range: float = 0.1

        self._is_open = False
        if address is not None:
            self.open_communication(address)

    @property
    def is_open(self):
        """ Get the communication status with the instrument"""
        return self._is_open

    def open_communication(self, address: str):
        """ Open a communication channel with the instrument using the serial address (USb, GPIB,...)"""
        if self.is_open:
            raise IOError('Device already connected')
        else:
            if address not in SerialAddresses.names():
                raise IOError('Invalid Address')
            else:
                self._is_open = True

    def close(self):
        """ Close de communication channel"""
        if self._is_open:
            self._is_open = False

    def get_function(self, channel='primary'):
        """ Get the current measurement type"""
        if not self.is_open:
            raise TimeoutError
        return self.measurement.name

    def set_function(self, function: str, channel="primary", reset_secondary=True):
        """ Set a measurement type

        Parameters
        ----------
        function: str
            One of the possible measurement, see the Measurement enum
        """
        if not self.is_open:
            raise TimeoutError
        if function not in Measurement.names():

            warnings.warn(f'The requested measurement, {function} cannot be set')
        else:
            self.measurement = Measurement[function]

    def get_reading(self, channel='primary'):
        """ Grab the current reading from the device"""
        if not self.is_open:
            raise TimeoutError
        return int(self._range * random.random() / self._resolution) * self._resolution

    def reset(self):
        if not self.is_open:
            raise TimeoutError

    def get_id(self):
        """ Get info about the connected device """
        if not self.is_open:
            raise TimeoutError
        return 'KEITHLEY INSTRUMENTS INC.,MODEL 2110,1417097,02.01-02-01'

    def get_function_parameters(self, function: str) -> TGenericFunctionParameters:
        """ Get the parameters of the current measurement: range, resolution, autorange"""
        if not self.is_open:
            raise TimeoutError
        return TGenericFunctionParameters(self._range, self._resolution, self._auto)

    def set_function_parameters(self, function: str, **kwargs):
        """ Set the parameters of a given measurement

        Parameters
        ----------
        function: str
            one of the possible measurement
        kwargs: dict
            mapping of the possible parameters: 'rng', 'resolution', 'autorng'
        Returns
        -------
        TGenericFunctionParameters: the current set parameters
        """
        if not self.is_open:
            raise TimeoutError
        for kwarg in kwargs:
            if kwarg == 'rng':
                self._range = kwargs[kwarg]
            elif kwarg == 'autorng':
                self._auto = kwargs[kwarg]
            elif kwarg == 'resolution':
                self._resolution = kwargs[kwarg]
        return self.get_function_parameters(function)

    def get_id(self):
        """ Get info about the connected device """
        if not self.is_open:
            raise TimeoutError
        return 'KEITHLEY INSTRUMENTS INC.,MODEL 2110,1417097,02.01-02-01'

    def get_function_parameters(self, function: str) -> TGenericFunctionParameters:
        """ Get the parameters of the current measurement: range, resolution, autorange"""
        if not self.is_open:
            raise TimeoutError
        return TGenericFunctionParameters(self._range, self._resolution, self._auto)

    def set_function_parameters(self, function: str, **kwargs):
        """ Set the parameters of a given measurement

        Parameters
        ----------
        function: str
            one of the possible measurement
        kwargs: dict
            mapping of the possible parameters: 'rng', 'resolution', 'autorng'
        Returns
        -------
        TGenericFunctionParameters: the current set parameters
        """
        if not self.is_open:
            raise TimeoutError
        for kwarg in kwargs:
            if kwarg == 'rng':
                self._range = kwargs[kwarg]
            elif kwarg == 'autorng':
                self._auto = kwargs[kwarg]
            elif kwarg == 'resolution':
                self._resolution = kwargs[kwarg]
        return self.get_function_parameters(function)


if __name__ == '__main__':

    meter = Keithley2110(SerialAddresses.names()[0])

    meter.get_function()
    pass