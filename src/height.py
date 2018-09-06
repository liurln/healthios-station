#!/usr/bin/env python
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import time
import threading
import logging

logging.basicConfig(format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')

STATION_HEIGHT = 195.0


class height_sensor:
    # Hardware: US-015
    # https://www.thaieasyelec.com/downloads/ESEN264/US-020%20Datasheet%20(China).pdf

    TRIGGER_PIN = 23
    ECHO_PIN = 24

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.TRIGGER_PIN, GPIO.OUT)
        GPIO.setup(self.ECHO_PIN, GPIO.IN)
        GPIO.output(self.TRIGGER_PIN, False)
        # Waiting for gpio setup
        time.sleep(0.5)
        logging.info('[Height sensor] Started')

        self.isStart = False
        self.isValid = False
        self.isComplete = False
        self.current_height = 0

    def trigger(self):
        # Turn Trigger pin on for 10us
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

    def read_height(self):
        self.trigger()
        distance_time = self.echo()
        distance = self.timeToDistance(distance_time)
        if distance > 5 and distance < 100:
            return STATION_HEIGHT - round(distance, 2)
        else:
            return 0

    def measure(self):
        height_overall = 0
        counter = 0
        start_time = time.time()
        gap_time = start_time
        while self.thread.stopped is False:
            current_height = self.read_height()
            if current_height != 0:
                counter = counter + 1
                height_overall = height_overall + current_height
                self.isValid = True
                self.current_height = round(
                    height_overall / counter, 2)
                if time.time() - start_time > 10:
                    logging.info('[Height sensor] Finish measurment')
                    self.isComplete = True
                    self.thread.stopped = True
            else:
                if gap_time - start_time > 2:
                    height_overall = 0
                    counter = 0
                    start_time = time.time()
                    gap_time = start_time
                    self.current_height = 0
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
            logging.info('[Height sensor] Starting measurement')

    def stop_measure(self):
        if self.isStart:
            self.isStart = False
            self.thread.stopped = True
            self.current_height = 0
            self.isValid = False
            self.isComplete = False
            logging.info('[Height sensor] Stop measurement')


def main():
    # For testing...
    print('Setup GPIO for US-015')
    myUS015 = height_sensor()
    print('Start measure Distance')
    while True:
        distance = myUS015.measure()
        print('Distance : {}'.format(distance))
        time.sleep(0.1)


if __name__ == '__main__':
    main()
