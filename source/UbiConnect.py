__author__ = 'Brendan Gluth'

import ubidots.apiclient as UbiApi
from requests.exceptions import RequestException

def _tryConnect(connectFunction):
    def connect():
        functionResults = connectFunction()
        if functionResults is None:
            functionResults = True
        return functionResults

    try:
        return connect()

    except (UbiApi.UbidotsError, RequestException):
        return False

def tryConnectToUbidotsAccount(ubiAccountKey):
    def connectAccountThroughAPIInit():
        return UbiApi.ApiClient(apikey = ubiAccountKey)

    apiClientCreationAttempt = _tryConnect(connectAccountThroughAPIInit)
    if _tryConnectSucceeded(apiClientCreationAttempt):
        return UbiConnection(apiClientCreationAttempt)
    return False

def _tryConnectSucceeded(connectFunctionResults):
    return connectFunctionResults is not False

class UbiConnection:

    def __init__(self, apiClient):
        self._apiClient = apiClient
        self._ubiVariableConnections = []
        self._connected = True

    def _tryConnectWithStatusStateUpdate(self, connectFunction):
        functionResults = _tryConnect(connectFunction)
        self._IntrepetConnectionResults(functionResults)
        return functionResults

    def _IntrepetConnectionResults(self, functionResults):
        # Note that functionResults may be true, false or another value returned from the server.
        if _tryConnectSucceeded(functionResults):
            self.isConnected = True
        else: self.isConnected = False


    def tryReadVariableFromServer(self, variableHandle):
        def readVariable(ubidotsVariableConnection):
            lastSetVariableValue = ubidotsVariableConnection.get_values(1)
            return lastSetVariableValue[0]['value'] # Note: Ubidots apparently likes storing numbers as floats...

        ubiVariableConnection = self._getUbiVariableConnectionByIndex(variableHandle);
        return self._tryConnectWithStatusStateUpdate(lambda: readVariable(ubiVariableConnection))

    def tryWriteVariableToServer(self, variableHandle, valueToWrite):
        ubiVariableConnection = self._getUbiVariableConnectionByIndex(variableHandle);
        return self._tryConnectWithStatusStateUpdate(lambda: ubiVariableConnection.save_value({'value': valueToWrite}))

    def addNewVariableAndReturnHandle(self, variableKey):
        indexOfNewVariable = len(self._ubiVariableConnections)
        self._ubiVariableConnections.append(self._apiClient.get_variable(variableKey))
        return indexOfNewVariable

    def isConnected(self):
        return self._connected

    def _getUbiVariableConnectionByIndex(self, variableIndex):
        return self._ubiVariableConnections[variableIndex]
