#!/usr/bin/evn python
# -*- coding: utf-8 -*-

import time
import numpy
try:
    import RPi.GPIO as GPIO
except ImportError:
    import fake_rpi.GPIO as GPIO
import threading
import logging

logging.basicConfig(format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')


class weight_sensor:
    def __init__(self, dat=27, clk=22, gain=128):
        self._DAT = dat
        self._CLK = clk

        self.GAIN = 0
        self.REFERENCE = 1
        self.OFFSET = 1
        self.lastVal = 0

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._CLK, GPIO.OUT)
        GPIO.setup(self._DAT, GPIO.IN)
        self.set_gain(gain)
        time.sleep(0.5)

        self.isStart = False
        self.isValid = False
        self.isComplete = False
        self.current_weight = 0

        logging.info('[Weight sensor] started')

        self.reset()

    def set_gain(self, gain):
        if gain is 128:
            self.GAIN = 1
        elif gain is 64:
            self.GAIN = 3
        elif gain is 32:
            self.GAIN = 2

        GPIO.output(self._CLK, False)
        self.read_raw()

    def set_offset(self, offset):
        self.OFFSET = offset

    def set_reference_unit(self, referenceUnit):
        self.REFERENCE = referenceUnit

    def is_ready(self):
        return GPIO.input(self._DAT) == 0

    def read_raw(self):
        while self.is_ready() is False:
            pass

        # use for store HX711 24 bits data
        # seperate data to 3 bytes
        dataBits = [[False] * 8, [False] * 8, [False] * 8]
        dataBytes = [0x0] * 4

        for j in range(2, -1, -1):
            for i in range(7, -1, -1):
                GPIO.output(self._CLK, True)
                dataBits[j][i] = GPIO.input(self._DAT)
                GPIO.output(self._CLK, False)
            # convert 8 bits data to 1 byte
            dataBytes[j] = numpy.packbits(numpy.uint8(dataBits[j]))

        for i in range(self.GAIN):
            GPIO.output(self._CLK, True)
            GPIO.output(self._CLK, False)

        dataBytes[2] ^= 0x80

        return dataBytes

    def read_long(self):
        # convert uint8 to uint32
        dataBytes = self.read_raw()
        arro8 = numpy.uint8(dataBytes)
        longVal = arro8.view('uint32')
        self.lastVal = longVal
        return longVal

    def read_average(self, time=10):
        value = 0
        for i in range(time):
            value += self.read_long()

        return round(value / time, 2)

    def get_weight(self):
        self.reset()
        weight = self.read_average() - self.OFFSET
        weight = weight / self.REFERENCE
        self.reset()
        return weight

    def calibrate(self):
        # calibrate offset value
        # store old reference to temp
        tmpReferenceUnit = self.REFERENCE
        self.set_reference_unit(1)
        offsetValue = self.read_average(15)
        self.set_offset(offsetValue)
        self.set_reference_unit(tmpReferenceUnit)
        logging.info(
            '[Weight sensor] calibrated , offset value: {}'.format(offsetValue))

    def reset(self):
        # reset hk711 state
        GPIO.output(self._CLK, False)
        GPIO.output(self._CLK, True)
        time.sleep(0.0001)
        GPIO.output(self._CLK, False)
        time.sleep(0.0001)

    def measure(self):
        weight_overall = 0
        counter = 0
        start_time = time.time()
        gap_time = start_time
        while self.thread.stopped is False:
            current_weight = self.get_weight()
            if current_weight > 20 and current_weight < 100:
                counter = counter + 1
                weight_overall = weight_overall + current_weight
                self.isValid = True
                self.current_weight = round(
                    weight_overall / counter, 2)
                if time.time() - start_time > 10:
                    logging.info('[Weight sensor] finish measurment')
                    self.isComplete = True
                    self.thread.stopped = True
            else:
                if gap_time - start_time > 2:
                    weight_overall = 0
                    counter = 0
                    start_time = time.time()
                    gap_time = start_time
                    self.current_weight = 0
                    self.isValid = False
                else:
                    gap_time = time.time()
            time.sleep(0.25)

    def start_measure(self):
        if not self.isStart:
            self.isStart = True
            self.thread = threading.Thread(target=self.measure)
            self.thread.stopped = False
            self.thread.start()
            logging.info('[Weight sensor] starting measurement')

    def stop_measure(self):
        if self.isStart:
            self.isStart = False
            self.thread.stopped = True
            self.current_weight = 0
            self.isValid = False
            self.isComplete = False
            logging.info('[Weight sensor] stop measurement')


def main():
    myWeightSensor = weight_sensor()
    myWeightSensor.calibrate()
    time.sleep(5)
    myWeightSensor.get_weight()


if __name__ == '__main__':
    main()
