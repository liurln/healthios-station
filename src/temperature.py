#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Adafruit_GPIO.I2C as I2C
import time
import threading
import logging

logging.basicConfig(format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')


# 0x5A is I2C address of MLX90614
TEPERATURE_ADDRESS = 0x5A


class temperature_sensor:
    # Hardware: MLX90614
    # https://www.melexis.com/en/product/MLX90614/Digital-Plug-Play-Infrared-Thermometer-TO-Can

    def __init__(self):
        self.setup_i2c()

        self.isStart = False
        self.isValid = False
        self.isComplete = False
        self.current_temperature = 0
        logging.info('[Temperature sensor] started')

    def setup_i2c(self):
        if not self.device_on:
            try:
                self._i2c = I2C.Device(TEPERATURE_ADDRESS, busnum=1)
                self.device_on = True
            except:
                logging.error('[Temperature sensor] cannot start device')
                self.device_on = False

    def measure_ambient(self):
        if self.device_on:
            return self.read_temperature(0x06)
        else:
            self.setup_i2c()
            self.measure_ambient()

    def measure_object(self):
        if self.device_on:
            return self.read_temperature(0x07)
        else:
            self.setup_i2c()
            self.measure_ambient()

    def read_temperature(self, register_address):
        temp = self._i2c.readS16(register_address)
        # celsius unit
        temp = (temp * 0.02) - 273.15
        return round(temp, 2)

    def measure(self):
        teamperature_overall = 0
        counter = 0
        start_time = time.time()
        gap_time = start_time
        while self.thread.stopped is False:
            current_temperature = self.measure_object()
            if current_temperature > 35 and current_temperature < 42:
                counter = counter + 1
                teamperature_overall = teamperature_overall + current_temperature
                self.isValid = True
                self.current_temperature = round(
                    teamperature_overall / counter, 2)

                if time.time() - start_time > 10:
                    logging.info('[Temperature sensor] finish measurment')
                    self.isComplete = True
                    self.thread.stopped = True
            else:
                if gap_time - start_time > 2:
                    teamperature_overall = 0
                    counter = 0
                    start_time = time.time()
                    gap_time = start_time
                    self.current_temperature = 0
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
            logging.info('[Temperature sensor] starting measurement')

    def stop_measure(self):
        if self.isStart:
            self.isStart = False
            self.thread.stopped = True
            self.current_temperature = 0
            self.isValid = False
            self.isComplete = False
            logging.info('[Temperature sensor] stop measurement')


def main():
    myGY906 = temperature_sensor()
    for x in range(0, 100):
        objectTemp = myGY906.measure_object()
        logging.info('Body temperature: {}'.format(objectTemp))
        time.sleep(1)


if __name__ == '__main__':
    main()
