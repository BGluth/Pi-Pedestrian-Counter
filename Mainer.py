__author__ = 'pi'

from ubidots import ApiClient
import RPi.GPIO as GPIO
import time
#import Queue

class Mainer:
    detectionCounter = 0

    @staticmethod
    def run():
        def handleMotionDetected(channel):
            Mainer.detectionCounter += 1
            print("Detection # " + str(Mainer.detectionCounter))

        def programCleanUp():
            GPIO.cleanup()



        const_MotionPin = 7

        # noConnectionDetrctions = Queue.Queue()

        # TODO: Connect to UbiDots account

        # Set up pins
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(const_MotionPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(const_MotionPin, GPIO.RISING, handleMotionDetected)

        stop = False

        try:
            while not stop:

                text = raw_input('Press any key to quit.\n')
                stop = True

        except KeyboardInterrupt:
            programCleanUp()

        programCleanUp()


Mainer.run()
