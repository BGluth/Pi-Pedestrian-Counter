class FakeTimerRemote:

    registeredCallbacks = {}

    def __init__(self, time, callbackFunction):
        self._registerCallBack(callbackFunction)

    def _registerCallBack(self, callbackFunction):
        callbackKey = callbackFunction.__name__
        if not FakeTimerRemote.registeredCallbacks.has_key(callbackKey):
            FakeTimerRemote.registeredCallbacks[callbackKey] = [callbackFunction]
        else: FakeTimerRemote.registeredCallbacks[callbackKey].append(callbackFunction)

    def start(self):
        pass

    def stop(self):
        pass

def callFunctionCallbacks(callbackName):
    callbacksToCall = FakeTimerRemote.registeredCallbacks[callbackName]

    numCallbacks = len(callbacksToCall)

    for callbackFunction in callbacksToCall[:numCallbacks]:
        callbackFunction()
    # Once a callback is called the callback should be removed from the list, as how a timer would expire after it is used.
    callbacksToCall = callbacksToCall[numCallbacks:]
        