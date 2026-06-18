import numpy as np
import laserbeamsize as lbs

from pymodaq.extensions.data_mixer.model import DataMixerModel
from pymodaq_data.data import DataToExport, DataCalculated

class DataMixerBeamProfiler(DataMixerModel):

    def process_dte(self, data: DataToExport):
        dte_processed = DataToExport('center')

        data_array = data.get_data_from_name('BSCamera')[0]

        x, y, d_major, d_minor, phi = lbs.beam_size(data_array)


        if True:
            dte_processed.append(DataCalculated('center', data=[np.atleast_1d(x), np.atleast_1d(y)],
                                                   labels=['X center', 'Y center']))

        if True:
            dte_processed.append(DataCalculated('diameter', data=[np.atleast_1d(d_major), np.atleast_1d(d_minor)],
                                                   labels=['Minor diameter', 'Major diameter']))

        if True:
            dte_processed.append(DataCalculated('phi', data=[np.atleast_1d(phi)],
                                                   labels=['Phase shift']))

        
        return dte_processed