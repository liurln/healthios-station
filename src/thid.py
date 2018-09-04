#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Author: LIURLN
"""

import json


class CardInformation:
    thaiFullName = ''
    engFullName = ''
    idNumber = ''
    birthOfDate = ''
    gender = ''
    address = ''

    def __init__(self):
        pass

    def setGender(self, genderData):
        if(genderData == '1'):
            self.gender = 'ชาย'
        elif(genderData == '2'):
            self.gender = 'หญิง'
        else:
            print('Wrong gender data!')

    def clearInformation(self):
        self.thaiFullName = ''
        self.engFullName = ''
        self.idNumber = ''
        self.birthOfDate = ''
        self.gender = ''
        self.address = ''

    def toJson(self):
        jsonData = {}
        jsonData['thaiFullName'] = self.thaiFullName
        jsonData['engFullName'] = self.engFullName
        jsonData['idNumber'] = self.idNumber
        jsonData['birthOfDate'] = self.birthOfDate
        jsonData['gender'] = self.gender
        jsonData['address'] = self.address
        return jsonData


class THIDCommand:
    # THIDCommand is instruction that have to send thought serail port for get
    # information in the card.
    getImage = '\x31\x0D'                   # portrait image
    getAddress = '\x32\x0D'                 # house number
    getThaiFullName = '\x33\x0D'            # Thai full name include prefix
    getCardManu = '\x34\x0D'                # where card was create
    getCardCode = '\x35\x0D'                # code under the card
    getCardExpiredDate = '\x36\x0D'         # card expired date
    getEngFullName = '\x37\x0D'             # English full name
    getBirthOfDate = '\x38\x0D'             # birth of date in B.E.
    getGender = '\x39\x0D'                  # gender 1 for male 2 for female
    getIDNumber = '\x30\x0D'                # Thai indentification number


class THID:
    import serial
    # Open serial port this time THID using ttyUSB1
    # Config serial port with 115200 buad-rate 8N1
    # Note! beware wrong serial port
    thidSerial = serial.Serial('/dev/ttyUSB1', 115200,
                               bytesize=8, parity='N', stopbits=1)
    thidIsOpen = False
    thidIsReadable = False
    thidIsInserted = False
    userInformation = CardInformation()

    def __init__(self):
        # Checking is serial port is open
        if(self.thidSerial.isOpen()):
            print('THID is ready!!!')
            self.thidIsOpen = True

        else:
            try:
                # Try to open serial port
                self.thidSerial.open()
                self.thidIsOpen = True
            except Exception as e:
                print('something wrong : ' + str(e))
                self.thidIsOpen = False

    def readCard(self):
        if(self.thidIsReadable is False):
            print('Insert the card...')
            if(self.listening() == 'INSERTED'):
                if(self.listening() == 'READY'):
                    print('Start read information from card')
                    self.sendCommand(THIDCommand.getIDNumber)
                    self.userInformation.idNumber = self.listening()
                    self.sendCommand(THIDCommand.getEngFullName)
                    self.userInformation.engFullName = self.listening()
                    self.sendCommand(THIDCommand.getThaiFullName)
                    self.userInformation.thaiFullName = self.listening()
                    self.sendCommand(THIDCommand.getGender)
                    self.userInformation.setGender(self.listening())
                    self.sendCommand(THIDCommand.getBirthOfDate)
                    self.userInformation.birthOfDate = self.listening()
                    self.sendCommand(THIDCommand.getAddress)
                    self.userInformation.address = self.listening()
                    # Call read card again for waiting card removed.
                    self.readCard()
        else:
            print('Remove the card')
            while(self.listening() != 'REMOVED'):
                pass

    def sendCommand(self, dataType):
        if(self.thidIsReadable):
            print('Sending command...')
            # Write command to serail port
            self.thidSerial.write(dataType)
        else:
            print('Please check the card!')
            print('--------------------------------------------------')
            return '-'

    def listening(self):
        # listening THID response data
        respData = []
        print('Waiting for response...')
        tmpByte = self.thidSerial.read()
        while(tmpByte != '\r'):
            respData.append(tmpByte)
            tmpByte = self.thidSerial.read()

        # checking response type
        respString = ''.join(respData)
        respLenght = len(respData)
        if(respLenght == 13 and self.thidIsReadable is False):
            print('Card inserted.')
            print('--------------------------------------------------')
            self.thidIsInserted = True
            return 'INSERTED'
        elif(respString == 'READY'):
            print('Card is ready to use.')
            self.thidIsReadable = True
            print('--------------------------------------------------')
            return 'READY'
        elif(respString == 'REMOVE'):
            print('Card removed.')
            self.thidIsReadable = False
            self.thidIsInserted = False
            self.userInformation.clearInformation()
            print('--------------------------------------------------')
            return 'REMOVED'
        elif(respString == 'OK'):
            print('Card is valid.')
            self.thidIsReadable = True
            print('--------------------------------------------------')
            return 'READY'
        elif(respString == 'ERROR'):
            print('Something wrong : invalid instruction!')
            print('--------------------------------------------------')
            return 'ERROR'
        elif(respString == 'CARD'):
            print('Please insert the card!')
            self.thidIsReadable = False
            print('--------------------------------------------------')
            return 'EMPTY'
        elif(respString == 'BUSY'):
            print('THID is busy!')
            print('--------------------------------------------------')
            return 'BUSY'
        elif(respString == 'NO'):
            print('Check dip switch some has turn on!')
            print('--------------------------------------------------')
            return 'DIP'
        else:
            print('**This is information from card')
            print(respString.decode('iso8859_11'))
            print('--------------------------------------------------')
            return respString.decode('iso8859_11')

    def isOpen(self):
        return self.thidIsOpen

    def isReadalbe(self):
        return self.thidIsReadable

    def isInserted(self):
        return self.thidIsInserted

    def getInformation(self):
        return self.userInformation.toJson()


def main():
    myThid = THID()
    if(myThid.isOpen()):
        myThid.readCard()


if __name__ == '__main__':
    main()
