import numpy as np

from pymodaq_plugins_teaching.daq_viewer_plugins.plugins_1D.daq_1Dviewer_Spectrum import DAQ_1DViewer_Spectrum
from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, comon_parameters, main

from pymodaq.utils.data import DataFromPlugins, DataToExport, Axis
from pymodaq_utils.math_utils import my_moment


class DAQ_1DViewer_SpectrumAndMoments(DAQ_1DViewer_Spectrum):
    """ Instrument plugin class for a OD viewer.
    
    This object inherits all functionalities to communicate with PyMoDAQ’s DAQ_Viewer module through inheritance via
    DAQ_Viewer_base. It makes a bridge between the DAQ_Viewer module and the Python wrapper of a particular instrument.
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
        ## TODO for your custom plugin: you should choose EITHER the synchrone or the asynchrone version following
        spectrum  =self.controller.grab_spectrum()
        wavelength = self.controller.get_wavelength_axis()


        moments = my_moment(wavelength, spectrum)
        moments_bis = my_moment(spectrum, wavelength, )
        self.dte_signal.emit(DataToExport(
            name='mydte',
            data=[DataFromPlugins(name='Spectrum',
                                  data=[spectrum],
                                  dim='Data1D', labels=['label00',],
                                  axes=[Axis('Wavelength', units='m',
                                             data=wavelength*1e-9)]),
                  DataFromPlugins(name='Moments',
                                  data=[np.atleast_1d(moments[0]),
                                        np.atleast_1d(moments_bis[1])],
                                  dim='Data0D', labels=['mean', 'std',])]))


if __name__ == '__main__':
    main(__file__)
