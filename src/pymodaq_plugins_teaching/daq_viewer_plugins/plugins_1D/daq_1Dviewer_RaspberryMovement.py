from threading import Lock
from pathlib import Path
import queue
import tempfile
import time
from typing import List

import numpy as np
from qtpy import QtCore, QtWidgets

from pymodaq.utils.daq_utils import ThreadCommand
from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, comon_parameters, main
from pymodaq.utils.parameter import Parameter
from pymodaq.utils.data import DataFromPlugins, Axis, DataToExport, DataRaw, DataCalculated
from pymodaq.utils.h5modules.saving import H5Saver
from pymodaq.utils.h5modules.data_saving import (DataEnlargeableSaver, DataToExportEnlargeableSaver, DataLoader,
                                                 NodeError)

from pymodaq_plugins_teaching.hardware.raspberry_serial import RaspberryReader, COMPORTS


lock = Lock()


class Frame:
    def __init__(self, data_list: List[float]):
        self.time = data_list[0]
        self.gyroscope = np.array(data_list[1:4])
        self.acceleration = np.array(data_list[4:])


class FrameCallback(QtCore.QObject):
    """

    """
    data_sig = QtCore.Signal()

    def __init__(self, frame_grabber: RaspberryReader, event_queue: queue.Queue):
        super().__init__()
        self.frame_grabber = frame_grabber
        self.event_queue = event_queue
        self._stop = False

    def grab(self, wait_time: int):
        self._stop = False
        while not self._stop:
            try:
                frame = Frame(self.frame_grabber.read_frame())
                self.event_queue.put(frame)
                QtCore.QThread.msleep(wait_time)
                QtWidgets.QApplication.processEvents()
            except Exception as e:
                print(e)
        self.data_sig.emit()

    def stop(self):
        self._stop = True


class DAQ_1DViewer_RaspberryMovement(DAQ_Viewer_base):
    """ Instrument plugin class for a 1D viewer.
    
    This object inherits all functionalities to communicate with PyMoDAQ’s DAQ_Viewer module through inheritance via
    DAQ_Viewer_base. It makes a bridge between the DAQ_Viewer module and the Python wrapper of a particular instrument.

    Attributes:
    -----------
    controller: object
        The particular object that allow the communication with the hardware, in general a python wrapper around the
         hardware library.

    """
    live_mode_available = True

    grabber_start_signal = QtCore.Signal(int)
    grabber_stop_signal = QtCore.Signal()
    saver_start_signal = QtCore.Signal()

    params = comon_parameters+[
        {'title': 'COM Port:', 'name': 'com_port', 'type': 'list', 'value': 'COM21', 'values': COMPORTS},
        {'title': 'Wait time (ms):', 'name': 'wait_time', 'type': 'int', 'value': 10},
        {'title': 'Refresh time (ms):', 'name': 'refresh_time', 'type': 'int', 'value': 1000},
        ]

    def ini_attributes(self):
        self.controller: RaspberryReader = None

        self.h5temp: H5Saver() = None
        self.temp_path: tempfile.TemporaryDirectory = None
        self.saver: DataToExportEnlargeableSaver = None
        self._loader: DataLoader = None

        self.saver_thread: QtCore.QThread = None

        self._queue = queue.Queue()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.process_events)

    def commit_settings(self, param: Parameter):
        """Apply the consequences of a change of value in the detector settings

        Parameters
        ----------
        param: Parameter
            A given parameter (within detector_settings) whose value has been changed by the user
        """
        ## TODO for your custom plugin
        if param.name() == "a_parameter_you've_added_in_self.params":
           self.controller.your_method_to_apply_this_param_change()
#        elif ...
        ##

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

        self.ini_detector_init(old_controller=controller,
                               new_controller=RaspberryReader(self.settings['com_port']))

        callback = FrameCallback(self.controller, self._queue)
        self.callback_thread = QtCore.QThread()  # creation of a Qt5 thread
        callback.moveToThread(self.callback_thread)  # callback object will live within this thread
        callback.data_sig.connect(self.emit_data)

        self.grabber_start_signal.connect(callback.grab)
        self.grabber_stop_signal.connect(callback.stop)
        self.callback_thread.callback = callback

        self.callback_thread.start()

        info = "Whatever info you want to log"
        initialized = True
        return info, initialized

    def close(self):
        """Terminate the communication protocol"""
        self.controller.close()

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
            self.live = kwargs['live']

        if not self.live:
            self.controller.single()
            frame = Frame(self.controller.read_frame())
            data_gyro = DataFromPlugins(name='Raspberry', data=[np.array([dat]) for dat in frame.gyroscope],
                                        dim='Data0D', labels=['Gx', 'Gy', 'Gz'],
                                        )
            data_gyro.timestamp = frame.time

            data_acceleration = DataFromPlugins(name='Raspberry', data=[np.array([dat]) for dat in frame.acceleration],
                                                dim='Data0D', labels=['ax', 'ay', 'az'],
                                                )
            data_acceleration.timestamp = frame.time
            self.dte_signal.emit(DataToExport('myplugin', data=[
                data_gyro, data_acceleration
            ]))
        else:
            self.controller.start()

            if self.h5temp is not None:
                self.h5temp.close()
                self.temp_path.cleanup()
            if self.saver_thread is not None:
                if self.saver_thread.isRunning():
                    self.saver_thread.terminate()
                    while self.saver_thread.isRunning():
                        QtCore.QThread.msleep(100)
                        print('Thread still running')

            self.h5temp = H5Saver(save_type='detector')
            self.temp_path = tempfile.TemporaryDirectory(prefix='pymo')
            addhoc_file_path = Path(self.temp_path.name).joinpath('temp_data.h5')
            self.h5temp.init_file(custom_naming=True, addhoc_file_path=addhoc_file_path)
            self.h5temp.get_set_group('/RawData', 'myframes')
            self.saver: DataToExportEnlargeableSaver = DataToExportEnlargeableSaver(self.h5temp,
                                                                                    axis_name='photon index',
                                                                                    axis_units='index')
            self._loader = DataLoader(self.h5temp)

            self.controller.ind_grabed = -1

            save_callback = SaverCallback(self._queue, self.saver)
            self.saver_thread = QtCore.QThread()
            save_callback.moveToThread(self.saver_thread)
            self.saver_thread.callback = save_callback
            self.saver_start_signal.connect(save_callback.work)
            self.saver_thread.start()

            self.grabber_start_signal.emit(self.settings['wait_time'])
            self.saver_start_signal.emit()
            self.timer.setInterval(self.settings['refresh_time'])
            self.timer.start()

    def emit_data(self):
        pass

    def process_events(self, emit_temp=True):
        try:
            node = self._loader.get_node('/RawData/myframes/Data1D/CH00/EnlData00')
            lock.acquire()
            dwa = self._loader.load_data(node, load_all=True)
            lock.release()
            print(f'Nframes: {dwa.size}')
            # dte = self.compute_positions(dwa)
            # if emit_temp:
            #     self.dte_signal_temp.emit(dte)
            # else:
            #     dwa.add_extra_attribute(save=True, plot=False)
            #     dte.append(dwa)
            #     self.dte_signal.emit(dte)
        except NodeError:
            pass

    def compute_positions(self, dwa: DataRaw) -> DataToExport:
        return DataToExport('Frames', data=[dwa])

    def stop(self):
        """Stop the current grab hardware wise if necessary"""
        self.timer.stop()
        self.controller.stop()
        self.grabber_stop_signal.emit()

        return ''


class SaverCallback(QtCore.QObject):
    def __init__(self, event_queue: queue.Queue, saver: DataToExportEnlargeableSaver):
        super().__init__()
        self.event_queue = event_queue
        self.saver = saver

    def work(self):
        while True:
            frame: Frame = self.event_queue.get()
            data = DataToExport('frames', data=[
                DataRaw('time', data=[frame.gyroscope, frame.acceleration],
                        labels=['gyroscope', 'acceleration'],
                        plot=False,
                        save=True
                        )
            ])
            lock.acquire()
            self.saver.add_data('/RawData/myframes', axis_value=frame.time, data=data)
            lock.release()
            self.event_queue.task_done()



if __name__ == '__main__':
    main(__file__)
