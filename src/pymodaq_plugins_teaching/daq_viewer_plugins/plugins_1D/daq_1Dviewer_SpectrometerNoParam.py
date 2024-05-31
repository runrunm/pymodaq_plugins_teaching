import numpy as np
from pymodaq.utils.daq_utils import ThreadCommand
from pymodaq.utils.data import DataFromPlugins, DataToExport, Axis, DataActuator
from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, comon_parameters, main
from pymodaq.utils.parameter import Parameter
from qtpy import QtWidgets

from pymodaq_plugins_teaching.hardware.spectrometer import Spectrometer
from pymodaq.utils.parameter import utils as putils
from pymodaq_plugins_teaching.daq_viewer_plugins.plugins_2D.daq_2Dviewer_CameraMonochromator import DAQ_2DViewer_CameraMonochromator
from pymodaq_plugins_teaching.daq_move_plugins.daq_move_Monochromator import DAQ_Move_Monochromator


class DAQ_1DViewer_SpectrometerNoParam(DAQ_2DViewer_CameraMonochromator):
    """
    """

    def ini_attributes(self):
        self.controller: Spectrometer = None
        self.monochromator: DAQ_Move_Monochromator = None
        super().ini_attributes()

    def commit_settings(self, param: Parameter):
        """Apply the consequences of a change of value in the detector settings

        Parameters
        ----------
        param: Parameter
            A given parameter (within detector_settings) whose value has been changed by the user
        """
        super().commit_settings(param)

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

        cam_status, cam_init = super().ini_detector(controller)
        QtWidgets.QApplication.processEvents()

        self.monochromator = DAQ_Move_Monochromator()
        self.monochromator.settings.child('multiaxes', 'multi_status').setValue('Slave')
        monochromator_status, monochromator_init = self.monochromator.ini_stage(self.controller)

        QtWidgets.QApplication.processEvents()

        initialized = monochromator_init and cam_init

        return cam_status + monochromator_status, initialized


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
        data_tot = np.mean(self.controller.grab_image(), 0)
        axis_array = self.monochromator.controller.get_wavelength_axis()
        self.dte_signal.emit(
            DataToExport(name='myplugin',
                         data=[DataFromPlugins(name='Spectrum', data=[data_tot],
                                               dim='Data1D', labels=['Spectrum'],
                                               axes=[Axis('wavelength', units='m', data=axis_array)])]))



if __name__ == '__main__':
    main(__file__)
