from enum import StrEnum
import numpy as np

from pymodaq_utils.math_utils import linspace_step_N
from pymodaq_data import Q_


class WaveType(StrEnum):
    SINUS = 'Sinus'
    SQUARE = 'Square'
    TRIANGLE = 'Triangle'

    @classmethod
    def names(cls):
        return list(cls._value2member_map_.keys())



class Generator():

    def __init__(self):
        self._wave_type = WaveType.SINUS
        self._freq = Q_(10., 'Hz')
        self._amp = Q_(1., 'V')
        self._offset = Q_(0., 'V')
        self._phase = Q_(0., 'rad')


    @property
    def wave_type(self):
        return self._wave_type

    @wave_type.setter
    def wave_type(self, wave_type: str):
        if wave_type in WaveType.names():
            self._wave_type = WaveType(wave_type)

    @property
    def frequency(self):
        return self._freq

    @frequency.setter
    def frequency(self, freq: Q_):
        if freq.is_compatible_with('Hz'):
            self._freq = freq.to('Hz')

    @property
    def amplitude(self):
        return self._amp

    @amplitude.setter
    def amplitude(self, amp: Q_):
        if amp.is_compatible_with('V'):
            self._amp = amp.to('V')

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, offset: Q_):
        if offset.is_compatible_with('V'):
            self._offset = offset.to('V')

    @property
    def phase(self):
        return self._phase

    @phase.setter
    def phase(self, phase: Q_):
        if phase.is_compatible_with('rad'):
            self._phase = phase.to('rad')

    def get_waveform(self, Npts: int, dt: Q_):
        """ Generate a waveform given the number of points and time resolution

        Parameters
        ----------
        Npts: The number of points in the waveform
        dt: the time resolution as a quantity

        Returns
        -------
        np.ndarray: 1D array containing the time
        np.ndarray: 1D Quantity array containing the waveform
        """
        time_array = linspace_step_N(Q_(0., 's'), dt, Npts)

        if self._wave_type == WaveType.SINUS:
            return time_array, self.amplitude * np.sin(2 * np.pi * self.frequency * time_array - self.phase) + self.offset