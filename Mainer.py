#!/usr/bin/env python

from itertools import combinations

__author__ = 'Brendan Gluth'

import RPi.GPIO as GPIO
import time
import os
import ipgetter
import datetime
import argparse

import UbiConnect

restart = True # Set to True to start the program once

def run():

    # ********** INIT **********
    # Local variables for run
    class State:
        #ubiConnection
        unsentDetections = 0
        totalDetections = 0 # Total to date (from Ubidots)
        pedestrianIndex = 0
        externalIPIndex = 0
        needsSave = False # Do we have new unsent detections to write to file?
        #outputFunction  # Can be either be "print" or a log function (depends on program arguments)

    # Constants
    const_AccountKey = '678c47d502499af97147fc3b4b76f45375b6e71d'
    const_PedestrianCountKey = '55a6bc6f7625427f55263d11'
    const_ExternalIPKey = '55bc22eb7625426f6b807d41'
    
    const_MotionPin = 7
    const_UpdateServerPedestrianInterval = 100
    const_UpdateUbidotsTimeInterval = 120 # not used yet
    const_CountPath = os.path.dirname(__file__) + '/Data/LastCount.txt'
    const_LogPath = os.path.dirname(os.path.abspath(__file__)) + '/Logs/LastLog.txt'
    const_CSVPath = os.path.dirname(os.path.abspath(__file__)) + '/Logs/CSVLog.csv'

    def wrappedPrint(string):
        print(string)

    def log(string):
        makeDirIfNotExists(os.path.dirname(const_LogPath))
        currentDateTime = datetime.datetime.now()
        logFile = open(const_LogPath, mode='a')
        logFile.write('[' + str(currentDateTime) + '] - ' + string + '\n')
        
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--silent', help='Silent mode', action='store_true')
    args = parser.parse_args()

    if args.silent:
        outputFunction = log
    else:
        outputFunction = wrappedPrint

    # ********** END OF INIT **********

    # ********** LOCAL FUNCTIONS **********

    def tryConnectToAccount():
        outputFunction('Trying to Connect to Ubidots account now...')
        if State.ubiConnection.tryAccountConnect(const_AccountKey) is False:
            outputFunction('Failed to connect to account.')
            return False
        else:
            connectUbiVariables()
        updateExternalIP()
        outputFunction('Connected to account!')
        return True

    def tryGetPedestrianCountFromServer():
        State.totalDetections = State.ubiConnection.getVariableFromServer(State.pedestrianIndex)
        if State.totalDetections is False:
            outputFunction('Failed to get pedestrian count from server. Will try again at a later time.')
            return False
        return True

    def tryWritePedestrianCountToServer(newCount):
        return State.ubiConnection.writeVariableToServer(State.pedestrianIndex, newCount)

    def handleMotionDetected(channel):
        writeToCSV()
        State.unsentDetections += 1
        State.needsSave = True
        outputFunction("Detection # " + str(State.totalDetections + State.unsentDetections))

        if State.unsentDetections % const_UpdateServerPedestrianInterval is 0:
            if not State.ubiConnection.accountConnected and tryConnectToAccount() is False:
                writeCountToFile()
                return
            
            if State.totalDetections is 0 and not tryGetPedestrianCountFromServer(): # Have we recieved data from the server yet?
                 outputFunction('Failed to read pedestrian detections from Ubidots.')
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

    def writeCountToFile():
        if not State.needsSave:
            return
        file = open(const_CountPath, mode='w')
        file.write(str(State.unsentDetections))
        State.needsSave = False
        outputFunction('Saved ' + str(State.unsentDetections) + ' unsent detections to file.')

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
        outputFunction('Loaded in ' + str(storedCount) + ' previously unsent detections from last run.')
        return storedCount

    def deleteStoredCountIfExists():
        if os.path.exists(const_CountPath):
            os.remove(const_CountPath)

    def makeDirIfNotExists(directoryPath):
        if not (os.path.exists(directoryPath)):
            os.mkdir(directoryPath)

    def updateExternalIP():
        #TODO: Deal with read and write to server failing
        def convertStringIPToInt(stringIP):
            seperateStrings = stringIP.split('.')
            seperateInts = map((lambda stringPart: int(stringPart)), seperateStrings)
            combinedInts = 1
            for i in range(0, 3):
                combinedInts *= (seperateInts[i] + 1)
            return combinedInts - 1

        currentIP = ipgetter.myip()
        lastIP = State.ubiConnection.getVariableFromServer(State.externalIPIndex)
        if convertStringIPToInt(currentIP) != lastIP:
            if not State.ubiConnection.writeVariableToServer(State.externalIPIndex, convertStringIPToInt(currentIP)):
                outputFunction('Failed to write external IP to Ubidots.')

    def connectUbiVariables():
        State.pedestrianIndex = State.ubiConnection.addNewVariable(const_PedestrianCountKey)
        State.externalIPIndex = State.ubiConnection.addNewVariable(const_ExternalIPKey)

    def programCleanUp():
        outputFunction('Quitting...')
        GPIO.cleanup()
        if State.unsentDetections > 0:
            writeCountToFile()

    # ********** END OF LOCAL FUNCTIONS **********

    # Run starts here:
    makeDirIfNotExists(os.path.dirname(const_CountPath))
    makeDirIfNotExists(os.path.dirname(const_CSVPath))

    # Set up ubidots connection
    State.ubiConnection = UbiConnect.UbiConnection(const_AccountKey, outputFunction)
    tryConnectToAccount()

    # Set up pins
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(const_MotionPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(const_MotionPin, GPIO.RISING, handleMotionDetected)

    # Read in any unsent count from a previous run
    State.unsentDetections = readCountFromFile()

    stop = False

    try:

        # Will make into a nicer menu later.
        while not stop:
            time.sleep(10) # hacky temp fix!

            # text = raw_input('Enter any text to quit.\n')
            #
            # # Menu currently just used for debug
            # if text == 'Debug':
            #     handleMotionDetected(7)
            # elif text == 'Excep':
            #     raise Exception
            # else:
            #     stop = True

        programCleanUp()

    except KeyboardInterrupt:
        programCleanUp()
    except Exception as e:
        outputFunction('The following exception has occured:\n' +e.message + '\n')
        programCleanUp()
        global restart
        restart = True
        outputFunction('Program will restart in 5 seconds.')
        time.sleep(5)


while restart is True:
    restart = False
    run()
