# -*- coding: utf-8 -*-
"""
Created the 09/10/2022

@author: Sebastien Weber
"""

import numpy as np
from easydict import EasyDict as edict
from pymodaq.utils.daq_utils import ThreadCommand, getLineInfo, DataFromPlugins
from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, comon_parameters, main

from pymodaq_plugins_teaching.hardware.spectrometer import Spectrometer


class DAQ_0DViewer_Monochromator(DAQ_Viewer_base):
    """
    """
    params = comon_parameters +\
             []

    def ini_attributes(self):
        self.controller = None

    def commit_settings(self, param):
        """Apply the consequences of a change of value in the detector settings

        Parameters
        ----------
        param: Parameter
            A given parameter (within detector_settings) whose value has been changed by the user
        """
        pass

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


        #initialize viewers pannel with the future type of data
        self.data_grabed_signal_temp.emit([DataFromPlugins(name='Monochromator',
                                                           data=[np.array([0.])],
                                                           dim='Data0D',
                                                           labels=['MonoChromator Amplitude'])])

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
        data_tot = self.controller.grab_monochromator()
        self.data_grabed_signal.emit([DataFromPlugins(name='Monochromator',
                                                      data=[data_tot],
                                                      dim='Data0D',
                                                      labels=['MonoChromator Amplitude'])])

    def stop(self):
        self.controller.stop()

        return ''


if __name__ == '__main__':
    main(__file__)
