#!/usr/bin/evn python
# -*- coding: utf-8 -*-

"""
Author: LIURLN
"""

from __future__ import print_function
import time
import threading
import Adafruit_ADS1x15

# This code is base on tutRPi/Raspberry-Pi-Heartbeat-Pulse-Sensor
# https://github.com/tutRPi/Raspberry-Pi-Heartbeat-Pulse-Sensor


class PulseSensor:
    def __init__(self, channel=0):
        # initial ADS1115 adc moodule
        self.adc = Adafruit_ADS1x15.ADS1015()
        # set gain for voltage reading
        self.GAIN = 1
        # set adc channel for pulse sensor
        self.channel = channel
        # initial pulse data variable
        self.BPM = 0
        self.isValid = False
        self.isComplete = False
        self.isStart = False

    def getBPMData(self):
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
            # print(inputSignal)
            currentTime = int(time.time() * 1000)
            sampleCounter += currentTime - lastTime
            lastTime = currentTime
            N = sampleCounter - lastBeatTime
            # find thought of pulse wave | avoid noise with IBI*3/5
            if inputSignal < thresh and N > (IBI / 5.0) * 3:
                if inputSignal < T:
                    T = inputSignal         # set thought to lowest value
            # find peak of pulse wave
            if inputSignal > thresh and inputSignal > P:
                P = inputSignal

            # print('input {} N {} P {} T {}'.format(inputSignal, N, P, T))
            if N > 250:
                if inputSignal > thresh and Pulse is False and N > (IBI / 5.0) * 3:
                    Pulse = True                    # pulse is detected
                    IBI = sampleCounter - lastBeatTime      # measure beat time
                    lastBeatTime = sampleCounter            # set for next pulse
                    if isStart is False:
                        isStart = True
                        measureTime = lastTime
                    if isStart:
                        if currentTime - measureTime > 2500:
                            self.isValid = True
                        if currentTime - measureTime > 10000:
                            self.isComplete = True
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
                    self.BPM = 60000 / runningTotal

            # reset value when pulse is down
            if inputSignal < thresh and Pulse:
                Pulse = False
                amp = P - T
                thresh = amp / 2 + T
                P = thresh
                T = thresh

            # reset value when pulse not detect for 1.5 sec
            if N > 1500:
                # print('Pulse not detected for 1.5 sec!')
                thresh = 512 * bits
                P = 512 * bits
                T = 512 * bits
                lastBeatTime = sampleCounter
                firstBeat = True
                secondBeat = False
                isStart = False
                measureTime = 0
                self.BPM = 0
                self.isValid = False
                self.isComplete = False

            time.sleep(0.002)

    def startBPMThread(self):
        if not self.isStart:
            self.isStart = True
            self.thread = threading.Thread(target=self.getBPMData)
            self.thread.stopped = False
            # print('-' * 30)
            print('Start BPM thread')
            self.thread.start()
        return

    def stopBPMThread(self):
        if self.isStart:
            self.isStart = False
            self.thread.stopped = True
            self.BPM = 0
            self.isValid = False
            self.isComplete = False
            print('Force stop BPM thread')
        return

    def isValid(self):
        return self.isValid

    def isCompleted(self):
        return self.isComplete

    def getCurrentBPM(self):
        return self.BPM


def main():
    pulseSen = PulseSensor()
    pulseSen.startBPMThread()
    for i in range(0, 100):
        if pulseSen.isValid:
            print('Pulse {}'.format(pulseSen.getCurrentBPM()))
        time.sleep(0.5)

    pulseSen.stopBPMThread()


if __name__ == '__main__':
    main()
