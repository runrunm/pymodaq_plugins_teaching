import numpy as np
from pymodaq.utils.daq_utils import ThreadCommand
from pymodaq.utils.data import DataFromPlugins, Axis, DataToExport
from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, comon_parameters, main
from pymodaq.utils.parameter import Parameter
from pymodaq_plugins_teaching.hardware.arduino import Arduino


class DAQ_1DViewer_LEDSpectro(DAQ_Viewer_base):
    """ Instrument plugin class for a 1D viewer.
    
    This object inherits all functionalities to communicate with PyMoDAQ’s DAQ_Viewer module through inheritance via
    DAQ_Viewer_base. It makes a bridge between the DAQ_Viewer module and the Python wrapper of a particular instrument.


    Attributes:
    -----------
    controller: object
        The particular object that allow the communication with the hardware, in general a python wrapper around the
         hardware library.
         
    """
    params = comon_parameters+[
        ]

    def ini_attributes(self):
        #  autocompletion
        self.controller: Arduino = None
        self.x_axis = None

    def commit_settings(self, param: Parameter):
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

        self.ini_detector_init(old_controller=controller,
                               new_controller=None)

        if self.is_master:
            self.controller = Arduino()

        info = "Whatever info you want to log"
        initialized = True
        return info, initialized

    def close(self):
        """Terminate the communication protocol"""
        if self.is_master:
            self.controller.close()

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

        axis_array = self.controller.get_spectrometer_axis()
        data_array = self.controller.generate_spectrum()
        self.dte_signal.emit(DataToExport(
            'myplugin',
            data=[DataFromPlugins(name='Mock1', data=[data_array],
                                  dim='Data1D', labels=['Spectrum'],
                                  units='counts',
                                  axes=[Axis('Wavelength', units='m', data=axis_array * 1e-9)],
                                  )]))

    def stop(self):
        """Stop the current grab hardware wise if necessary"""
        pass


if __name__ == '__main__':
    main(__file__)
