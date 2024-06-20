from qtpy import QtWidgets
import numpy as np

from pymodaq.utils import gui_utils as gutils
from pymodaq.utils.config import Config
from pymodaq.utils.logger import set_logger, get_module_name

from pymodaq.utils.plotting.data_viewers.viewer2D import Viewer2D
from pymodaq.utils.gui_utils.widgets.lcd import LCD
from pymodaq.control_modules.daq_viewer import DAQ_Viewer
from pymodaq.utils.data import DataToExport

# todo: replace here *pymodaq_plugins_template* by your plugin package name
from pymodaq_plugins_teaching.utils import Config as PluginConfig
import laserbeamsize as lbs

logger = set_logger(get_module_name(__file__))

main_config = Config()
plugin_config = PluginConfig()

# todo: modify this as you wish
EXTENSION_NAME = 'Beam Profiler'  # the name that will be displayed in the extension list in the
# dashboard
CLASS_NAME = 'BeamProfiler'  # this should be the name of your class defined below


# todo: modify the name of this class to reflect its application and change the name in the main
# method at the end of the script
class BeamProfiler(gutils.CustomApp):

    # todo: if you wish to create custom Parameter and corresponding widgets. These will be
    # automatically added as children of self.settings. Morevover, the self.settings_tree will
    # render the widgets in a Qtree. If you wish to see it in your app, add is into a Dock
    params = []

    def __init__(self, parent: gutils.DockArea, dashboard):
        super().__init__(parent, dashboard)

        self.setup_ui()

    def setup_docks(self):
        """Mandatory method to be subclassed to setup the docks layout

        Examples
        --------
        >>>self.docks['ADock'] = gutils.Dock('ADock name')
        >>>self.dockarea.addDock(self.docks['ADock'])
        >>>self.docks['AnotherDock'] = gutils.Dock('AnotherDock name')
        >>>self.dockarea.addDock(self.docks['AnotherDock'''], 'bottom', self.docks['ADock'])

        See Also
        --------
        pyqtgraph.dockarea.Dock
        """
        # todo: create docks and add them here to hold your widgets
        # reminder, the attribute self.settings_tree will  render the widgets in a Qtree.
        # If you wish to see it in your app, add is into a Dock
        self.docks['viewer2D'] = gutils.Dock('Camera Data')
        self.dockarea.addDock(self.docks['viewer2D'])
        self.target_viewer = Viewer2D(QtWidgets.QWidget())
        self.docks['viewer2D'].addWidget(self.target_viewer.parent)

        self.docks['lcds'] = gutils.Dock('Beam properties')
        self.dockarea.addDock(self.docks['lcds'], 'right', self.docks['viewer2D'])
        self.lcd = LCD(QtWidgets.QWidget(), Nvals=5, labels=['X', 'Y', 'dx', 'dy', 'theta'])
        self.docks['lcds'].addWidget(self.lcd.parent)

        cam_window = QtWidgets.QMainWindow()
        dockarea = gutils.DockArea()
        cam_window.setCentralWidget(dockarea)
        self.camera_viewer = DAQ_Viewer(dockarea, title='BSCamera', daq_type='DAQ2D')
        self.camera_viewer.detector = 'BSCamera'
        #cam_window.show()

        self.camera_viewer.init_hardware()
        QtWidgets.QApplication.processEvents()

    def setup_actions(self):
        """Method where to create actions to be subclassed. Mandatory
        """
        self.add_action('grab', 'Grab', 'camera', "Grab from camera", checkable=True)
        self.add_action('quit', 'Quit', 'close2', "Quit program")
        self.add_action('show', 'Show/hide', 'read2', "Show Hide DAQViewer", checkable=True)

    def connect_things(self):
        """Connect actions and/or other widgets signal to methods"""
        self.connect_action('grab', self.camera_viewer.grab)
        self.connect_action('quit', self.quit_app)
        self.connect_action('show', self.show_viewer)

        self.camera_viewer.grab_done_signal.connect(self.show_data)

    def show_data(self, dte: DataToExport):
        dte_raw = dte.get_data_from_source('raw')  # to avoid selecting a 2D ROI
        dwa2D = dte_raw.get_data_from_dim('Data2D')[0]  #take the first 2D dwa

        values = [np.array([val]) for val in lbs.beam_size(dwa2D[0])]

        self.target_viewer.show_data(dwa2D)
        self.lcd.setvalues(values)

    def show_viewer(self, do_show: bool):
        self.camera_viewer.parent.parent().setVisible(do_show)

    def quit_app(self):
        self.camera_viewer.quit_fun()
        self.camera_viewer.dockarea.parent().close()
        self.mainwindow.close()

    def setup_menu(self):
        """Non mandatory method to be subclassed in order to create a menubar

        create menu for actions contained into the self._actions, for instance:

        Examples
        --------
        >>>file_menu = self.mainwindow.menuBar().addMenu('File')
        >>>self.affect_to('load', file_menu)
        >>>self.affect_to('save', file_menu)

        >>>file_menu.addSeparator()
        >>>self.affect_to('quit', file_menu)

        See Also
        --------
        pymodaq.utils.managers.action_manager.ActionManager
        """
        # todo create and populate menu using actions defined above in self.setup_actions
        file_menu = self.mainwindow.menuBar().addMenu('File')
        action_menu = self.mainwindow.menuBar().addMenu('Actions')
        self.affect_to('quit', file_menu)
        self.affect_to('grab', action_menu)
        self.affect_to('show', action_menu)

    def value_changed(self, param):
        """ Actions to perform when one of the param's value in self.settings is changed from the
        user interface

        For instance:
        if param.name() == 'do_something':
            if param.value():
                print('Do something')
                self.settings.child('main_settings', 'something_done').setValue(False)

        Parameters
        ----------
        param: (Parameter) the parameter whose value just changed
        """
        pass


def main():
    from pymodaq.utils.gui_utils.utils import mkQApp
    app = mkQApp('CustomApp')

    mainwindow = QtWidgets.QMainWindow()
    dockarea = gutils.DockArea()
    mainwindow.setCentralWidget(dockarea)

    # todo: change the name here to be the same as your app class
    prog = BeamProfiler(dockarea)

    mainwindow.show()

    app.exec()


if __name__ == '__main__':
    main()
