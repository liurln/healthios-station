#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Author: LIURLN
"""

from pyfingerprint import PyFingerprint
import time
import urllib2

LINEWIDTH = 50


class Fingerprint:

    def __init__(self):
        # Set fingerprint sensor to ttyUSB0 with buadrate 57600
        self.fingerprintSensor = PyFingerprint(
            '/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)
        # Flag for checking sensor available
        self.fingerprintSensorValid = False
        self.fingerprintTemplateValid = False
        self.fingerprintCharValid = False
        self.verify()

    def verify(self):
        # Verify fingerprintsensor
        try:
            if(self.fingerprintSensor.verifyPassword() is False):
                print('Fingerprint password is wrong!')

            self.fingerprintSensorValid = True
            print('Fingerprint sensor is available!')
        except Exception as e:
            print('Something wrong : ' + str(e))

        print('-' * LINEWIDTH)

    def createTemplate(self):
        if(self.fingerprintSensorValid):
            try:
                time.sleep(2)
                print('Waiting for finger...')
                # wait for finger
                while(self.fingerprintSensor.readImage() is False):
                    pass
                print('Finger read.')
                print('Start convert fingerprint image...')
                self.fingerprintSensor.convertImage(0x01)
                print('Converted.')
                time.sleep(2)
                # double check
                # waiting for finger remove
                while(self.fingerprintSensor.readImage()):
                    pass
                print('Waiting for finger...')
                # wait for finger
                while(self.fingerprintSensor.readImage() is False):
                    pass
                print('Finger read.')
                print('Start convert fingerprint image...')
                self.fingerprintSensor.convertImage(0x02)
                print('Converted.')
                print('Create fingerprint template...')
                self.fingerprintSensor.createTemplate()
                print('Created.')
                print('Download fingerprint template...')
                self.fingerprintTemplate = self.fingerprintSensor.downloadCharacteristics()
                self.fingerprintTemplateValid = True
            except Exception as e:
                print('Something wrong : ' + str(e))
        print('-' * LINEWIDTH)

    def scanOneTime(self):
        if(self.fingerprintSensorValid):
            try:
                self.fingerprintCharValid = False
                print('Waiting for finger...')
                # wait for finger
                startTime = time.time()
                timeout = False
                while(self.fingerprintSensor.readImage() is False and timeout is False):
                    if time.time() - startTime > 20:
                        timeout = True
                print('Finger read.')
                # print('Start convert fingerprint image...')
                self.fingerprintSensor.convertImage(0x01)
                # print('Converted.')
                # print('Download fingerprint characteristic...')
                self.fingerprintChar = self.fingerprintSensor.downloadCharacteristics()
                self.fingerprintCharValid = True
                self.fingerptintCompare = False
                self.fingerptintCompareValid = False
                self.userID = 0
            except Exception as e:
                print('Something wrong : ' + str(e))
        print('-' * LINEWIDTH)

    def fetchAllFingerprint(self):
        # fetch all fingerprint from web database
        fetchEndPoint = "htt]://203.154.59.215:8080/api/data/fingerprint"
        res = urllib2.urlopen(fetchEndPoint)
        content = res.content
        pass

    def compare(self):
        if self.fingerprintCharValid:
            # upload template to address 0x02
            self.fingerprintSensor.uploadCharacteristics(
                0x02, self.fingerprintTemplate)
            score = self.fingerprintSensor.compareCharacteristics()
            if score > 0:
                self.fingerptintCompare = True
                self.userID = 1111111111111
            self.fingerptintCompareValid = True

    def downloadImage(self):
        if(self.fingerprintSensorValid):
            try:
                print('Waiting for finger...')
                # wait for finger
                while(self.fingerprintSensor.readImage() is False):
                    pass

                # save fingerprint image
                print('Saving fingerprint image...')
                self.fingerprintSensor.downloadImage(
                    '/home/pi/healthios/img/fingerprint_img.png')
                print('Fingerprint saved!')
            except Exception as e:
                print('Something wrong : ' + str(e))
        print('-' * LINEWIDTH)


def main():
    myFingerprintSensor = Fingerprint()
    myFingerprintSensor.createTemplate()
    time.sleep(2)
    myFingerprintSensor.scanOneTime()
    ss = time.time()
    myFingerprintSensor.compare()
    print time.time() - ss


if __name__ == '__main__':
    main()
