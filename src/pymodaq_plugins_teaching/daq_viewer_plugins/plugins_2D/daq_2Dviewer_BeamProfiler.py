import numpy as np
from qtpy.QtCore import QThread
from qtpy import QtWidgets

from typing import Iterable
import laserbeamsize as lbs

from pymodaq.utils.daq_utils import ThreadCommand
from pymodaq.utils.data import DataFromPlugins, DataToExport
from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, comon_parameters, main
from pymodaq.utils.parameter import Parameter

from pymodaq_plugins_mockexamples.daq_viewer_plugins.plugins_2D.daq_2Dviewer_BSCamera import DAQ_2DViewer_BSCamera


class DAQ_2DViewer_BeamProfiler(DAQ_2DViewer_BSCamera):
    """
    """

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
        if 'live' in kwargs:
            if kwargs['live']:
                self.live = True
                # self.live = False  # don't want to use that for the moment

        if self.live:
            while self.live:
                data = self.average_data(Naverage)  # hardware averaging
                QThread.msleep(kwargs.get('wait_time', 100))
                data.append(self.metrics_from_image(data.data[0].data[0]))
                self.dte_signal.emit(data)
                QtWidgets.QApplication.processEvents()
        else:
            data = self.average_data(Naverage)  # hardware averaging
            QThread.msleep(000)
            data.append(self.metrics_from_image(data.data[0].data[0]))
            self.dte_signal.emit(data)

    def metrics_from_image(self, data_array: np.ndarray) -> Iterable[float]:
        x, y, dx, dy, phi = lbs.beam_size(data_array)
        return DataToExport('metrics', data=[
            DataFromPlugins('Position', data=[np.atleast_1d([x]), np.atleast_1d([y])],
                            labels=['x', 'y']),
            DataFromPlugins('Dimensions', data=[np.atleast_1d([dx]), np.atleast_1d([dy])],
                            labels=['sizex', 'sizey']),
            DataFromPlugins('Rotation', data=[np.atleast_1d([phi * 180 / np.pi])],
                            labels=['Rotation',]),
        ])



if __name__ == '__main__':
    main(__file__)
