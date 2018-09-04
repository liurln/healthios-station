#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Author: LIURLN
"""

import Adafruit_GPIO.I2C as I2C
import time
import threading


class TemperatureSensor:

    # 0x5A is default address of gy906
    def __init__(self, address=0x5A):
        self._i2c = I2C.Device(address, busnum=1)
        self.isStart = False
        self.isValid = False
        self.isComplete = False
        self.temperature = 0

    def ambientTemp(self):
        return self.readTemperature(0x06)

    def objectTemp(self):
        return self.readTemperature(0x07)

    def readTemperature(self, registerAddress):
        temp = self._i2c.readS16(registerAddress)
        # celsius unit
        temp = (temp * 0.02) - 273.15
        return round(temp, 2)

    def getTempData(self):
        temp_datas = 0
        counter = 0
        startTime = time.time()
        while self.thread.stopped is False:
            tmp = self.objectTemp()
            if tmp > 30 and tmp < 50:
                counter = counter + 1
                temp_datas = temp_datas + tmp
                self.isValid = True
                if time.time() - startTime > 10:
                    self.temperature = round(temp_datas / counter, 2)
                    self.isComplete = True
            else:
                temp_datas = 0
                counter = 0
                self.temperature = 0
                startTime = time.time()
                self.isValid = False
                self.isComplete = False
            time.sleep(0.5)

    def startTempThread(self):
        if not self.isStart:
            self.isStart = True
            self.thread = threading.Thread(target=self.getTempData)
            self.thread.stopped = False
            # print('-' * 30)
            print('Start Temperature thread')
            self.thread.start()
        return

    def stopTempThread(self):
        if self.isStart:
            self.isStart = False
            self.thread.stopped = True
            self.temperature = 0
            self.isValid = False
            self.isComplete = False
            print('Force stop Temperature thread')
        return


def main():
    myGY906 = GY906()
    for x in range(0, 100):
        objectTemp = myGY906.objectTemp()
        ambientTemp = myGY906.ambientTemp()
        print('Object temp: {}C , Ambient: {}C'.format(
            objectTemp, ambientTemp))
        time.sleep(1)


if __name__ == '__main__':
    main()
