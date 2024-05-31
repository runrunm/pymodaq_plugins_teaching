import numpy as np
from pymodaq.utils.daq_utils import ThreadCommand
from pymodaq.utils.data import DataFromPlugins, DataToExport
from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, comon_parameters, main
from pymodaq.utils.parameter import Parameter


from pymodaq_plugins_teaching.hardware.spectrometer import Spectrometer


class DAQ_2DViewer_CameraMonochromator(DAQ_Viewer_base):
    """
    """
    params = comon_parameters+[
        {'title': 'Exposure (ms)', 'name': 'exposure', 'type': 'slide', 'value': 50, 'min': 1,
         'max': 100, 'subtype': 'linear'},
        {'title': 'Noise level', 'name': 'noise', 'type': 'float', 'value': 0.5, }
        ]

    def ini_attributes(self):
        self.controller: Spectrometer = None

    def commit_settings(self, param: Parameter):
        """Apply the consequences of a change of value in the detector settings

        Parameters
        ----------
        param: Parameter
            A given parameter (within detector_settings) whose value has been changed by the user
        """
        if param.name() == 'noise':
            self.controller.noise = param.value()
        elif param.name() == 'exposure':
            self.controller.amplitude = param.value()

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
                               new_controller=Spectrometer())

        if self.settings['controller_status'] == 'Master':
            initialized = self.controller.open_communication()
        else:
            initialized = True

        self.emit_status(ThreadCommand('update_main_settings', [['wait_time'], 100, 'value']))

        info = "Whatever info you want to log"
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
        data_tot = self.controller.grab_image()
        self.dte_signal.emit(
            DataToExport(name='myplugin',
                         data=[DataFromPlugins(name='Mock1', data=[data_tot],
                                               dim='Data2D', labels=['Camera'])]))

    def stop(self):
        """Stop the current grab hardware wise if necessary"""
        self.controller.stop()
        self.emit_status(ThreadCommand('Update_Status', ['Some info you want to log']))
        ##############################
        return ''


if __name__ == '__main__':
    main(__file__)
