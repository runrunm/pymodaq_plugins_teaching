import numpy as np
from pymodaq_utils.math_utils import my_moment

from pymodaq_utils.utils import ThreadCommand
from pymodaq_data.data import DataToExport, Axis
from pymodaq_gui.parameter import Parameter

from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, comon_parameters, main
from pymodaq.utils.data import DataFromPlugins

from pymodaq_plugins_teaching.daq_viewer_plugins.plugins_1D.daq_1Dviewer_Spectro import DAQ_1DViewer_Spectro

from pymodaq_plugins_teaching.hardware.spectrometer import Spectrometer

# TODO:
# (1) change the name of the following class to DAQ_1DViewer_TheNameOfYourChoice
# (2) change the name of this file to daq_1Dviewer_TheNameOfYourChoice ("TheNameOfYourChoice" should be the SAME
#     for the class name and the file name.)
# (3) this file should then be put into the right folder, namely IN THE FOLDER OF THE PLUGIN YOU ARE DEVELOPING:
#     pymodaq_plugins_my_plugin/daq_viewer_plugins/plugins_1D


class DAQ_1DViewer_Spectro_Moments(DAQ_1DViewer_Spectro):

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

        spectrum = self.controller.grab_spectrum()
        wl = self.controller.get_wavelength_axis()

        moments = my_moment(wl, spectrum)
        moments_bis = my_moment(spectrum, wl)

        ## TODO for your custom plugin: you should choose EITHER the synchron or the asynchron version following

        ##synchrone version (blocking function)
        data_tot = self.controller.grab_spectrum()
        self.dte_signal.emit(DataToExport('mydte',
                                          data=[DataFromPlugins(name='data_spectro',
                                                                data=[data_tot],
                                                                dim='Data1D',
                                                                labels=['data_spectro'],
                                                                axes=[self.x_axis]),
                                                DataFromPlugins(name='mean',
                                                                data=[np.atleast_1d(moments[0])],
                                                                dim='Data0D'),
                                                DataFromPlugins(name='std',
                                                                data=[np.atleast_1d(moments_bis[1])],
                                                                dim='Data0D')
                                                ]))


        data_x_axis = self.controller.get_wavelength_axis()*1e-9  # if possible
        self.x_axis = Axis(data=data_x_axis, label='wl_axis', units='m', index=0)


if __name__ == '__main__':
    main(__file__)
