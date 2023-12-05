import time
from pathlib import Path
from threading import Thread, Event

import numpy as np
import serial
from serial import Serial, SerialTimeoutException
from serial.tools.list_ports import comports


COMPORTS_INFO = comports()
COMPORTS = [comport.device for comport in COMPORTS_INFO]

here = Path(__file__).parent.parent
data_memory_map = np.load(here.joinpath('resources/shortwalk.npy'), mmap_mode='r')


class Frame:
    def __init__(self, frame_array: np.ndarray):
        self.frame = frame_array

    def to_str(self):
        return ' '.join([str(arr) for arr in self.frame])

    def __repr__(self):
        return self.to_str()


class FrameYielder:
    ind_grabbed = 0

    def __init__(self):
        self._frame_grabber = self._grabber()

    def _grabber(self):
        while self.ind_grabbed < data_memory_map.shape[0]:
            next_grab = 1
            ind_grabbed = self.ind_grabbed
            self.ind_grabbed += next_grab
            print(self.ind_grabbed)
            yield np.atleast_1d(np.squeeze(data_memory_map[ind_grabbed:ind_grabbed+next_grab, ...]))

    def grab(self) -> Frame:
        return Frame(next(self._frame_grabber))


class RaspberrySerial:

    def __init__(self, com_port: str = None, timeout: int = 1, **kwargs):

        self.controller = Serial()

        for key, value in kwargs:
            if hasattr(self.controller, key):
                setattr(self.controller, key, value)

        self.controller.timeout = timeout

        if com_port is not None:
            self.controller.port = com_port
            self.open()

    def open(self, com_port: str = None):
        if com_port is not None:
            self.controller.port = com_port
        self.controller.open()

    def close(self):
        if self.controller.is_open:
            self.controller.close()

    @property
    def _write(self):
        return self.controller.write

    @property
    def _read(self):
        return self.controller.read

    def _readline(self) -> bytes:
        return self.controller.readline()


class RaspberryReader(RaspberrySerial):

    def start(self):
        self._write(b'START\n')

    def stop(self):
        self._write(b'STOP\n')

    def single(self):
        self._write(b'READ\n')

    def read_frame(self):
        try:
            answer: str = self._readline().decode()
            answer = answer.strip()
            answer = answer.split(' ')
            answer = [float(ans) for ans in answer]
            return answer
        except (SerialTimeoutException, TypeError, ValueError) as e:
            return ''


class RaspberryWriter(RaspberrySerial):

    def __init__(self, com_port: str = None, timeout: int = 1, **kwargs):
        super().__init__(com_port, timeout=0.100, **kwargs)

        self.thread: Thread = None
        self._event = Event()
        self.frame_yielder = FrameYielder()

    @property
    def is_running(self):
        return self._event.is_set()

    @is_running.setter
    def is_running(self, status: bool):
        if status:
            self._event.set()
        else:
            self._event.clear()

    def poll(self) -> bool:

        try:
            command: str = self._readline().decode()
            command = command.strip()
            if command != '':
                print(f'The received command is: {command}')
            if command == 'START':
                self._start()

            elif command == 'STOP':
                self._stop()
                return False

            elif command == 'READ':
                self._send_data()

            return True

        except SerialTimeoutException:
            pass

    def _start(self):
        self.is_running = True
        self.thread = Thread(None, self._send_data_all)
        self.thread.start()

    def _stop(self):
        self.is_running = False

    def _send_data(self):
        self._write(f'{self.frame_yielder.grab().to_str()}\n'.encode())

    def _send_data_all(self):
        while self.is_running:
            self._send_data()
            time.sleep(0.000)


def main_reader_all():
    reader = RaspberryReader('COM21')
    try:
        reader.start()
        for _ in range(50):
            print(reader.read_frame())
        reader.stop()
    except Exception as e:
        print(e)
    finally:
        reader.close()


def main_reader():
    reader = RaspberryReader('COM21')
    try:
        for _ in range(10):
            reader.single()
            print(reader.read_frame())
    except Exception as e:
        print(e)
    finally:
        reader.close()


def main_writer():
    writer = RaspberryWriter('COM22')
    try:
        while True:
            writer.poll()
            time.sleep(0.05)
    except Exception as e:
        print(e)
    finally:
        writer.close()


