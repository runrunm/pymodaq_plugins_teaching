# -*- coding: utf-8 -*-
"""
Created the 09/10/2022

@author: Sebastien Weber
"""
from qtpy import QtCore
import numpy as np
from easydict import EasyDict as edict
from pymodaq.utils.daq_utils import ThreadCommand, getLineInfo
from pymodaq.utils.data import DataFromPlugins, Axis, DataToExport
from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, comon_parameters, main

from pymodaq_plugins_teaching.hardware.spectrometer import Spectrometer
from pymodaq.post_treatment.process_to_scalar import DataProcessorFactory
from pymodaq.utils.math_utils import my_moment
math_factory = DataProcessorFactory()


class DAQ_1DViewer_Spectrometer(DAQ_Viewer_base):
    """
    """
    params = comon_parameters +\
             [{'title': 'Gratings:', 'name': 'gratings', 'type': 'list', 'limits': Spectrometer.gratings},
              {'title': 'Info:', 'name': 'info', 'type': 'str', 'value': ''},
              {'title': 'Grating wavelength:', 'name': 'grating', 'type': 'float', 'value': 532},
            ]

    def ini_attributes(self):
        self.controller: Spectrometer = None

    def commit_settings(self, param):
        """Apply the consequences of a change of value in the detector settings

        Parameters
        ----------
        param: Parameter
            A given parameter (within detector_settings) whose value has been changed by the user
        """
        if param.name() == 'grating':
            self.controller.set_wavelength(param.value())

        elif param.name() == 'gratings':
            self.controller.grating = param.value()

        self.x_axis = Axis('wavelength', data=self.controller.get_wavelength_axis())

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
        self.x_axis = Axis('wavelength', data=self.controller.get_wavelength_axis())
        self.data_grabed_signal_temp.emit([DataFromPlugins(name='Monochromator',
                                                           data=[np.zeros((Spectrometer.Nx, ))],
                                                           dim='Data1D',
                                                           labels=['Spectrometer Amplitudes'],
                                                           axes=[Axis(data=self.controller.get_wavelength_axis(),
                                                                     label='Wavelength',
                                                                     units='nm')]),
                                           ])
        self.emit_status(ThreadCommand('update_main_settings',
                                       attribute=[['wait_time'], 234, 'value']))
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
        dwa = DataFromPlugins(name='Monochromator',
                              data=[self.controller.get_wavelength_axis(), data_tot, ],
                              dim='Data1D',
                              labels=['Spectrometer Amplitudes'],
                              axes=[],
                              )

        self.dte_signal.emit(DataToExport('spectro', data=[dwa]))
        QtCore.QThread.msleep(100)

    def stop(self):
        self.controller.stop()
        return ''


if __name__ == '__main__':
    main(__file__)
