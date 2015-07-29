__author__ = 'Brendan Gluth'

from ubidots import ApiClient
import RPi.GPIO as GPIO
import time
import os

import UbiConnect

class Mainer:


    _unsentDetections = 0
    _totalDetections = 0 # Total to date (from Ubidots)
    _pedestrianIndex = 0
    _needsSave = False # Do we have new unsent detections to write to file?
    _restart = True # Set to True to start the program once

    @staticmethod
    def run():

        # Constants
        const_MotionPin = 7
        const_PedestrianCountKey = '55a6bc6f7625427f55263d11'
        const_AccountKey = '678c47d502499af97147fc3b4b76f45375b6e71d'
        const_UpdateServerPedestrianInterval = 100
        const_UpdateUbidotsTimeInterval = 120 # not used yet
        const_CountStoreLocation = os.path.dirname(__file__) + '/Data/LastCount.txt'


        # Set up ubidots connection
        ubiConnection = UbiConnect.UbiConnection(const_AccountKey)
        if ubiConnection._accountConnected:
            ubiConnection.addNewVariable(const_PedestrianCountKey)

        def tryConnectToAccount():
            print('Trying to Connect to account now...')
            if ubiConnection.tryAccountConnect(const_AccountKey) is False:
                print('Failed to connect to account.')
                return False
            else:
                Mainer._pedestrianIndex = ubiConnection.addNewVariable(const_PedestrianCountKey)
                print('Connected to account!')
                return True

        def tryGetPedestrianCountFromServer():
            Mainer._totalDetections = ubiConnection.getVariableFromServer(Mainer._pedestrianIndex)
            if Mainer._totalDetections is False:
                print('Failed to get pedestrian count from server. Will try again at a later time.')
                return False
            return True

        def tryWritePedestrianCountToServer(newCount):
            return ubiConnection.writeVariableToServer(Mainer._pedestrianIndex, newCount)

        def handleMotionDetected(channel):
            Mainer._unsentDetections += 1
            Mainer._needsSave = True
            print("Detection # " + str(Mainer._totalDetections + Mainer._unsentDetections))

            if Mainer._unsentDetections % const_UpdateServerPedestrianInterval is 0:
                if not ubiConnection.accountConnected and tryConnectToAccount() is False:
                    writeCountToFile()
                    return

                if Mainer._totalDetections is 0 and not tryGetPedestrianCountFromServer(): # Have we recieved data from the server yet?
                     print('Failed to read pedestrian detections from Ubidots.')
                     writeCountToFile()
                     return # Can't connect

                # At this point we have the count from the server
                newTotalDetections = int(Mainer._totalDetections) + Mainer._unsentDetections
                if tryWritePedestrianCountToServer(newTotalDetections):
                    # Succesfully wrote to server
                    print('Added ' + str(newTotalDetections - int(Mainer._totalDetections)) + ' detections to server count.')
                    Mainer._totalDetections = newTotalDetections
                    Mainer._unsentDetections = 0
                    Mainer._needsSave = False
                    deleteStoredCountIfExists()
                else:
                    print("Failed to write new detection count to Ubidots.")
                    writeCountToFile()

        def writeCountToFile():
            if not Mainer._needsSave:
                return
            directoryPath = os.path.dirname(const_CountStoreLocation)
            if not (os.path.exists(directoryPath)):
                os.mkdir(directoryPath)
            file = open(const_CountStoreLocation, mode='w')
            file.write(str(Mainer._unsentDetections))
            Mainer._needsSave = False
            print ('Saved ' + str(Mainer._unsentDetections) + ' unsent detections to file.')

        def readCountFromFile():
            if not (os.path.exists(const_CountStoreLocation)):
                return 0
            file = open(const_CountStoreLocation, mode='r')
            fileContents = file.readline()
            if fileContents == "": # Rare but could happen if Pi shuts down in the middle of a write
                return 0
            storedCount = int(fileContents)
            file.close()
            print('Loaded in ' + str(storedCount) + ' previously unsent detections from last run.')
            return storedCount

        def deleteStoredCountIfExists():
            if os.path.exists(const_CountStoreLocation):
                os.remove(const_CountStoreLocation)

        def programCleanUp():
            GPIO.cleanup()
            if Mainer._unsentDetections > 0:
                writeCountToFile()

        # Run starts here:
        # Set up pins
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(const_MotionPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(const_MotionPin, GPIO.RISING, handleMotionDetected)

        # Read in any unsent count from a previous run
        Mainer._unsentDetections = readCountFromFile()

        stop = False

        try:
            # Will make into a nicer menu later.
            while not stop:
                text = raw_input('Enter any text to quit.\n')

                # Menu currently just used for debug
                if text == 'Debug':
                    handleMotionDetected(7)
                elif text == 'Excep':
                    raise Exception
                else:
                    stop = True

            programCleanUp()

        except KeyboardInterrupt:
            programCleanUp()
        except Exception, e:
            print('The following exception has occured:\n' +e.message + '\n')
            programCleanUp()
            Mainer._restart = True
            print('Program Will restart in 5 seconds.')
            time.sleep(5)

while Mainer._restart is True:
    Mainer._restart = False
    Mainer.run()
