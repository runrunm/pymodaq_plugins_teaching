from collections import OrderedDict
import datetime
import numpy as np

from pymodaq.utils.logger import set_logger, get_module_name
from pymodaq.utils.gui_utils.custom_app import CustomApp
from pymodaq.utils.gui_utils.dock import DockArea, Dock
from  pymodaq.utils.gui_utils.file_io import select_file
from pymodaq.utils.config import Config

from qtpy import QtWidgets

from pymodaq.utils.data import DataToExport

from pymodaq_plugins_teaching.app.beam_profiler import BeamProfiler

import laserbeamsize as lbs
import matplotlib
from matplotlib import pyplot as plt
matplotlib.use("Qt5Agg")

from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg,
    NavigationToolbar2QT as NavigationToolbar,
)
from matplotlib.figure import Figure


config = Config()
logger = set_logger(get_module_name(__file__))


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(fig)


class BeamProfilerMatplotlib(BeamProfiler):

    def setup_docks(self):
        '''
        subclass method from CustomApp
        '''
        super().setup_docks()

        dock_matplotlib = Dock('Matplotlib', size=(350, 350))
        self.dockarea.addDock(dock_matplotlib, 'bottom')
        matplotlib_widget = QtWidgets.QWidget()
        self.matplotlib_canvas = MplCanvas(matplotlib_widget, width=5, height=4, dpi=100)
        dock_matplotlib.addWidget(self.matplotlib_canvas)

    def show_data(self, data: DataToExport):
        """
        do stuff with data from the detector if its grab_done_signal has been connected
        Parameters
        ----------
        data: DataToExport
        """
        self.raw_data = data
        data2D = data.get_data_from_dim('Data2D')
        x, y, dx, dy, phi = lbs.beam_size(data2D[0][0])

        self.target_viewer.show_data(data2D[0])
        self.lcd_position.setvalues([np.array([val]) for val in (x, y)])
        self.lcd_diameter.setvalues([np.array([val]) for val in (dx, dy)])
        self.lcd_angle.setvalues([np.array([phi * 180 / np.pi]) ])

        #plt.figure(self.matplotlib_canvas.figure)

        lbs.plot_image_analysis(data2D[0][0], fig=self.matplotlib_canvas.figure)


    def quit_function(self):
        # close all stuff that need to be
        self.detector.quit_fun()
        QtWidgets.QApplication.processEvents()
        self.mainwindow.close()



def main():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    mainwindow = QtWidgets.QMainWindow()
    dockarea = DockArea()
    mainwindow.setCentralWidget(dockarea)

    prog = BeamProfilerMatplotlib(dockarea)

    mainwindow.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
