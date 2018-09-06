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

from weight import weight_sensor
from height import height_sensor
from pulse import pulse_sensor
from temperature import temperature_sensor

app = Flask(__name__)
CORS(app)
thidSensor = THID()
fingerprintSensor = Fingerprint()
threads = []

weight_sens = weight_sensor()
height_sens = height_sensor()
pulse_sens = pulse_sensor()
temperature_sens = temperature_sensor()


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
    res['status'] = fingerprintSensor.fingerprintTemplateValid
    return json.dumps(res)


@app.route("/finger/start/template", methods=['GET'])
def fingerprintStartCreateTemplate():
    res = {}
    # Call THID to check card inserted
    if fingerprintSensor.fingerprintTemplateValid is False:
        t = threading.Thread(name='THID', target=fingerprintThread)
        threads.append(t)
        t.start()
    res['status'] = True
    return json.dumps(res)


@app.route("/finger/template", methods=['GET'])
def fingerprintValidCheck():
    res = {}
    # Call THID to check card inserted
    res['status'] = fingerprintSensor.fingerprintTemplateValid
    res['data'] = fingerprintSensor.fingerprintTemplate
    return json.dumps(res)


@app.route("/finger/valid/scan", methods=['GET'])
def fingerprintScanValidCheck():
    res = {}
    # Call THID to check card inserted
    res['status'] = fingerprintSensor.fingerprintCharValid
    return json.dumps(res)


@app.route("/finger/start/scan", methods=['GET'])
def fingerprintStartScan():
    res = {}
    # Call THID to check card inserted
    if fingerprintSensor.fingerprintTemplateValid is False:
        t = threading.Thread(name='THID', target=fingerprintThread2)
        threads.append(t)
        t.start()
    res['status'] = True
    return json.dumps(res)


@app.route("/finger/valid/compare", methods=['GET'])
def fingerprintCompareValidCheck():
    res = {}
    # Call THID to check card inserted
    res['status'] = fingerprintSensor.fingerptintCompareValid
    return json.dumps(res)


@app.route("/finger/start/compare", methods=['GET'])
def fingerprintStartCompare():
    res = {}
    # Call THID to check card inserted
    if fingerprintSensor.fingerprintTemplateValid is False:
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
    res['valid'] = pulse_sens.isValid
    res['finish'] = pulse_sens.isComplete
    res['data'] = pulse_sens.current_bpm
    return json.dumps(res)


@app.route("/pulse/valid", methods=['GET'])
def pulseValidCheck():
    # Call pulseSensor for check user is using
    res = {}
    if pulse_sens.isValid:
        res['status'] = True
    else:
        res['status'] = False
    return json.dumps(res)


@app.route("/pulse/finish", methods=['GET'])
def pulseIsComplete():
    # Call pulseSensor for check finish checking
    res = {}
    if pulse_sens.isComplete:
        pulse_sens.stop_measure()
        res['status'] = True
    else:
        res['status'] = False
    return json.dumps(res)


@app.route("/pulse/start", methods=['GET'])
def pulseStart():
    pulse_sens.start_measure()
    res = {}
    res['status'] = True
    return json.dumps(res)


@app.route("/thermal/", methods=['GET'])
def thermalGetData():
    res = {}
    res['valid'] = temperature_sens.isValid
    res['finish'] = temperature_sens.isComplete
    res['data'] = temperature_sens.current_temperature
    return json.dumps(res)


@app.route("/thermal/valid", methods=['GET'])
def thermalValidCheck():
    # Call thermalSensor for check user is using
    res = {}
    res['status'] = temperature_sens.isValid
    return json.dumps(res)


@app.route("/thermal/finish", methods=['GET'])
def thermalIsComplete():
    # Call thermalSensor for check finish checking
    res = {}
    if temperature_sens.isComplete:
        temperature_sens.stop_measure()
        res['status'] = True
    else:
        res['status'] = False
    return json.dumps(res)


@app.route("/thermal/start", methods=['GET'])
def thermalStart():
    # Call thermalSensor for check finish checking
    temperature_sens.start_measure()
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
    res['valid'] = weight_sens.isValid
    res['finish'] = weight_sens.isComplete
    res['data'] = weight_sens.current_weight
    return json.dumps(res)


@app.route("/weight/valid", methods=['GET'])
def weightValidCheck():
    # Call weightSensor for check user is using
    res = {}
    res['status'] = weight_sens.isValid
    return json.dumps(res)


@app.route("/weight/finish", methods=['GET'])
def weightIsComplete():
    # Call weightSensor for check finish checking
    res = {}
    res['status'] = weight_sens.isComplete
    return json.dumps(res)


@app.route("/weight/start", methods=['GET'])
def weightStart():
    # Call weightSensor for check finish checking
    res = {}
    weight_sens.start_measure()
    res['status'] = True
    return json.dumps(res)


@app.route("/height/", methods=['GET'])
def heightGetData():
    res = {}
    res['valid'] = height_sens.isValid
    res['finish'] = height_sens.isComplete
    res['data'] = height_sens.current_height
    return json.dumps(res)


@app.route("/height/valid", methods=['GET'])
def heightValidCheck():
    # Call heightSensor for check user is using
    res = {}
    res['status'] = height_sens.isValid
    return json.dumps(res)


@app.route("/height/finish", methods=['GET'])
def heightIsComplete():
    # Call heightSensor for check finish checking
    res = {}
    res['status'] = height_sens.isComplete
    return json.dumps(res)


@app.route("/height/start", methods=['GET'])
def heightStart():
    # Call heightSensor for check finish checking
    res = {}
    height_sens.start_measure()
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
    fingerprintSensor.createTemplate()
    print('Exit Thread FINGERPRINT TEMPLATE!')
    print('--------------------------------------------------')


def fingerprintThread2():
    print('--------------------------------------------------')
    print('Start Thead FINGERPRINT TEMPLATE!')
    fingerprintSensor.scanOneTime()
    print('Exit Thread FINGERPRINT TEMPLATE!')
    print('--------------------------------------------------')


def fingerprintThread3():
    print('--------------------------------------------------')
    print('Start Thead FINGERPRINT TEMPLATE!')
    fingerprintSensor.compare()
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
