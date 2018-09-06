#!/usr/bin/evn python
# -*- coding: utf-8 -*-

"""
Author: LIURLN
"""

from __future__ import print_function
import time
import threading
import Adafruit_ADS1x15
import logging

logging.basicConfig(format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')


class pulse_sensor:
    # This code is base on tutRPi/Raspberry-Pi-Heartbeat-Pulse-Sensor
    # https://github.com/tutRPi/Raspberry-Pi-Heartbeat-Pulse-Sensor
    def __init__(self, channel=0):
        # initial ADS1115 adc moodule
        self.adc = Adafruit_ADS1x15.ADS1015()
        # set gain for voltage reading
        self.GAIN = 1
        # set adc channel for pulse sensor
        self.channel = channel
        # initial pulse data variable
        self.current_bpm = 0
        self.isValid = False
        self.isComplete = False
        self.isStart = False

        logging.info('[Pulse sensor] started')

    def read_bpm(self):
        rate = [0] * 10         # array hold last 10 IBI values
        sampleCounter = 0       # used to determine pulse timing
        lastBeatTime = 0        # used to find IBI value
        bits = 2
        P = 512 * bits
        T = 512 * bits
        thresh = 512 * bits
        amp = 100
        firstBeat = True
        secondBeat = False

        IBI = 600
        Pulse = False           # True : heartbeat is detected
        lastTime = int(time.time() * 1000)

        isStart = False
        measureTime = 0

        while self.thread.stopped is False:
            inputSignal = self.adc.read_adc(self.channel, gain=self.GAIN)
            currentTime = int(time.time() * 1000)
            sampleCounter += currentTime - lastTime
            lastTime = currentTime
            time_gap = sampleCounter - lastBeatTime
            # find thought of pulse wave | avoid noise with IBI*3/5
            if inputSignal < thresh and time_gap > (IBI / 5.0) * 3:
                if inputSignal < T:
                    T = inputSignal         # set thought to lowest value
            # find peak of pulse wave
            if inputSignal > thresh and inputSignal > P:
                P = inputSignal

            # print('input {} time_gap {} P {} T {}'.format(inputSignal, time_gap, P, T))
            if time_gap > 250:
                if inputSignal > thresh and Pulse is False and time_gap > (IBI / 5.0) * 3:
                    Pulse = True                    # pulse is detected
                    IBI = sampleCounter - lastBeatTime      # measure beat time
                    lastBeatTime = sampleCounter            # set for next pulse

                    # initial IBI array with same value
                    if secondBeat:
                        secondBeat = False
                        for i in range(len(rate)):
                            rate[i] = IBI

                    if firstBeat:
                        firstBeat = False
                        secondBeat = True
                        continue

                    # shift left IBI array for next pulse
                    rate[:-1] = rate[1:]
                    rate[-1] = IBI
                    runningTotal = sum(rate)
                    runningTotal /= len(rate)
                    self.current_bpm = 60000 / runningTotal

                    if isStart is False:
                        isStart = True
                        measureTime = lastTime
                    else:
                        if currentTime - measureTime > 2500:
                            self.isValid = True
                            logging.info('[Pulse sensor] pulse detected')
                        if currentTime - measureTime > 10000:
                            self.isComplete = True
                            self.thread.stopped = True
                            logging.info('[Pulse sensor] finish measurement')

            # reset value when pulse is down
            if inputSignal < thresh and Pulse:
                Pulse = False
                amp = P - T
                thresh = amp / 2 + T
                P = thresh
                T = thresh

            # reset value when pulse not detect for 1.5 sec
            if time_gap > 1500:
                thresh = 512 * bits
                P = 512 * bits
                T = 512 * bits
                lastBeatTime = sampleCounter
                firstBeat = True
                secondBeat = False
                isStart = False
                measureTime = 0
                self.current_bpm = 0
                self.isValid = False
                self.isComplete = False
                logging.info('[Pulse sensor] pulse disappeared')

            time.sleep(0.002)

    def start_measure(self):
        if not self.isStart:
            self.isStart = True
            self.thread = threading.Thread(target=self.read_bpm)
            self.thread.stopped = False
            logging.info('[Pulse sensor] starting measurement')
            self.thread.start()

    def stop_measure(self):
        if self.isStart:
            self.isStart = False
            self.thread.stopped = True
            self.current_bpm = 0
            self.isValid = False
            self.isComplete = False
            logging.info('[Pulse sensor] starting measurement')


def main():
    pulseSen = pulse_sensor()
    pulseSen.start_measure()
    for i in range(0, 100):
        if pulseSen.isValid:
            print('Pulse {}'.format(pulseSen.getCurrentBPM()))
        time.sleep(0.5)

    pulseSen.stop_measure()


if __name__ == '__main__':
    main()
