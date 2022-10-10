# -*- coding: utf-8 -*-
"""
Created the 09/10/2022

@author: Sebastien Weber
"""
# -*- coding: utf-8 -*-
"""
Created the 09/10/2022

@author: Sebastien Weber
"""

import numpy as np
from easydict import EasyDict as edict
from pymodaq.daq_utils.daq_utils import ThreadCommand, getLineInfo, DataFromPlugins, Axis
from pymodaq.daq_viewer.utility_classes import DAQ_Viewer_base, comon_parameters, main

from pymodaq_plugins_teaching.hardware.spectrometer import Spectrometer


class DAQ_1DViewer_Spectrometer(DAQ_Viewer_base):
    """
    """
    params = comon_parameters +\
             [{'title': 'Info:', 'name': 'info', 'type': 'str', 'value': ''},
              {'title': 'Lambda0:', 'name': 'lambda0', 'type': 'float', 'value': 532},
              {'title': 'Amp:', 'name': 'amplitude', 'type': 'float', 'value': 10},
              {'title': 'width (nm):', 'name': 'width', 'type': 'float', 'value': 2},
              {'title': 'noise:', 'name': 'noise', 'type': 'float', 'value': 0.5},]


    def commit_settings(self, param):
        """Apply the consequences of a change of value in the detector settings

        Parameters
        ----------
        param: Parameter
            A given parameter (within detector_settings) whose value has been changed by the user
        """
        if param.name() == 'lambda0':
            self.controller.data_wavelength = param.value()
        elif param.name() == 'amplitude':
            self.controller.amplitude = param.value()
        elif param.name() == 'width':
            self.controller.width = param.value()
        elif param.name() == 'noise':
            self.controller.noise = param.value()

    def ini_detector(self, controller=None):
        """Detector communication initialization

        Parameters
        ----------
        controller: (object)
            custom object of a PyMoDAQ plugin (Slave case). None if only one actuator/detector by controller
            (Master case)

        Returns
        -------
        info: str
        initialized: bool
            False if initialization failed otherwise True
        """

        self.controller = self.ini_detector_init(old_controller=controller,
                                                 new_controller=Spectrometer())
        self.controller.open_communication()
        self.settings.child('info').setValue(self.controller.infos)
        #initialize viewers pannel with the future type of data
        self.data_grabed_signal_temp.emit([DataFromPlugins(name='Monochromator',
                                                           data=[np.zeros((Spectrometer.Nx, ))],
                                                           dim='Data1D',
                                                           labels=['Spectrometer Amplitudes'])])
        self.emit_x_axis(Axis(data=self.controller.get_wavelength_axis(),
                              label='Wavelength',
                              units='nm'))

        self.settings.child('lambda0').setValue(self.controller.data_wavelength)
        self.settings.child('amplitude').setValue(self.controller.amplitude)
        self.settings.child('width').setValue(self.controller.width)
        self.settings.child('noise').setValue(self.controller.noise)

        info = Spectrometer.infos
        initialized = True
        return info, initialized

    def close(self):
        """Terminate the communication protocol"""
        self.controller.close_communication()

    def grab_data(self, Naverage=1, **kwargs):
        """Start a grab from the detector

        Parameters
        ----------
        Naverage: int
            Number of hardware averaging (if hardware averaging is possible, self.hardware_averaging should be set to
            True in class preamble and you should code this implementation)
        kwargs: dict
            others optionals arguments
        """
        data_tot = self.controller.grab_spectrum()
        self.data_grabed_signal.emit([DataFromPlugins(name='Monochromator',
                                                      data=[data_tot],
                                                      dim='Data1D',
                                                      labels=['Spectrometer Amplitudes']
                                                      )])

    def stop(self):
        self.controller.stop()
        return ''


if __name__ == '__main__':
    main(__file__)
