import numpy as np
import laserbeamsize as lbs

from pymodaq.control_modules.viewer_utility_classes import main

# from pymodaq_plugins_mock.daq_viewer_plugins.plugins_2D.daq_2Dviewer_Mock import DAQ_2DViewer_Mock
from pymodaq_plugins_mockexamples.daq_viewer_plugins.plugins_2D.daq_2Dviewer_BSCamera import DAQ_2DViewer_BSCamera

from pymodaq_data.data import DataToExport, DataCalculated
from pymodaq.utils.data import DataFromPlugins

class DAQ_2DViewer_BeamProfiler(DAQ_2DViewer_BSCamera):
    params = DAQ_2DViewer_BSCamera.params + [
        {'title': 'Beam size', 'name': 'beam_size_settings', 'type': 'group', 'children': [
            {'title': 'Center', 'name': 'center', 'type': 'bool', 'value': True},
            {'title': 'Diameter', 'name': 'diameter', 'type': 'bool', 'value': True},
            {'title': 'φ', 'name': 'phi', 'type': 'bool', 'value': True},
        ]},
    ]

    def grab_data(self, Naverage=1, **kwargs):
        data = self.average_data(Naverage)

        data_array = data.get_data_from_name('BSCamera')[0]

        # Calculation
        x, y, d_major, d_minor, phi = lbs.beam_size(data_array)

        if self.settings['beam_size_settings', 'center']:
            data.append(DataCalculated('center', data=[np.atleast_1d(x), np.atleast_1d(y)],
                                                   labels=['X center', 'Y center']))

        if self.settings['beam_size_settings', 'diameter']:
            data.append(DataCalculated('diameter', data=[np.atleast_1d(d_major), np.atleast_1d(d_minor)],
                                                   labels=['Minor diameter', 'Major diameter']))

        if self.settings['beam_size_settings', 'phi']:
            data.append(DataCalculated('phi', data=[np.atleast_1d(phi)],
                                                   labels=['Phase shift']))

        # peut aussi être: if self.settings.child('beam_size_settings', 'XY').child():

        # data_0d_diameter = DataCalculated('diameter', data=[np.atleast_1d(d_major),
        #                                                     np.atleast_1d(d_minor)],
        #                                               labels=["Minor diameter", "Major diameter"])
        # data_0d_center = DataCalculated('center', data=[np.atleast_1d(x), np.atleast_1d(y)], labels=['X center', 'Y center'])

        self.dte_signal.emit(data)
    
if __name__ == '__main__':
    main(__file__)