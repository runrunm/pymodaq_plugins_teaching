import numpy as np

from pymodaq_utils.utils import ThreadCommand
from pymodaq_data.data import DataToExport, Q_
from pymodaq_gui.parameter import Parameter

from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, comon_parameters, main
from pymodaq.utils.data import DataFromPlugins, Axis

from pymodaq_plugins_teaching.hardware.generator import Generator, WaveType


class DAQ_1DViewer_Generator(DAQ_Viewer_base):
    """ Instrument plugin class for a OD viewer.
    
    This object inherits all functionalities to communicate with PyMoDAQ’s DAQ_Viewer module through inheritance via
    DAQ_Viewer_base. It makes a bridge between the DAQ_Viewer module and the Python wrapper of a particular instrument.

    TODO Complete the docstring of your plugin with:
        * The set of instruments that should be compatible with this instrument plugin.
        * With which instrument it has actually been tested.
        * The version of PyMoDAQ during the test.
        * The version of the operating system.
        * Installation instructions: what manufacturer’s drivers should be installed to make it run?

    Attributes:
    -----------
    controller: object
        The particular object that allow the communication with the hardware, in general a python wrapper around the
         hardware library.
         
    # TODO add your particular attributes here if any

    """
    params = comon_parameters+[
        {'title': 'Npts:', 'name': 'npts', 'type': 'int', 'value': 256},
        {'title': 'Delta time (s):', 'name': 'delta_t', 'type': 'float', 'value': 1e-3, 'suffix': 's', 'siPrefix': True},
        {'title': 'Waveforms:', 'name': 'waveform', 'type': 'list', 'limits': WaveType.names()},
        {'title': 'Amplitude:', 'name': 'amplitude', 'type': 'float', 'value': 1, 'suffix': 'V', 'siPrefix': True},
        {'title': 'Frequency:', 'name': 'frequency', 'type': 'float', 'value': 10, 'suffix': 'Hz', 'siPrefix': True},

    ]

    def ini_attributes(self):
        #  TODO declare the type of the wrapper (and assign it to self.controller) you're going to use for easy
        #  autocompletion
        self.controller: Generator = None

        #TODO declare here attributes you want/need to init with a default value
        pass

    def commit_settings(self, param: Parameter):
        """Apply the consequences of a change of value in the detector settings

        Parameters
        ----------
        param: Parameter
            A given parameter (within detector_settings) whose value has been changed by the user
        """
        if param.name() == "amplitude":
           self.controller.amplitude = Q_(param.value(), param.opts['suffix'])
        elif param.name() == 'frequency':
            self.controller.frequency = Q_(param.value(), 'Hz')
        elif param.name() == 'waveform':
            self.controller.waveform = param.value()

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


        if self.is_master:
            self.controller = Generator()  #instantiate you driver with whatever arguments are needed
            initialized = True
        else:
            self.controller = controller
            initialized = True

        info = "Whatever info you want to log"
        return info, initialized

    def close(self):
        """Terminate the communication protocol"""
        ## TODO for your custom plugin
        if self.is_master:
            pass

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

        npts = self.settings['npts']
        dt = self.settings['delta_t']

        time_array, waveform = self.controller.get_waveform(npts, Q_(dt, 's'))

        self.dte_signal.emit(DataToExport(
            name='mydte',
            data=[DataFromPlugins(name='mymock',
                                  data=[waveform.magnitude + 0.1 *np.random.randn(*waveform.shape)],
                                  dim='Data1D', labels=['label00',],
                                  units=waveform.units,
                                  axes=[Axis('Time', units='s',
                                             data=time_array.m_as('s'))])]))

    def stop(self):
        """Stop the current grab hardware wise if necessary"""

        pass


if __name__ == '__main__':
    main(__file__)