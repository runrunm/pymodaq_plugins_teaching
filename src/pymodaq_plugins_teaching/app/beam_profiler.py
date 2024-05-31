from collections import OrderedDict
import datetime
import numpy as np

from pymodaq.utils.logger import set_logger, get_module_name
from pymodaq.utils.gui_utils.custom_app import CustomApp
from pymodaq.utils.gui_utils.dock import DockArea, Dock
from  pymodaq.utils.gui_utils.file_io import select_file
from pymodaq.utils.config import Config

from qtpy import QtWidgets
from qtpy.QtCore import Slot, QDate, QThread

from pymodaq.utils import daq_utils as utils
from pymodaq.utils.parameter import ioxml
from pymodaq.control_modules.daq_viewer import DAQ_Viewer
from pymodaq.utils.plotting.data_viewers.viewer2D import Viewer2D
from pymodaq.utils.gui_utils.widgets.lcd import LCD

from pymodaq.utils.h5modules.browsing import H5Browser
from pymodaq.utils.h5modules.saving import H5Saver
from pymodaq.utils.h5modules.data_saving import DataToExportSaver
from pymodaq.utils.data import DataToExport

import laserbeamsize as lbs

config = Config()
logger = set_logger(get_module_name(__file__))


class BeamProfiler(CustomApp):

    # list of dicts enabling the settings tree on the user interface
    params = [
    ]

    def __init__(self, dockarea):

        super().__init__(dockarea)

        # init the object parameters
        self.raw_data: DataToExport = None
        self.setup_ui()

    def setup_actions(self):
        '''
        subclass method from ActionManager
        '''
        logger.debug('setting actions')
        self.add_action('quit', 'Quit', 'close2', "Quit program", toolbar=self.toolbar)
        self.add_action('grab', 'Grab', 'camera', "Grab from camera", checkable=True,
                        toolbar=self.toolbar)
        self.add_action('save', 'Save', 'SaveAs', "Save current data", checkable=False,
                        toolbar=self.toolbar)
        self.add_action('show', 'Show/hide', 'read2', "Show Hide DAQViewer", checkable=True,
                        toolbar=self.toolbar)

        logger.debug('actions set')

    def setup_docks(self):
        '''
        subclass method from CustomApp
        '''
        logger.debug('setting docks')
        # create a dock containing a viewer object, could be 0D, 1D or 2D depending what kind of data one want to plot here a 0D
        dock_viewer_2D = Dock('Viewer dock', size=(350, 350))
        self.dockarea.addDock(dock_viewer_2D,)
        target_widget = QtWidgets.QWidget()
        self.target_viewer = Viewer2D(target_widget)
        dock_viewer_2D.addWidget(target_widget)

        dock_lcd_position = Dock('Beam position', size=(350, 350))
        self.dockarea.addDock(dock_lcd_position, 'right', dock_viewer_2D)
        lcd_widget_position = QtWidgets.QWidget()
        dock_lcd_position.addWidget(lcd_widget_position)
        self.lcd_position = LCD(lcd_widget_position, Nvals=2, labels=['x', 'y'])

        dock_lcd_diameter = Dock('Beam diameter', size=(350, 350))
        self.dockarea.addDock(dock_lcd_diameter, 'bottom', dock_lcd_position)
        lcd_widget_diameter = QtWidgets.QWidget()
        dock_lcd_diameter.addWidget(lcd_widget_diameter)
        self.lcd_diameter = LCD(lcd_widget_diameter, Nvals=2, labels=['dx', 'dy'])

        dock_lcd_angle = Dock('Beam angle', size=(350, 350))
        self.dockarea.addDock(dock_lcd_angle, 'bottom', dock_lcd_diameter)
        lcd_widget_angle = QtWidgets.QWidget()
        dock_lcd_angle.addWidget(lcd_widget_angle)
        self.lcd_angle = LCD(lcd_widget_angle, Nvals=1, labels=['angle'])

        self.daq_viewer_area = DockArea()
        self.detector = DAQ_Viewer(self.daq_viewer_area,  title="A detector")

        # set its type to 'BSCamera'
        self.detector.daq_type = 'DAQ2D'
        self.detector.detector = 'BSCamera'
        # init the detector and wait 1000ms for the completion
        self.detector.init_hardware()
        self.detector.settings.child('main_settings', 'wait_time').setValue(100)
        QtWidgets.QApplication.processEvents()
        QThread.msleep(1000)

        logger.debug('docks are set')

    def connect_things(self):
        '''
        subclass method from CustomApp
        '''
        logger.debug('connecting things')
        self.log_signal[str].connect(self.add_log)  # connect together this custom signal with the add_log method

        self.detector.grab_done_signal.connect(self.data_done)
        self.connect_action('quit', self.quit_function)
        self.connect_action('save', self.save_data)

        self.connect_action('grab', self.detector.grab)
        self.connect_action('show', self.show_detector)

        self.detector.grab_done_signal.connect(self.show_data)
        logger.debug('connecting done')

    def show_detector(self, status):
        self.daq_viewer_area.setVisible(status)

    def setup_menu(self):
        '''
        subclass method from CustomApp
        '''
        logger.debug('settings menu')
        file_menu = self.mainwindow.menuBar().addMenu('File')
        self.affect_to('quit', file_menu)
        file_menu.addSeparator()
        self.affect_to('save', file_menu)

        self.affect_to('quit', file_menu)

        logger.debug('menu set')

    def value_changed(self, param):
        logger.debug(f'calling value_changed with param {param.name()}')
        pass

        logger.debug(f'Value change applied')

    def data_done(self, data):
        # print(data)
        pass

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

    def quit_function(self):
        # close all stuff that need to be
        self.detector.quit_fun()
        QtWidgets.QApplication.processEvents()
        self.mainwindow.close()

    def run_detector(self):
        self.detector.ui.grab_pb.click()

    def save_data(self):
        try:
            path = select_file(start_path=self.settings.child('main_settings', 'base_path').value(), save=True,
                                                                   ext='h5')
            if path is not None:
                # init the file object with an addhoc name given by the user
                h5saver = H5Saver(save_type='custom')
                h5saver.init_file(update_h5=True, addhoc_file_path=path)
                datasaver = DataToExportSaver(h5saver)


                # save all metadata
                settings_str = ioxml.parameter_to_xml_string(self.settings)
                settings_str = b'<All_settings>' + settings_str
                settings_str += ioxml.parameter_to_xml_string(self.detector.settings) + ioxml.parameter_to_xml_string(
                    h5saver.settings) + b'</All_settings>'

                datasaver.add_data(h5saver.root(), self.raw_data, settings_as_xml=settings_str)

                h5saver.close_file()

                st = 'file {:s} has been saved'.format(str(path))
                self.add_log(st)
                self.settings.child('main_settings', 'info').setValue(st)

        except Exception as e:
            logger.exception(str(e))

    @Slot(str)
    def add_log(self, txt):
        """
            Add a log to the logger list from the given text log and the current time

            ================ ========= ======================
            **Parameters**   **Type**   **Description**

             *txt*             string    the log to be added
            ================ ========= ======================

        """
        now = datetime.datetime.now()
        new_item = QtWidgets.QListWidgetItem(str(now) + ": " + txt)
        self.logger_list.addItem(new_item)
        logger.info(txt)


def main():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    mainwindow = QtWidgets.QMainWindow()
    dockarea = DockArea()
    mainwindow.setCentralWidget(dockarea)

    prog = BeamProfiler(dockarea)

    mainwindow.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
