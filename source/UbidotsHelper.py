import TextOutputer
import UbiConnect

class UbidotsHelper:
    def __init__(self):
        self._ubiHandleToVariableNameDict = {}

    def tryConnectToAccount(self, ubiAccountKey):

        TextOutputer.output('Trying to Connect to Ubidots account now...')
        ubiConnectionAttempt = UbiConnect.tryConnectToUbidotsAccount(ubiAccountKey)
        success = self._intrepretConnectionAttemptResults(ubiConnectionAttempt)
        return success

    def _intrepretConnectionAttemptResults(self, ubiConnectionAttempt):
        if ubiConnectionAttempt is not False:
            TextOutputer.output('Connected to Ubidots account!')
            self._ubiConnection = ubiConnectionAttempt
            return True
        else:
            TextOutputer.output('Failed to connect to Ubidots account.')
            return False  

    def getHandleToUbiVariable(self, variableKey, variableName):
        ubiVariableHandle = self._ubiConnection.addNewVariable(variableKey)
        self._ubiHandleToVariableNameDict[ubiVariableHandle] = variableName
        return ubiVariableHandle

    def tryGetVariableFromUbiServer(self, ubiVariableHandle):
        returnedServerValue = self._ubiConnection.tryGetVariableFromServer(ubiVariableHandle)
        if totalDetections is False:
            TextOutputer.output('Failed to get ' + self.ubiVariableNames[ubiVariableHandle] + ' from server.')
        return returnedServerValue

    def trySetVariableValueOnUbiServer(self, ubiVariableHandle, newValue):
        success = self._ubiConnection.writeVariableToServer(ubiVariableHandle, newValue)
        if not success:
            TextOutputer.output('Failed to set ' + self.ubiVariableNames[ubiVariableHandle] + ' on server.')
        return success