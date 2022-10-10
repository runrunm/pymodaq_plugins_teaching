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
             [{'title': 'Grating:', 'name': 'grating', 'type': 'list', 'values': Spectrometer.gratings}]

    def commit_settings(self, param):
        """
        """

        if param.name() == 'grating':
           self.controller.grating = param.value()

    def ini_detector(self, controller=None):
        """Detector communication initialization

        Parameters
        ----------
        controller: (object) custom object of a PyMoDAQ plugin (Slave case). None if only one detector by controller (Master case)

        Returns
        -------
        self.status (edict): with initialization status: three fields:
            * info (str)
            * controller (object) initialized controller
            *initialized: (bool): False if initialization failed otherwise True
        """

        try:
            self.status.update(edict(initialized=False,info="",x_axis=None,y_axis=None,controller=None))
            if self.settings.child(('controller_status')).value() == "Slave":
                if controller is None:
                    raise Exception('no controller has been defined externally while this detector is a slave one')
                else:
                    self.controller = controller
            else:
                self.controller = Spectrometer()
                self.controller.open_communication()
                #####################################

            #initialize viewers pannel with the future type of data
            self.data_grabed_signal_temp.emit([DataFromPlugins(name='Monochromator',
                                                               data=[np.zeros((Spectrometer.Nx, ))],
                                                               dim='Data1D',
                                                               labels=['Spectrometer Amplitudes'])])

            self.status.info = Spectrometer.infos
            self.status.initialized = True
            self.status.controller = self.controller
            return self.status

        except Exception as e:
            self.emit_status(ThreadCommand('Update_Status', [getLineInfo() + str(e), 'log']))
            self.status.info = getLineInfo() + str(e)
            self.status.initialized = False
            return self.status

    def close(self):
        """
        Terminate the communication protocol
        """
        self.controller.close_communication()

    def grab_data(self, Naverage=1, **kwargs):
        """

        Parameters
        ----------
        Naverage: (int) Number of hardware averaging
        kwargs: (dict) of others optionals arguments
        """
        data_tot = self.controller.grab_spectrum()
        self.data_grabed_signal.emit([DataFromPlugins(name='Monochromator',
                                                      data=[data_tot],
                                                      dim='Data1D',
                                                      labels=['Spectrometer Amplitudes'],
                                                      x_axis=Axis(data=self.controller.get_wavelength_axis(),
                                                                  label='Wavelength',
                                                                  units='nm'))])

    def stop(self):
        self.controller.stop()

        return ''


if __name__ == '__main__':
    main(__file__)
