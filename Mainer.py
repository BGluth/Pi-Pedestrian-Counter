__author__ = 'Brendan Gluth'

from ubidots import ApiClient
import RPi.GPIO as GPIO
import time

import UbiConnect

class Mainer:

    unsentDetections = 0
    totalDetections = 0 # Total to date (from Ubidots)

    @staticmethod
    def run():

        # Constants
        const_MotionPin = 7
        const_PedestrianCountKey = '55a6bc6f7625427f55263d11'
        const_AccountKey = '678c47d502499af97147fc3b4b76f45375b6e71d'
        const_UpdateServerPedestrianInterval = 3
        const_UpdateUbidotsTimeInterval = 120 # not used yet
        const_CountStoreLocation = 'Data/LastCount.txt'


        # Set up ubidots connection
        ubiConnection = UbiConnect.UbiConnection(const_AccountKey)
        pedestrianIndex = ubiConnection.addNewVariable(const_PedestrianCountKey)
        print('variable index: ' + str(pedestrianIndex))

        def tryGetPedestrianCountFromServer():
            Mainer.totalDetections = ubiConnection.getVariableFromServer(pedestrianIndex)
            if (Mainer.totalDetections is False):
                print('Failed to get pedestrian count from server. Will try again at a later time.')
                totalDetections = 0
                return False
            return True

        def tryWritePedestrianCountToServer(newCount):
            return ubiConnection.writeVariableToServer(pedestrianIndex, newCount)

        def handleMotionDetected(channel):
            Mainer.unsentDetections += 1
            print("Detection # " + str(Mainer.unsentDetections))
            if (Mainer.unsentDetections % const_UpdateServerPedestrianInterval is 0):
                if (Mainer.totalDetections is 0 and not tryGetPedestrianCountFromServer()): # Have we recieved data from the server yet?
                     print('Failed to read pedestrian detections from Ubidots.')
                     return # Can't connect

                # At this point we have the count from the server
                newTotalDetections = Mainer.totalDetections + Mainer.unsentDetections
                if tryWritePedestrianCountToServer(newTotalDetections):
                    # Succesfully wrote to server
                    print('Added ' + str(newTotalDetections - Mainer.totalDetections) + ' detections to server count.')
                    Mainer.totalDetections = newTotalDetections
                    Mainer.unsentDetections = 0
                else:
                    # TODO: Failed to connect. Store count to a file on disk
                    print("Failed to write new detection count to Ubidots.")


        def programCleanUp():
            GPIO.cleanup()
            #TODO: Write current unsent count to disk


        # Run starts here:
        # Set up pins
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(const_MotionPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(const_MotionPin, GPIO.RISING, handleMotionDetected)


        stop = False

        try:
            # Will make into a nicer menu later.
            while not stop:
                text = raw_input('Press any key to quit.\n')
                stop = True

        except KeyboardInterrupt:
            programCleanUp()

        programCleanUp()


Mainer.run()
