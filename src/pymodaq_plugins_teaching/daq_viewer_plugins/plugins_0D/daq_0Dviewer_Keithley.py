import numpy as np
from pymodaq.utils.daq_utils import ThreadCommand
from pymodaq.utils.data import DataFromPlugins, DataToExport
from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, comon_parameters, main
from pymodaq.utils.parameter import Parameter
from pymodaq.utils.parameter import utils as putils


if False:
    from pylablib.devices.Keithley.multimeter import Keithley2110, TGenericFunctionParameters
    from pyvisa import ResourceManager
else:
    from pymodaq_plugins_teaching.hardware.keithley import Keithley2110, ResourceManager, TGenericFunctionParameters


rm = ResourceManager()

RESOURCES = rm.list_resources()
MEASUREMENTS = list(Keithley2110._p_function._get_alias_map().keys())


class DAQ_0DViewer_Keithley(DAQ_Viewer_base):
    """
    """
    params = comon_parameters+[
        {'title': 'Connections:', 'name': 'addresses', 'type': 'list', 'limits': RESOURCES},
        {'title': 'Info:', 'name': 'info', 'type': 'str', 'readonly': True},
        {'title': 'Measurements:', 'name': 'measure', 'type': 'list', 'limits': MEASUREMENTS},
        {'title': 'Config:', 'name': 'config', 'type': 'group', 'children': [
            {'title': 'Reset:', 'name': 'reset', 'type': 'bool_push', 'value': False},
            {'title': 'Autorange:', 'name': 'auto', 'type': 'bool', 'value': True},
            {'title': 'Range:', 'name': 'range', 'type': 'float'},
            {'title': 'Resolution:', 'name': 'resolution', 'type': 'float'},

        ]},
        ]

    def ini_attributes(self):
        self.controller: Keithley2110 = None

    def commit_settings(self, param: Parameter):
        """Apply the consequences of a change of value in the detector settings

        Parameters
        ----------
        param: Parameter
            A given parameter (within detector_settings) whose value has been changed by the user
        """
        if param.name() == 'measure':
            self.controller.set_function(param.value())
            self.get_params()

        elif param.name() == 'auto':
            self.set_params('autorng', param.value())
        elif param.name() == 'range':
            self.set_params('rng', param.value())
        elif param.name() == 'resolution':
            self.set_params('resolution', param.value())
        elif param.name() == 'reset':
            self.controller.reset()

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
                               new_controller=Keithley2110(self.settings['addresses']))

        info = self.controller.get_id()
        self.settings.child('info').setValue(info)
        measurement = self.controller.get_function('primary')
        self.settings.child('measure').setValue(measurement)
        self.get_params()

        initialized = True
        return info, initialized

    def get_params(self):
        measurement = self.controller.get_function('primary')
        self._write_params(self.controller.get_function_parameters(measurement))

    def _write_params(self, params: TGenericFunctionParameters):
        self.settings.child('config', 'auto').setValue(params.autorng)
        self.settings.child('config', 'range').setValue(params.rng)
        self.settings.child('config', 'resolution').setValue(params.resolution)

    def set_params(self, param_name, param_value):
        self._write_params(self.controller.set_function_parameters(self.controller.get_function('primary'),
                                                                   **{param_name: param_value}))

    def close(self):
        """Terminate the communication protocol"""
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
        data_tot = self.controller.get_reading('primary')
        self.dte_signal.emit(
            DataToExport(name='myplugin',
                         data=[DataFromPlugins(name='Mock1', data=[np.array([data_tot])],
                                               dim='Data0D', labels=['DM2110'])]))

    def stop(self):
        """Stop the current grab hardware wise if necessary"""
        self.emit_status(ThreadCommand('Update_Status', ['Some info you want to log']))
        return ''


if __name__ == '__main__':
    main(__file__, init=True)
