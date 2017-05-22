import numpy as np
import re
import csv


# Handles the input buffer and writes sensor values to a file when recording
class DataProcessor:
    n = 10
    m = 6
    minRecordAcceleration = 1.5

    def __init__(self):
        self.buffer = np.ndarray(shape=(self.n, self.m), dtype=float)
        self.buffer.fill(0)
        self.arrayPointer = 0
        self.recState = RecordState()

    # insert raw data string into the buffer. Data will be parsed based on x,y,z,alpha,beta,gamma as float values
    def put_raw(self, raw_data):
        self.buffer[self.arrayPointer] = re.findall(r'[-+]?\d*\.\d+|\d+', raw_data)

        if self.recState.is_prepared() and not self.recState.is_recording and \
                (np.amax(self.buffer[self.arrayPointer]) >= self.minRecordAcceleration or abs(np.amin(self.buffer[self.arrayPointer])) >= self.minRecordAcceleration):
            self.recState.record(self.arrayPointer)

        self._inc_array_pointer()
        if self.recState.is_recording and self.arrayPointer == self.recState.start_idx:
            self.write_buffer_to_csv()
            self.clean()

    def _inc_array_pointer(self):
        self.arrayPointer = (self.arrayPointer + 1) % self.n

    def write_buffer_to_csv(self):
        data = self.get_flat_buffer()
        data = np.append(data, [self.recState.gesture_id])
        with open(r'raw/sensor_data.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow(data)

    def clean(self):
        self.buffer.fill(0)
        self.arrayPointer = 0
        self.recState.reset()

    def prepare_recording(self, gid):
        self.recState.prepare_recording(gid)

    def get_flat_buffer(self):
        out_array = np.array([])
        out_array = np.append(out_array, np.roll(self.buffer.flatten(), self.n * self.m - self.arrayPointer))
        return out_array


class RecordState:

    def __init__(self):
        self.is_recording = False
        self.gesture_id = -1
        self.start_idx = -1

    def reset(self):
        self.is_recording = False
        self.gesture_id = -1
        self.start_idx = -1

    def prepare_recording(self, gid):
        self.gesture_id = gid

    def is_prepared(self):
        return self.gesture_id >= 0

    def record(self, start_idx):
        self.is_recording = True
        self.start_idx = start_idx
