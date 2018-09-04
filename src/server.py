#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Author: LIURLN
"""

from flask import Flask
from flask_cors import CORS
from thid import THID
import threading
import json
from fingerprintSensor import Fingerprint

from hx711 import WeightSensor
from us015 import HeightSensor
from pulseSensor import PulseSensor
from gy906 import TemperatureSensor

app = Flask(__name__)
CORS(app)
thidSensor = THID()
fingerprintSensor = Fingerprint()
threads = []

weightS = WeightSensor()
heightS = HeightSensor()
pulseS = PulseSensor()
tmepS = TemperatureSensor()


@app.route("/", methods=['GET'])
def hello():
    return 'Welcome to Healthios!'


@app.route("/thid/valid", methods=['GET'])
def thidValidCheck():
    res = {}
    # Call THID to check card inserted
    res['status'] = thidSensor.isInserted()
    return json.dumps(res)


@app.route("/thid/readable", methods=['GET'])
def thidReadableCheck():
    res = {}
    # Call THID to check card inserted
    res['status'] = thidSensor.isReadalbe()
    return json.dumps(res)


@app.route("/thid/", methods=['GET'])
def thidGetData():
    res = {}
    # Call THID to get all data in card
    res['status'] = thidSensor.isReadalbe()
    res['data'] = thidSensor.getInformation()
    return json.dumps(res)


@app.route("/thid/start", methods=['GET'])
def thidStartThread():
    if checkRunningThread('THID') is False:
        t = threading.Thread(name='THID', target=thidThread)
        threads.append(t)
        t.start()

    res = {}
    res['status'] = thidSensor.isOpen()
    return json.dumps(res)


@app.route("/finger/valid/template", methods=['GET'])
def fingerprintTemplateValidCheck():
    res = {}
    # Call THID to check card inserted
    res['status'] = fingerprint.fingerprintTemplateValid
    return json.dumps(res)


@app.route("/finger/start/template", methods=['GET'])
def fingerprintStartCreateTemplate():
    res = {}
    # Call THID to check card inserted
    if fingerprint.fingerprintTemplateValid is False:
        t = threading.Thread(name='THID', target=fingerprintThread)
        threads.append(t)
        t.start()
    res['status'] = True
    return json.dumps(res)


@app.route("/finger/template", methods=['GET'])
def fingerprintValidCheck():
    res = {}
    # Call THID to check card inserted
    res['status'] = fingerprint.fingerprintTemplateValid
    res['data'] = fingerprint.fingerprintTemplate
    return json.dumps(res)


@app.route("/finger/valid/scan", methods=['GET'])
def fingerprintScanValidCheck():
    res = {}
    # Call THID to check card inserted
    res['status'] = fingerprint.fingerprintCharValid
    return json.dumps(res)


@app.route("/finger/start/scan", methods=['GET'])
def fingerprintStartScan():
    res = {}
    # Call THID to check card inserted
    if fingerprint.fingerprintTemplateValid is False:
        t = threading.Thread(name='THID', target=fingerprintThread2)
        threads.append(t)
        t.start()
    res['status'] = True
    return json.dumps(res)


@app.route("/finger/valid/compare", methods=['GET'])
def fingerprintCompareValidCheck():
    res = {}
    # Call THID to check card inserted
    res['status'] = fingerprint.fingerptintCompareValid
    return json.dumps(res)


@app.route("/finger/start/compare", methods=['GET'])
def fingerprintStartCompare():
    res = {}
    # Call THID to check card inserted
    if fingerprint.fingerprintTemplateValid is False:
        t = threading.Thread(name='THID', target=fingerprintThread3)
        threads.append(t)
        t.start()
    res['status'] = True
    return json.dumps(res)


@app.route("/finger/", methods=['GET'])
def fingerprintGetData():
    res = {}
    # Call THID to get all data in card
    res['status'] = thidSensor.fingerptintCompareValid
    res['data'] = thidSensor.userID
    return json.dumps(res)


@app.route("/pulse/", methods=['GET'])
def pulseGetData():
    res = {}
    res['valid'] = pulseS.isValid
    res['finish'] = pulseS.isComplete
    res['data'] = pulseS.getCurrentBPM()
    return json.dumps(res)


@app.route("/pulse/valid", methods=['GET'])
def pulseValidCheck():
    # Call pulseSensor for check user is using
    res = {}
    if pulseS.isValid:
        res['status'] = True
    else:
        res['status'] = False
    return json.dumps(res)


@app.route("/pulse/finish", methods=['GET'])
def pulseIsComplete():
    # Call pulseSensor for check finish checking
    res = {}
    if pulseS.isComplete:
        pulseS.stopBPMThread()
        res['status'] = True
    else:
        res['status'] = False
    return json.dumps(res)


@app.route("/pulse/start", methods=['GET'])
def pulseStart():
    pulseS.startBPMThread()
    res = {}
    res['status'] = True
    return json.dumps(res)


@app.route("/thermal/", methods=['GET'])
def thermalGetData():
    res = {}
    res['valid'] = tmepS.isValid
    res['finish'] = tmepS.isComplete
    res['data'] = tmepS.temperature
    return json.dumps(res)


@app.route("/thermal/valid", methods=['GET'])
def thermalValidCheck():
    # Call thermalSensor for check user is using
    res = {}
    res['status'] = tmepS.isValid
    return json.dumps(res)


@app.route("/thermal/finish", methods=['GET'])
def thermalIsComplete():
    # Call thermalSensor for check finish checking
    res = {}
    if tmepS.isComplete:
        tmepS.stopTempThread()
        res['status'] = True
    else:
        res['status'] = False
    return json.dumps(res)


@app.route("/thermal/start", methods=['GET'])
def thermalStart():
    # Call thermalSensor for check finish checking
    tmepS.startTempThread()
    res = {}
    res['status'] = True
    return json.dumps(res)


@app.route("/pressure/", methods=['GET'])
def pressureGetData():
    res = {}
    res['valid'] = True
    res['finish'] = True
    data = [60, 80, 130]
    res['data'] = data
    return json.dumps(res)


@app.route("/pressure/valid", methods=['GET'])
def pressureValidCheck():
    # Call pressureSensor for check user is using
    res = {}
    res['status'] = True
    return json.dumps(res)


@app.route("/pressure/finish", methods=['GET'])
def pressureIsComplete():
    # Call pressureSensor for check finish checking
    res = {}
    res['status'] = True
    return json.dumps(res)


@app.route("/pressure/start", methods=['GET'])
def pressureStart():
    # Call pressureSensor for check finish checking
    res = {}
    res['status'] = True
    return json.dumps(res)


@app.route("/weight/", methods=['GET'])
def weightGetData():
    res = {}
    res['valid'] = True
    res['finish'] = True
    res['data'] = 66.5
    return json.dumps(res)


@app.route("/weight/valid", methods=['GET'])
def weightValidCheck():
    # Call weightSensor for check user is using
    res = {}
    res['status'] = True
    return json.dumps(res)


@app.route("/weight/finish", methods=['GET'])
def weightIsComplete():
    # Call weightSensor for check finish checking
    res = {}
    res['status'] = True
    return json.dumps(res)


@app.route("/weight/start", methods=['GET'])
def weightStart():
    # Call weightSensor for check finish checking
    res = {}
    res['status'] = True
    return json.dumps(res)


@app.route("/height/", methods=['GET'])
def heightGetData():
    res = {}
    res['valid'] = True
    res['finish'] = True
    res['data'] = 176.5
    return json.dumps(res)


@app.route("/height/valid", methods=['GET'])
def heightValidCheck():
    # Call heightSensor for check user is using
    res = {}
    res['status'] = True
    return json.dumps(res)


@app.route("/height/finish", methods=['GET'])
def heightIsComplete():
    # Call heightSensor for check finish checking
    res = {}
    res['status'] = True
    return json.dumps(res)


@app.route("/height/start", methods=['GET'])
def heightStart():
    # Call heightSensor for check finish checking
    res = {}
    res['status'] = True
    return json.dumps(res)


def thidThread():
    print('--------------------------------------------------')
    print('Start Thead THID!')
    thidSensor.readCard()
    print('Exit Thread THID!')
    print('--------------------------------------------------')


def fingerprintThread():
    print('--------------------------------------------------')
    print('Start Thead FINGERPRINT TEMPLATE!')
    fingerprint.createTemplate()
    print('Exit Thread FINGERPRINT TEMPLATE!')
    print('--------------------------------------------------')


def fingerprintThread2():
    print('--------------------------------------------------')
    print('Start Thead FINGERPRINT TEMPLATE!')
    fingerprint.scanOneTime()
    print('Exit Thread FINGERPRINT TEMPLATE!')
    print('--------------------------------------------------')


def fingerprintThread3():
    print('--------------------------------------------------')
    print('Start Thead FINGERPRINT TEMPLATE!')
    fingerprint.compare()
    print('Exit Thread FINGERPRINT TEMPLATE!')
    print('--------------------------------------------------')


def checkRunningThread(threadType):
    for thread in threads:
        if thread.name == threadType:
            if thread.is_alive() is False:
                print('Thread is end')
                threads.remove(thread)
                return False
            return True

    return False


def main():
    app.run('0.0.0.0', port=54322)


if __name__ == '__main__':
    main()
