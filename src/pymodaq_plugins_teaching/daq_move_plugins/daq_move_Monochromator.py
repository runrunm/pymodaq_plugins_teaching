from pymodaq.daq_move.utility_classes import DAQ_Move_base  # base class
from pymodaq.daq_move.utility_classes import comon_parameters_fun, main  # common set of parameters for all actuators
from pymodaq.daq_utils.daq_utils import ThreadCommand, getLineInfo  # object used to send info back to the main thread
from easydict import EasyDict as edict  # type of dict
from pymodaq_plugins_teaching.hardware.spectrometer import Spectrometer


class DAQ_Move_Monochromator(DAQ_Move_base):
    """Plugin for the Template Instrument

    This object inherits all functionality to communicate with PyMoDAQ Module through inheritance via DAQ_Move_base
    It then implements the particular communication with the instrument

    Attributes:
    -----------
    controller: object
        The particular object that allow the communication with the hardware, in general a python wrapper around the
         hardware library
    """
    _controller_units = 'Wavelength'
    is_multiaxes = True
    axes_names = ['wavelength']

    params = [{'title': 'Info:', 'name': 'info', 'type': 'str', 'value': ''},
              {'title': 'Grating:', 'name': 'grating', 'type': 'list', 'values': Spectrometer.gratings},
              {'title': 'Tau (ms):', 'name': 'tau', 'type': 'int', 'value': 2000},] +\
             comon_parameters_fun(is_multiaxes, axes_names)

    def get_actuator_value(self):
        """Get the current value from the hardware with scaling conversion.

        Returns
        -------
        float: The position obtained after scaling conversion.
        """

        pos = self.controller.get_wavelength()  # when writing your own plugin replace this line
        pos = self.get_position_with_scaling(pos)
        return pos

    def close(self):
        """Terminate the communication protocol"""
        self.controller.close_communication()

    def commit_settings(self, param):
        """Apply the consequences of a change of value in the detector settings

        Parameters
        ----------
        param: Parameter
            A given parameter (within detector_settings) whose value has been changed by the user
        """
        if param.name() == "grating":
            self.controller.grating = param.value()
        elif param.name() == 'tau':
            self.controller.tau = param.value() / 1000

    def ini_stage(self, controller: Spectrometer = None):
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
        self.controller = self.ini_stage_init(old_controller=controller,
                                              new_controller=Spectrometer())
        self.controller.open_communication()
        self.settings.child('info').setValue(self.controller.infos)

        info = self.controller.infos
        initialized = True  # or False if your hardware coun't be initialized
        return info, initialized

    def move_abs(self, value):
        """ Move the actuator to the absolute target defined by value

        Parameters
        ----------
        value: (float) value of the absolute target positioning
        """

        value = self.check_bound(value)  #if user checked bounds, the defined bounds are applied here
        value = self.set_position_with_scaling(value)  # apply scaling if the user specified one
        self.controller.set_wavelength(value, 'abs')
        self.target_position = value

    def move_rel(self, value):
        """ Move the actuator to the relative target actuator value defined by value

        Parameters
        ----------
        value: (float) value of the relative target value
        """
        value = self.check_bound(self.current_position+value)-self.current_position
        self.target_position = value + self.current_position
        self.controller.set_wavelength(value, 'rel')

    def move_home(self):
        """Call the reference method of the controller"""
        self.controller.find_reference()

    def stop_motion(self):
        """Stop the actuator and emits move_done signal"""
        self.controller.stop()


if __name__ == '__main__':
    main(__file__)

