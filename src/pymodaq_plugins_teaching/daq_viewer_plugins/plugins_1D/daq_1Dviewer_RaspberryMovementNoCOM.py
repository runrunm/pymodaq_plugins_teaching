import numpy as np
import pandas as pd
import pyins
from pyins.util import GYRO_COLS, ACCEL_COLS

from pymodaq.utils.daq_utils import ThreadCommand
from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, comon_parameters, main
from pymodaq.utils.parameter import Parameter
from pymodaq.utils.data import DataFromPlugins, Axis, DataToExport, DataRaw, DataCalculated
from pymodaq.utils.h5modules.saving import H5Saver
from pymodaq.utils.h5modules.data_saving import (DataEnlargeableSaver, DataToExportEnlargeableSaver, DataLoader,
                                                 NodeError)

from pymodaq_plugins_teaching.hardware.raspberry_serial import data_memory_map


class DAQ_1DViewer_RaspberryMovementNoCOM(DAQ_Viewer_base):
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
        self.controller = None

    def commit_settings(self, param: Parameter):
        """Apply the consequences of a change of value in the detector settings

        Parameters
        ----------
        param: Parameter
            A given parameter (within detector_settings) whose value has been changed by the user
        """
        ## TODO for your custom plugin
        if param.name() == "a_parameter_you've_added_in_self.params":
           self.controller.your_method_to_apply_this_param_change()
#        elif ...
        ##

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

        info = "Whatever info you want to log"
        initialized = True
        return info, initialized

    def close(self):
        """Terminate the communication protocol"""
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

        time = data_memory_map[:, 0]
        gyro = data_memory_map[:, 1:4] * np.pi / 180
        accel = data_memory_map[:, 4:] * 9.8  # m/s²

        trajectory = self.compute_trajectory(time, gyro, accel)


        dwa_positions = DataFromPlugins('positions', data=[trajectory['lat'].to_numpy(),
                                                           trajectory['lon'].to_numpy()],
                                        axes=[Axis('time', 's', data=time)])
        self.dte_signal.emit(DataToExport('Frames', data=[dwa_positions]))

    def compute_trajectory(self, time: np.ndarray, gyro: np.ndarray, accel: np.ndarray):
        index = pd.Index(time, name='time')
        imu = pd.DataFrame(data=np.hstack((gyro, accel)), index=index,
                           columns=GYRO_COLS + ACCEL_COLS)

        increments = pyins.strapdown.compute_increments_from_imu(imu, 'rate')
        integrator = pyins.strapdown.Integrator(pd.Series(data=np.array([0,	0, 0, -0.0, 0.0,
                                                                         -0., 2.30, 1.15, 85.33]),
                                                          index=['lat',	'lon', 'alt', 'VN',	'VE', 'VD', 'roll', 'pitch',
                                                                 'heading']))
        trajectory_computed: pd.DataFrame = integrator.integrate(increments)
        return trajectory_computed

    def stop(self):
        """Stop the current grab hardware wise if necessary"""
        return ''


if __name__ == '__main__':
    main(__file__)
