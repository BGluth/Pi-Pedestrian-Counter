#!/usr/bin/env python

__author__ = 'Brendan Gluth'

#import RPi.GPIO as GPIO
import time
import os
#import ipgetter
import datetime
import argparse

import Utilities
from UbiConnect import UbiConnection
from UbidotsHelper import UbidotsHelper
import TextOutputer

import OutputUtilities

restart = True # Set to True to start the program once
stop = False

# Local variables for run
class State:
    unsentDetections = 0
    totalDetections = 0 # Total to date (from Ubidots)
    pedestrianIndex = 0
    needsSave = False # Do we have new unsent detections to write to file?

def main():
    
    def run():
        
        # ********** LOCAL FUNCTIONS **********

        
        def tryGetXMLValue(dict, key):
            if key not in dict:
                raise Utilities.XMLUnexpectedValue(key + ' was not found in ' + const_UbidotsXMLPath + '!')
            value = dict[key]
            if value == '':
                raise Utilities.XMLUnexpectedValue(key + ' is empty!')
                
            return value
            
        def tryGenerateUbidotsXMLTemplate():
            if not os.path.exists(const_UbidotsXMLPath):
                file = open(const_UbidotsXMLPath, 'w')
                file.write('<data AccountKey="" PedestrianCountKey=""/>')
                file.close()
                TextOutputer.output('Generated UbidotsAccountInfo.xml.')

        def tryConnectToAccount():
            return ubiConnectionHelper.tryConnectToAccount()

        def tryGetPedestrianCountFromServer():
            return ubiConnectionHelper.tryGetVariableFromUbiServer(State.pedestrianCountUbiHandle)

        def tryWritePedestrianCountToServer(newPedestrianCount):
            return ubiConnectionHelper.trySetVariableValueOnUbiServer(State.pedestrianCountUbiHandle, newPedestrianCount)

        def handleMotionDetected(channel):
            try:         
                writeToCSV()
                State.unsentDetections += 1
                State.needsSave = True
                TextOutputer.output("Detection # " + str(State.totalDetections + State.unsentDetections))

                if State.unsentDetections % const_UpdateServerPedestrianInterval is 0:
                    if not ubiConnectionHelper.accountConnected and tryConnectToAccount() is False:
                        writeCountToFile()
                        return
                    
                    if State.totalDetections is 0 and not tryGetPedestrianCountFromServer(): # Have we recieved data from the server yet?
                            writeCountToFile()
                            return # Can't connect

                    # At this point we have the count from the server
                    newTotalDetections = int(State.totalDetections) + State.unsentDetections
                    if tryWritePedestrianCountToServer(newTotalDetections):
                        # Succesfully wrote to server
                        outputFunction('Added ' + str(newTotalDetections - int(State.totalDetections)) + ' detections to server count.')
                        State.totalDetections = newTotalDetections
                        State.unsentDetections = 0
                        State.needsSave = False
                        deleteStoredCountIfExists()
                    else:
                        outputFunction("Failed to write new detection count to Ubidots.")
                        writeCountToFile()
                        
            except Exception as e:
                TextOutputer.output('The following exception has occured:\n' + e.message + '\n')
                global restart
                global stop
                restart = True
                stop = True
                TextOutputer.output('Program will restart in 5 seconds.')
                time.sleep(5)

        def writeCountToFile():
            if not State.needsSave:
                return
            file = open(const_CountPath, mode='w')
            file.write(str(State.unsentDetections))
            State.needsSave = False
            TextOutputer.output('Saved ' + str(State.unsentDetections) + ' unsent detections to file.')

        def writeToCSV():
            file = open(const_CSVPath, 'a')
            file.write(str(str(datetime.datetime.now()) + "\n"))
            file.close()
            
        def readCountFromFile():
            if not (os.path.exists(const_CountPath)):
                return 0
            file = open(const_CountPath, mode='r')
            fileContents = file.readline()
            if fileContents == "": # Rare but could happen if Pi shuts down in the middle of a write
                return 0
            storedCount = int(fileContents)
            file.close()
            TextOutputer.output('Loaded in ' + str(storedCount) + ' previously unsent detections from last run.')
            return storedCount

        def deleteStoredCountIfExists():
            if os.path.exists(const_CountPath):
                os.remove(const_CountPath)

        def connectUbiVariables():
            pedestrianIndex = ubiConnectionHelper.addNewVariable(PedestrianCountKey)

        def programCleanUp():
            TextOutputer.output('Quitting...')
            #GPIO.cleanup()
            if State.unsentDetections > 0:
                writeCountToFile()
                
        # ********** END OF LOCAL FUNCTIONS **********
        
        # ********** INIT **********
        # Local variables for run
        class State:
            #ubiConnection
            unsentDetections = 0
            totalDetections = 0 # Total to date (from Ubidots)
            pedestrianIndex = 0
            #externalIPIndex = 0
            needsSave = False # Do we have new unsent detections to write to file?
            #outputFunction  # Can be either be "print" or a log function (depends on program arguments)
        
        # Constants
        const_MotionPin = 7
        const_UpdateServerPedestrianInterval = 100
        const_UpdateUbidotsTimeInterval = 120 # not used yet
        const_CountPath = os.path.dirname(__file__) + '/../Data/LastCount.txt'
        const_LogPath = os.path.dirname(os.path.abspath(__file__)) + '/../Logs/LastLog.txt'
        const_CSVPath = os.path.dirname(os.path.abspath(__file__)) + '/../Logs/CSVLog.csv'
        const_UbidotsXMLPath = os.path.dirname(os.path.abspath(__file__)) + '/../Data/UbidotsAccountInfo.xml'
        
        # Program Arguments
        parser = argparse.ArgumentParser()
        parser.add_argument('-s', '--silent', help='Silent mode', action='store_true')
        args = parser.parse_args()

        if args.silent:
            TextOutputer.output = OutputUtilities.createLoggingFunction(const_LogPath, useTimeStamp = True)

        # ********** END OF INIT **********

        
        try:
            Utilities.makeDirIfNotExists(os.path.dirname(const_CountPath))
            Utilities.makeDirIfNotExists(os.path.dirname(const_CSVPath))
            Utilities.makeDirIfNotExists(os.path.dirname(const_UbidotsXMLPath))
        
            # Load in Ubidots account info
            tryGenerateUbidotsXMLTemplate()
            values = Utilities.readInXMLValues(const_UbidotsXMLPath)  
            
            AccountKey = tryGetXMLValue(values, 'AccountKey')
            PedestrianCountKey = tryGetXMLValue(values, 'PedestrianCountKey')
            
            # Set up ubidots connection
            ubiConnectionHelper = UbidotsHelper(UbiConnection(AccountKey));
            ubiConnectionHelper.tryConnectToAccount()

            # Set up pins
            #GPIO.setmode(GPIO.BCM)
            #GPIO.setup(const_MotionPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            #GPIO.add_event_detect(const_MotionPin, GPIO.RISING, handleMotionDetected)

            # Read in any unsent count from a previous run
            State.unsentDetections = readCountFromFile()
            
            global stop
            stop = False
            
            # Will make into a nicer menu later.
            while not stop:
                #time.sleep(5) # hacky temp fix!
                
                 # For debugging
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
        except Utilities.XMLUnexpectedValue as e:
            programCleanUp()
            TextOutputer.output('The following exception has occured:\n' + e.message + '\n')
            TextOutputer.output('Make sure ' + const_UbidotsXMLPath + ' exists and is formatted correctly!')

    global restart
    
    while restart is True:
        restart = False
        run()

# Common python hack to force everything to be defined before any code is called.
if __name__ == "__main__":
    main()
