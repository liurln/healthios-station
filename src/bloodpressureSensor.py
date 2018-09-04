#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Author: LIURLN
"""

import time
import threading
import Adafruit_ADS1x15
import RPi.GPIO as GPIO
import matplotlib.pyplot as plt
import pandas
from scipy.signal import butter, lfilter


class BloodpressureSensor:
    def __init__(self, channel=1):
        # initial ADS1115 adc 16bits modules
        self.adc = Adafruit_ADS1x15.ADS1115()
        self.GAIN = 8
        self.CHANNEL = channel

        self._MOTOR_R = 20
        self._MOTOR_L = 21

        # Set gpio mode to BCM
        GPIO.setmode(GPIO.BCM)
        # Set CLK pin as output
        GPIO.setup(self._MOTOR_R, GPIO.OUT)
        # Set DAT pin as input
        GPIO.setup(self._MOTOR_L, GPIO.OUT)
        time.sleep(0.001)
        GPIO.output(self._MOTOR_R, True)
        GPIO.output(self._MOTOR_L, True)

        self.SYSTOLIC = 0
        self.DIASTOLIC = 0
        self.isValid = False
        self.isComplete = False

    def pumpAir(self, debug=False):
        # Start pump air till pressure for 12 second
        print('Start pump air to cuff')
        if debug:
            GPIO.output(self._MOTOR_R, True)
            GPIO.output(self._MOTOR_L, False)
            time.sleep(12)
            GPIO.output(self._MOTOR_R, True)
            GPIO.output(self._MOTOR_L, True)
        else:
            # pump air until pressure is more than 160mmHg
            GPIO.output(self._MOTOR_R, True)
            GPIO.output(self._MOTOR_L, False)
            while self.getPressure() < 160:
                time.sleep(0.01)
            GPIO.output(self._MOTOR_R, True)
            GPIO.output(self._MOTOR_L, True)
        print('Pumped start measurement...')

    def getPressure(self):
        # raw data will be 0-65535
        rawData = self.adc.read_adc(self.CHANNEL, gain=self.GAIN)
        # convert raw data to pressure (Pa)
        # 0 = 0 Pa | 65535 = 466200 Pa
        # 466200 / 65535 = 7.113756008239872
        #airPressure = rawPressure * 7.113756
        # convert pressure to blood pressure (mmHg)
        # 101325 Pa = 760 mmHg
        # 760 / 101325 = 0.0075006168270417
        #bloodPressure = airPressure * 0.007501
        # convert raw data to voltage level
        voltageInput = rawData * 0.000015625
        voltageCalibrate = voltageInput - 0.2
        airPressure = voltageCalibrate * 155555.55556
        bloodPressure = airPressure / 133.32239
        return round(bloodPressure, 4)

    def averagePressure(self):
        pressureInterval = [0] * 10
        for i in range(10):
            pressureInterval[i] = self.getPressure()
            time.sleep(0.001)
        return round(sum(pressureInterval) / 10, 4)

    def isValid(self):
        return self.isValid

    def isCompleted(self):
        return self.isComplete


class Oscillometric:

    def butterBandpass(self, lowcut, highcut, fs, order=5):
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(order, [low, high], btype='band')
        return b, a

    def butterBandpassFilter(self, data, lowcut, highcut, fs, order=5):
        b, a = self.butterBandpass(lowcut, highcut, fs, order=order)
        y = lfilter(b, a, data)
        return y

    def butterLowpass(self, cutoff, fs, order=5):
        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        return b, a

    def butterLowpassFilter(self, data, cutoff, fs, order=6):
        b, a = self.butterLowpass(cutoff, fs, order=order)
        y = lfilter(b, a, data)
        return y

    def measurement(self, data):
        # Filter raw data with lowpass
        bpLowpass = self.butterLowpassFilter(data, 10, 100, 5)
        # Filter lowpass data with bandpass
        bpBandpass = self.butterBandpassFilter(bpLowpass, 0.25, 5, 100, 5)
        print('Start analyz')
        maximum = 0
        prior = 0
        index = 0
        for i in range(len(data)):
            temp = bpBandpass[i]
            if temp > maximum and (prior - temp) < 0.5:
                maximum = temp
                index = i
                print(prior - temp)
            prior = temp

        mean = bpBandpass[index]
        sys = mean * 1.1
        dia = mean * 0.8
        print('Map: ', mean)
        print('Sys: ', sys)
        print('Dia: ', dia)
        plt.figure(1)
        plt.clf()
        t = []
        for i in range(len(data)):
            t.append(i)
        plt.plot(t, data, label='Raw data')
        plt.plot(t, bpLowpass, label='Lowpass data')
        plt.plot(t, bpBandpass, label='Bandpass data')
        plt.show()


"""
    FOR TESTING...
"""
x = []
y = []
index = 0
for i in range(100):
    x.append(i)
    y.append(0)

myBloodpressureSensor = BloodpressureSensor()
time.sleep(1)

bp = []


def getData():
    print('Getting data...')
    index = 0
    for i in range(1, 100):
        y[i] = myBloodpressureSensor.getPressure()
        bp.append(y[i])
    print(sum(y) / 99)
    while index < 3000:
        y[1:-1] = y[2:]
        y[-1] = myBloodpressureSensor.getPressure()
        bp.append(y[-1])
        index += 1
    df = pandas.DataFrame(bp)
    df.to_csv('bp.csv')
    print('Log writed.')
    osci = Oscillometric()
    osci.measurement(data=bp)


"""
    END PART TESTING...
"""


def main():
    #thread = threading.Thread(target=getData)
    # thread.start()
    myBloodpressureSensor.pumpAir()
    getData()


if __name__ == '__main__':
    main()
