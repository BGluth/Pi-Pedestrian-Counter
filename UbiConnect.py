__author__ = 'Brendan Gluth'

import ubidots.apiclient as UbiApi
from requests.exceptions import RequestException

class UbiConnection:

    def __init__(self, accountKey):
        self._ubiAccountKey = accountKey
        self._ubiVariables = []
        self._connected = False
        self._accountConnected = False

    def _tryConnect(self, connectFunction):
        def connect():
            connectFunction()
            self._connected = True

        try:
            connect()
            return True

        except (UbiApi.UbidotsError, RequestException):
            self.connected = False;
            return False

    def tryAccountConnect(self):
        def connectAccountThroughAPIInit():
            self._api = UbiApi.ApiClient(apikey = self._ubiAccountKey)

        return self._tryConnect(connectAccountThroughAPIInit) 

    def tryGetVariableFromServer(self, variableIndex):
        def readVariable(ReturnedUbidotsVariableData):
            return ReturnedUbidotsVariableData[0]['value'] # Note: Ubidots apparently likes storing numbers as floats...

        ubiVariable = _getUbiVariableByIndex(variableIndex);
        return self._tryConnect(lambda: readVariable(ubiVariable.get_values(1)))

    def tryWriteVariableToServer(self, variableIndex, valueToWrite):
        ubiVariable = _getUbiVariableByIndex(variableIndex);
        return self._tryConnect(lambda: ubiVariable.save_value({'value': valueToWrite}))

    def addNewVariable(self, variableKey):
        indexOfNewVariable = len(self._ubiVariables)
        self._ubiVariables.append(self._api.get_variable(variableKey))
        return indexOfNewVariable

    def isConnected(self):
        return self.connected

    def isConnectedToAccount(self):
        return self.accountConnected

    def _getUbiVariableByIndex(self, variableIndex):
        return self._ubiVariables[variableIndex]
