__author__ = 'root'

import ubidots.apiclient as UbiApi
from requests.exceptions import RequestException

class UbiConnection:

    @property
    def connected(self):
        return self._connected
    @property
    def accountConnected(self):
        return self._accountConnected


    def _tryConnect(self, function):
        try:
            returnedValue = function()
            self._connected = True
            return returnedValue

        except (UbiApi.UbidotsError, RequestException):
            if (not self._connected): # Print message if we just lost connection.
                print('Failed to connect to Ubidots.') # Client of class should try again until it becomes availiable.
                self._connected = False
            return False

    def tryAccountConnect(self, accountKey):
        result = self._tryConnect(lambda: UbiApi.ApiClient(apikey=accountKey))
        if result is not False:
            self._api = result
            self._connected = True
            self._accountConnected = True
            return True
        else:
            self._connected = False
            return False

    def __init__(self, accountKey):
        def apiInit():
            #TODO: Add a connection retry if it fails to connect when this object is created.
            self._api = UbiApi.ApiClient(apikey=accountKey)

        self._ubiAccountKey = accountKey
        self._ubiVariables = []
        self._connected = False
        self._accountConnected = False
        self.tryAccountConnect(accountKey)
        print('Connected to Ubidot account: ' + str(self._accountConnected))

    def getVariableFromServer(self, variableIndex):
        def readVariable(variableList):
            if (len(variableList) > 0):
                return variableList[0]['value'] # Note: Ubidots apparently likes storing numbers as floats...
            else:
                return 0 # Might be inappropriate if returning something like a string, but for now we just need a number

        return self._tryConnect(lambda: readVariable(self._ubiVariables[variableIndex].get_values(1)))

    def writeVariableToServer(self, variableIndex, valueToWrite):
        print('Writing ' + str(valueToWrite) + ' to server.')
        return self._tryConnect(lambda: self._ubiVariables[variableIndex].save_value({'value': valueToWrite}))


    def addNewVariable(self, variableKey):
        index = len(self._ubiVariables)
        self._ubiVariables.append(self._api.get_variable(variableKey))
        return index
