__author__ = 'root'

import ubidots.apiclient as UbiApi

class UbiConnection:

    def _tryConnect(self, function):
        try:
            function()
            self._connected = True
            return True

        except UbiApi.UbidotsError:
            if (not self._connected): # print message if we just lost connection.
                print('Failed to connect to Ubidots. Will continue to try until it becomes availiable.')
                self._connected = False
            return False

    def __init__(self, accountKey):
        def init():
            self._api = UbiApi.ApiClient(apikey=accountKey)
            self._ubiAccountKey = accountKey
            self._ubiVariables = []

        self._connected = self._tryConnect(init)
        print('Connected to Ubidot account: ' + str(self._connected))

    def getVariableFromServer(self, variableIndex):
        def readVariable(variableList):
            if (len(variableList) > 0):
                return variableList[0]['value']
            else:
                return 0 # Might be inappropriate if returning something like a string, but for now we just need a number

        return self._tryConnect(lambda: readVariable(self._ubiVariables[variableIndex].get_values(1)))

    def writeVariableToServer(self, variableIndex, valueToWrite):
        print('Writing ' + str(valueToWrite) + ' to server.')
        return self._tryConnect(lambda: self._ubiVariables[variableIndex].save_value({'value': valueToWrite - 1}))


    def addNewVariable(self, variableKey):
        index = len(self._ubiVariables)
        self._ubiVariables.append(self._api.get_variable(variableKey))
        return index
