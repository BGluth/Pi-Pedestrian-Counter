__author__ = 'pi'

from ubidots import ApiClient
import RPi.GPIO as GPIO
import time
import Queue

CONST_MotionPin = 7
CONST_CheckDelay = 0.1
CONST_DetectionExtraDelay = 1.5

#noConnectionDetrctions = Queue.Queue()

# Set up pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(CONST_MotionPin, GPIO.IN)

# TODO: Connect to UbiDots account


detectionCounter = 0

stop = False

while not stop:
    motionDetected = GPIO.input(CONST_MotionPin)
    print("Checking for motion...")

    if motionDetected:
        detectionCounter += 1
        motionDetected = False
        print("Detection # " + str(detectionCounter))
        #time.sleep(CONST_DetectionExtraDelay)

    time.sleep(CONST_CheckDelay)
