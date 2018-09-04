#!/usr/bin/evn python
# -*- coding: utf-8 -*-

"""
Author: LIURLN
"""

import time
import numpy
try:
    import RPi.GPIO as GPIO
except ImportError:
    import fake_rpi.GPIO as GPIO

# FOR DEV
# import FakseRPi use only in DEV env
# import importlib.util
# try:
#     importlib.util.find_spec('RPi.GPIO')
#     import RPi.GPIO as GPIO
# except:
#     import FakeRPi.GPIO as GPIO

LINEWIDTH = 100


class WeightSensor:
    def __init__(self, dat=27, clk=22, gain=128):
        self._DAT = dat
        self._CLK = clk
        self.GAIN = 0
        self.REFERENCE = 1
        self.OFFSET = 1
        self.lastVal = 0

        # Set gpio mode to BCM
        GPIO.setmode(GPIO.BCM)
        # Set CLK pin as output
        GPIO.setup(self._CLK, GPIO.OUT)
        # Set DAT pin as input
        GPIO.setup(self._DAT, GPIO.IN)
        # Set trigger pin state to 0
        self.setGain(gain)
        time.sleep(0.5)
        self.reset()
        print('## WEIGHT SENSOR HK711 STARTED')
        print('-' * LINEWIDTH)

    def setGain(self, gain):
        if gain is 128:
            self.GAIN = 1
        elif gain is 64:
            self.GAIN = 3
        elif gain is 32:
            self.GAIN = 2

        GPIO.output(self._CLK, False)
        self.readRaw()

    def setOffset(self, offset):
        self.OFFSET = offset

    def setReferenceUnit(self, referenceUnit):
        self.REFERENCE = referenceUnit

    def isReady(self):
        return GPIO.input(self._DAT) == 0

    def readRaw(self):
        while self.isReady() is False:
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

    def readLong(self):
        # convert uint8 to uint32
        dataBytes = self.readRaw()
        arro8 = numpy.uint8(dataBytes)
        longVal = arro8.view('uint32')
        self.lastVal = longVal
        return longVal

    def readAverage(self, time=10):
        value = 0
        for i in range(time):
            value += self.readLong()

        return round(value / time, 2)

    def getWeight(self):
        self.reset()
        weight = self.readAverage() - self.OFFSET
        weight = weight / self.REFERENCE
        print('> this is information for testing...')
        print('> WEIGHT: {}'.format(weight))
        print('-' * LINEWIDTH)
        self.reset()
        return weight

    def tare(self):
        # calibrate offset value
        print('START CALIBRATE 0 GRAM...')
        # store old reference to temp
        tmpReferenceUnit = self.REFERENCE
        self.setReferenceUnit(1)
        offsetValue = self.readAverage(15)
        print('> OFFSET : {}'.format(offsetValue))
        self.setOffset(offsetValue)
        self.setReferenceUnit(tmpReferenceUnit)
        print('> CALIBRATED')
        print('-' * LINEWIDTH)

    def reset(self):
        # reset hk711 state
        GPIO.output(self._CLK, False)
        GPIO.output(self._CLK, True)
        time.sleep(0.0001)
        GPIO.output(self._CLK, False)
        time.sleep(0.0001)


def main():
    myWeightSensor = WeightSensor()
    myWeightSensor.tare()
    time.sleep(5)
    myWeightSensor.getWeight()


if __name__ == '__main__':
    main()
