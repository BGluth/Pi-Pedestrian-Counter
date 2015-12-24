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
            functionResults = connectFunction()
            if functionResults is None:
                functionResults = True
            self._connected = True
            return functionResults

        try:
            return connect()

        except (UbiApi.UbidotsError, RequestException):
            self._connected = False;
            return False

    def tryAccountConnect(self):
        def connectAccountThroughAPIInit():
            self._api = UbiApi.ApiClient(apikey = self._ubiAccountKey)

        success = self._tryConnect(connectAccountThroughAPIInit)
        self._accountConnected = success
        return success

    def tryReadVariableFromServer(self, variableHandle):
        def readVariable(ubidotsVariableConnection):
            lastSetVariableValue = ubidotsVariableConnection.get_values(1)
            return lastSetVariableValue[0]['value'] # Note: Ubidots apparently likes storing numbers as floats...

        ubiVariableConnection = self._getUbiVariableConnectionByIndex(variableHandle);
        return self._tryConnect(lambda: readVariable(ubiVariableConnection))

    def tryWriteVariableToServer(self, variableHandle, valueToWrite):
        ubiVariableConnection = self._getUbiVariableConnectionByIndex(variableHandle);
        return self._tryConnect(lambda: ubiVariableConnection.save_value({'value': valueToWrite}))

    def addNewVariableAndReturnHandle(self, variableKey):
        indexOfNewVariable = len(self._ubiVariableConnections)
        self._ubiVariableConnections.append(self._api.get_variable(variableKey))
        return indexOfNewVariable

    def isConnected(self):
        return self._connected

    def isConnectedToAccount(self):
        return self._accountConnected

    def _getUbiVariableConnectionByIndex(self, variableIndex):
        return self._ubiVariableConnections[variableIndex]
