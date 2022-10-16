from pymodaq.daq_move.utility_classes import DAQ_Move_base  # base class
from pymodaq.daq_move.utility_classes import comon_parameters_fun, main  # common set of parameters for all actuators
from pymodaq_plugins_teaching.hardware.servo import Servo, COMPORTS


class DAQ_Move_ServoFirmata(DAQ_Move_base):
    """Plugin for the Template Instrument

    This object inherits all functionality to communicate with PyMoDAQ Module through inheritance via DAQ_Move_base
    It then implements the particular communication with the instrument

    Attributes:
    -----------
    controller: object
        The particular object that allow the communication with the hardware, in general a python wrapper around the
         hardware library
    """
    _controller_units = 'degree'
    is_multiaxes = False
    axes_names = []

    params = [{'title': 'Info:', 'name': 'info', 'type': 'str', 'value': ''},
              {'title': 'COM port:', 'name': 'comport', 'type': 'list', 'values': COMPORTS},
              {'title': 'Pin:', 'name': 'pin', 'type': 'int', 'value': 9},] +\
             comon_parameters_fun(is_multiaxes, axes_names)

    def get_actuator_value(self):
        """Get the current value from the hardware with scaling conversion.

        Returns
        -------
        float: The position obtained after scaling conversion.
        """

        pos = self.controller.angle  # when writing your own plugin replace this line
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
        if param.name() == "pin":
            self.controller.servo_pin = param.value()

    def ini_stage(self, controller: Servo = None):
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
                                              new_controller=Servo())
        self.controller.open_communication(self.settings['comport'])

        info = self.controller.info
        self.settings.child('info').setValue(info)
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
        self.controller.set_angle(value)
        self.target_position = value

    def move_rel(self, value):
        """ Move the actuator to the relative target actuator value defined by value

        Parameters
        ----------
        value: (float) value of the relative target value
        """
        value = self.check_bound(self.current_position+value)-self.current_position
        self.target_position = value + self.current_position
        self.controller.set_angle(self.target_position)

    def move_home(self):
        """Call the reference method of the controller"""
        self.controller.set_angle(0)

    def stop_motion(self):
        """Stop the actuator and emits move_done signal"""
        pass


if __name__ == '__main__':
    main(__file__)

