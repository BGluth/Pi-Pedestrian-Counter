import TextOutputer

class UbidotsHelper:
    def __init__(self, ubiConnection):
        self._ubiConnection = ubiConnection
        self._ubiHandleToVariableNameDict = {}

    def tryConnectToAccount(self):
        TextOutputer.output('Trying to Connect to Ubidots account now...')
        success = self._ubiConnection.tryAccountConnect()
        if success is False:
            TextOutputer.output('Failed to connect to Ubidots account.')
        else:
            TextOutputer.output('Connected to Ubidots account!')
        return success

    def getHandleToUbiVariable(self, variableKey, variableName):
        ubiVariableHandle = self._ubiConnection.addNewVariable(variableKey)
        self._ubiHandleToVariableNameDict[ubiVariableHandle] = variableName
        return ubiVariableHandle

    def tryGetVariableFromUbiServer(self, ubiVariableHandle):
        returnedServerValue = ubiConnection.tryGetVariableFromServer(ubiVariableHandle)
        if totalDetections is False:
            TextOutputer.output('Failed to get ' + self.ubiVariableNames[ubiVariableHandle] + ' from server.')
        return returnedServerValue

    def trySetVariableValueOnUbiServer(self, ubiVariableHandle, newValue):
        success = ubiConnection.writeVariableToServer(ubiVariableHandle, newValue)
        if not success:
            TextOutputer.output('Failed to set ' + self.ubiVariableNames[ubiVariableHandle] + ' on server.')
        return success