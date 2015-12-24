__author__ = 'Brendan Gluth'

import ubidots.apiclient as UbiApi
from requests.exceptions import RequestException

class UbiConnection:

    def __init__(self, accountKey):
        self._ubiAccountKey = accountKey
        self._ubiVariableConnections = []
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

    def tryGetVariableFromServer(self, variableHandle):
        def readVariable(ReturnedUbidotsVariableData):
            return ReturnedUbidotsVariableData[0]['value'] # Note: Ubidots apparently likes storing numbers as floats...

        ubiVariableConnection = _getUbiVariableConnectionByIndex(variableHandle);
        return self._tryConnect(lambda: readVariable(ubiVariableConnection.get_values(1)))

    def tryWriteVariableToServer(self, variableHandle, valueToWrite):
        ubiVariableConnection = _getUbiVariableConnectionByIndex(variableHandle);
        return self._tryConnect(lambda: ubiVariableConnection.save_value({'value': valueToWrite}))

    def addNewVariableAndReturnHandle(self, variableKey):
        indexOfNewVariable = len(self._ubiVariableConnections)
        self._ubiVariableConnections.append(self._api.get_variable(variableKey))
        return indexOfNewVariable

    def isConnected(self):
        return self.connected

    def isConnectedToAccount(self):
        return self.accountConnected

    def _getUbiVariableConnectionByIndex(self, variableIndex):
        return self._ubiVariableConnections[variableIndex]
