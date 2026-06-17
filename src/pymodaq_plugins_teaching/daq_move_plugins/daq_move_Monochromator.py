from typing import Union, List, Dict
from pymodaq.control_modules.move_utility_classes import (DAQ_Move_base, comon_parameters_fun,
                                                          main, DataActuatorType, DataActuator)

from pymodaq_utils.utils import ThreadCommand  # object used to send info back to the main thread
from pymodaq_gui.parameter import Parameter

from pymodaq_plugins_teaching.hardware.spectrometer import Spectrometer
from pymodaq_data import Q_
# from pymodaq.control_modules.thread_commands import ThreadStatus


# TODO:
# (1) change the name of the following class to DAQ_Move_TheNameOfYourChoice
# (2) change the name of this file to daq_move_TheNameOfYourChoice ("TheNameOfYourChoice" should be the SAME
#     for the class name and the file name.)
# (3) this file should then be put into the right folder, namely IN THE FOLDER OF THE PLUGIN YOU ARE DEVELOPING:
#     pymodaq_plugins_my_plugin/daq_move_plugins
class DAQ_Move_Monochromator(DAQ_Move_base):
    """ Instrument plugin class for an actuator.

    This object inherits all functionalities to communicate with PyMoDAQ’s DAQ_Move module through inheritance via
    DAQ_Move_base. It makes a bridge between the DAQ_Move module and the Python wrapper of a particular instrument.

    TODO Complete the docstring of your plugin with:
        * The set of controllers and actuators that should be compatible with this instrument plugin.
        * With which instrument and controller it has been tested.
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
    is_multiaxes = False
    _axis_names: Union[List[str], Dict[str, int]] = ['axis_1', 'axis_2']
    _controller_units: Union[str, List[str]] = 'nm'
    _epsilon: Union[float, List[float]] = 0.1
    data_actuator_type = DataActuatorType.DataActuator

    params = [
        {'title': 'Info', 'name': 'info', 'type': 'str', 'value': ''},
        {'title': 'Tau', 'name': 'tau', 'type': 'float', 'value': 500, 'units': 'ms'},
        {'title': 'Grating', 'name': 'grating', 'type': 'list', 'limits': Spectrometer.gratings, 'value': Spectrometer.gratings[0]}
    ] + comon_parameters_fun(is_multiaxes, axis_names=_axis_names, epsilon=_epsilon)

    def ini_attributes(self):
        self.controller: Spectrometer = None

    def get_actuator_value(self):
        """Get the current value from the hardware with scaling conversion.

        Returns
        -------
        float: The position obtained after scaling conversion.
        """
        pos = DataActuator(data=self.controller.get_wavelength(), units=self.axis_unit)
        pos = self.get_position_with_scaling(pos)
        return pos

    def close(self):
        """Terminate the communication protocol"""
        if self.is_master:
            self.controller.close_communication()  # when writing your own plugin replace this line

    def commit_settings(self, param: Parameter):
        """Apply the consequences of a change of value in the detector settings

        Parameters
        ----------
        param: Parameter
            A given parameter (within detector_settings) whose value has been changed by the user
        """
        if param.name() == "tau":
            tau_q = Q_(param.value(), 'ms')
            self.controller.tau = tau_q.m_as('s')
        if param.name() == "grating":
            self.controller.grating = param.value()
        else:
            pass

    def ini_stage(self, controller=None):
        """Actuator communication initialization

        Parameters
        ----------
        controller: (object)
            custom object of a PyMoDAQ plugin (Slave case). None if only one actuator by controller (Master case)

        Returns
        -------
        info: str
        initialized: bool
            False if initialization failed otherwise True
        """
        self.ini_stage_init(slave_controller=controller)  # will be useful when controller is slave

        if self.is_master:  # is needed when controller is master
            self.controller = Spectrometer()  # arguments for instantiation
            self.controller.set_wavelength(532)
            initialized = self.controller.open_communication()
        else:
            self.controller = controller
            initialized = True
        
        self.settings.child('tau').setValue(Q_(self.controller.tau, 's').m_as('ms'))  # On vient sonder la valeur tau du controlleur 
                                                                                        # pour la mettre à jour dans les settings (on ne la hardcode pas)
        self.settings.child('grating').setValue(self.controller.grating)

        info = "Controller initialized"
        self.settings.child('info').setValue(self.controller.infos)

        # A checker pour changer les valeurs initiales des boites verte et rouge (move_abs)
        # self.emit_status(ThreadCommand(ThreadStatus.UPDATE_UI, 'set_abs_value_green', args=(Q_('300 nm'), )))

        return info, initialized

    def move_abs(self, value: DataActuator):
        """Move the actuator to the absolute target defined by value

        Parameters
        ----------
        value: (float) value of the absolute target positioning
        """

        value = self.check_bound(value)  # if user checked bounds, the defined bounds are applied here
        self.target_value = value
        value = self.set_position_with_scaling(value)  # apply scaling if the user specified one
        ## TODO for your custom plugin
        self.controller.set_wavelength(value.value(self.axis_unit), set_type='abs')  # axis_unit ou 'nm' not to be
                                                                                     # mixed up with axis_units
        self.emit_status(ThreadCommand('Update_Status', ['Some info you want to log']))

    def move_rel(self, value: DataActuator):
        """ Move the actuator to the relative target actuator value defined by value

        Parameters
        ----------
        value: (float) value of the relative target positioning
        """
        value = self.check_bound(self.current_position + value) - self.current_position
        self.target_value = value + self.current_position
        value = self.set_position_relative_with_scaling(value)

        ## TODO for your custom plugin
        self.controller.set_wavelength(value.value(self.axis_unit), set_type='rel')  # when writing your own plugin replace this line
        self.emit_status(ThreadCommand('Update_Status', ['Some info you want to log']))

    def move_home(self):
        """Call the reference method of the controller"""

        self.controller.find_reference()
        self.emit_status(ThreadCommand('Update_Status', ['Some info you want to log']))

    def stop_motion(self):
        """Stop the actuator and emits move_done signal"""

        ## TODO for your custom plugin
        self.controller.stop()  # when writing your own plugin replace this line
        self.emit_status(ThreadCommand('Update_Status', ['Some info you want to log']))


if __name__ == '__main__':
    main(__file__)
