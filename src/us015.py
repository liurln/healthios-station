#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Author: LIURLN
"""

import RPi.GPIO as GPIO
import time


class HeightSensor:
    TRIGGER_PIN = 23
    ECHO_PIN = 24

    def __init__(self):
        # Set gpio mode to BCM
        GPIO.setmode(GPIO.BCM)
        # Set trigger pin as output
        GPIO.setup(self.TRIGGER_PIN, GPIO.OUT)
        # Set echo pin as input
        GPIO.setup(self.ECHO_PIN, GPIO.IN)
        # Set trigger pin state to 0
        GPIO.output(self.TRIGGER_PIN, False)
        # Waiting for gpio setup
        time.sleep(0.5)

    def trigger(self):
        # Start send pulse to trigger pin
        # Trigger pin will on 10us
        GPIO.output(self.TRIGGER_PIN, True)
        # Waiting for 10us
        time.sleep(0.0001)
        GPIO.output(self.TRIGGER_PIN, False)

    def echo(self):
        # Reading incoming pulse on echo pin
        startTime = time.time()
        # Set start timeout
        timeoutTimer = startTime
        while GPIO.input(self.ECHO_PIN) == 0:
            startTime = time.time()
            if (startTime - timeoutTimer) > 0.1:
                return 0

        stopTime = time.time()
        # Set stop timeout
        timeoutTimer = stopTime
        while GPIO.input(self.ECHO_PIN) == 1:
            stopTime = time.time()
            if (stopTime - timeoutTimer) > 0.1:
                return 0

        # Compare range of incoming wave
        elaspedTime = stopTime - startTime
        return elaspedTime

    def timeToDistance(self, elaspedTime):
        # Calculate distance from elasped time
        # Using sound wave velocity - 343 meters / second
        # Divide value with 2 for get true value
        distance = (elaspedTime * 34300) / 2
        return round(distance, 2)

    def measure(self, debug=False):
        distance = 0
        timer = 0
        # Finding average distance form 10 measurement
        while timer < 10:
            self.trigger()
            tmpDistance = self.timeToDistance(self.echo())
            if tmpDistance > 0 and tmpDistance < 200:
                distance = distance + tmpDistance
                timer = timer + 1
            else:
                pass
            time.sleep(0.01)
            if debug:
                print(tmpDistance)

        return round(distance / 10, 2)


def main():
    # For testing...
    print('Setup GPIO for US-015')
    myUS015 = US015()
    print('Start measure Distance')
    while True:
        distance = myUS015.measure()
        print('Distance : {}'.format(distance))
        time.sleep(0.1)


if __name__ == '__main__':
    main()
