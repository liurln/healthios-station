#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Author: LIURLN
"""

from pyfingerprint.pyfingerprint import PyFingerprint

# Set fingerprint sensor to ttyUSB0 with buadrate 57600
fingerprintSensor = PyFingerprint(
    '/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)
# Flag for checking sensor available
fingerprintSensorStateFlag = False


def verify():
    # Verify fingerprintsensor
    global fingerprintSensorStateFlag
    try:
        if(fingerprintSensor.verifyPassword() is False):
            print('Fingerprint password is wrong!')

        fingerprintSensorStateFlag = True
        print('Fingerprint sensor is available!')
    except Exception as e:
        print('Something wrong : ' + str(e))


def scan():
    if(fingerprintSensorStateFlag):
        try:
            print('Waiting for finger...')
            # wait for finger
            while(fingerprintSensor.readImage() is False):
                pass

            # save fingerprint image
            print('Saving fingerprint image...')
            fingerprintSensor.downloadImage(
                '/home/pi/healthios/img/fingerprint_img.bmp')
            print('Fingerprint saved!')
        except Exception as e:
            print('Something wrong : ' + str(e))


def main():
    verify()
    scan()


if __name__ == '__main__':
    main()
