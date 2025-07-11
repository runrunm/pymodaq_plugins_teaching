import numpy as np

from pyqtgraph.parametertree import Parameter

from qtpy import QtWidgets
from typing import Optional

from pymodaq_gui.utils.dock import Dock, DockArea
from pymodaq_gui.plotting.data_viewers.viewer1D import Viewer1D, DataToExport, DataWithAxes

from pymodaq.control_modules.daq_viewer import DAQ_Viewer, DAQTypesEnum

from pymodaq.extensions.utils import CustomExt
from pymodaq_plugins_teaching.utils import Config as PluginConfig

plugin_config = PluginConfig()

EXTENSION_NAME = 'Generator'  # the name that will be displayed in the extension list in the dashboard
CLASS_NAME = 'GenExt'  # this should be the name of your class defined below


class GenExt(CustomExt):

    params = [
        {'title': 'Frequency', 'name': 'frequency', 'type': 'slide', 'value': 10, 'default': 10, 'limits': (1, 1000), 'subtype': 'linear'},
    ]


    def __init__(self, parent, dashboard):
        super().__init__(parent, dashboard)

        self.viewer1D_raw: Optional[Viewer1D] = None
        self.viewer1D_fft: Optional[Viewer1D] = None

        self.daq_viewer: DAQ_Viewer = self.modules_manager.get_mod_from_name("Generator")

        self.dwa_raw: Optional[DataWithAxes] = None

        self.setup_ui()


    def setup_docks(self):
        self.docks['raw_viewer'] = Dock('Raw Viewer', autoOrientation=False)
        self.docks['fft_viewer'] = Dock('FFT Viewer')
        self.docks['parameters'] = Dock('Parameters', autoOrientation=False)

        self.docks['fft_viewer'].hideTitleBar()

        self.dockarea.addDock(self.docks['raw_viewer'], 'right')
        self.dockarea.addDock(self.docks['fft_viewer'], 'bottom', self.docks['raw_viewer'])
        self.dockarea.addDock(self.docks['parameters'], 'left')


        self.viewer1D_raw = Viewer1D(QtWidgets.QWidget())
        self.docks['raw_viewer'].addWidget(self.viewer1D_raw.parent)  # parent for accessing QWidget (for adding in dock)

        self.viewer1D_fft = Viewer1D(QtWidgets.QWidget())
        self.docks['fft_viewer'].addWidget(self.viewer1D_fft.parent)


        dockarea = DockArea()
        main_window = QtWidgets.QMainWindow()
        main_window.setCentralWidget(dockarea)

        self.docks['parameters'].addWidget(self.settings_tree)

        self.daq_viewer.settings.child('main_settings', 'wait_time').setValue(50)  # ('child', 'subchild', 'subsubchild')
        self.daq_viewer.snap()

        self.dashboard.mainwindow.setVisible(False)


    def setup_actions(self):
        self.add_action('snap', 'Snap Data', 'Snapshot2_32', tip="Click to get one data shot")
        self.add_action('grab', 'Grab Data', 'run_all', tip="Click to continuously grab data", checkable=True)
        self.add_action('show', 'Show/Hide Viewer', 'read2', tip="Show/Hide the DAQ_Viewer panel", checkable=True)

    def connect_things(self):
        # self.daq_viewer.grab_done_signal.connect(lambda dte: self.viewer1D_raw.show_data(dte[0]))
        self.daq_viewer.grab_done_signal.connect(self.get_dwa_and_show)

        self.connect_action('snap', self.daq_viewer.snap)
        self.connect_action('grab', self.daq_viewer.grab)
        self.connect_action('show', self.dashboard.mainwindow.setVisible)

        # self.connect_action('frequency_changed', )


    def get_dwa_and_show(self, dte=DataToExport):
        self.dwa_raw = dte[0]
        self.viewer1D_raw.show_data(self.dwa_raw)

        self.dwa_fft = self.dwa_raw.ft()
        self.viewer1D_fft.show_data(abs(self.dwa_fft))
    
    def value_changed(self, param: Parameter):
        if param.name() == "frequency":
            self.daq_viewer.settings.child('detector_settings', 'frequency').setValue(param.value())

def main():
    from pymodaq_gui.utils.utils import mkQApp
    from pymodaq.utils.gui_utils.loader_utils import load_dashboard_with_preset

    app = mkQApp('GenExt')

    preset_file_name = plugin_config('defaults', 'preset')
    dashboard, extension, win = load_dashboard_with_preset(preset_file_name, EXTENSION_NAME)
    app.exec()

    return dashboard, extension, win

if __name__ == '__main__':
    main()