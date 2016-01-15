import TextOutputer
import UbiConnect


def tryConnectToAccount(ubiAccountKey):
    TextOutputer.output('Trying to Connect to Ubidots account now...')
    ubiConnectionAttempt = UbiConnect.tryConnectToUbidotsAccount(ubiAccountKey)
    return _intrepretOutputForConnectionAttemptResults(ubiConnectionAttempt)

def _intrepretOutputForConnectionAttemptResults(ubiConnectionAttempt):
    if ubiConnectionAttempt is not False:
        TextOutputer.output('Connected to Ubidots account!')
        return UbidotsHelper(ubiConnectionAttempt)

    TextOutputer.output('Failed to connect to Ubidots account.')
    return False

class UbidotsHelper:
    def __init__(self, ubiConnection):
        self._ubiHandleToVariableNameDict = {}
        self._ubiConnection = ubiConnection
 
    def tryGetHandleToUbiServerVariable(self, serverVariableKey, localVariableName):
        ubiVariableHandle = self._ubiConnection.tryAddNewVariableAndReturnHandle(serverVariableKey)

        if ubiVariableHandle is not False:
            self._ubiHandleToVariableNameDict[ubiVariableHandle] = localVariableName
        else:
            TextOutputer.output('Failed to get handle to server variable \'' + localVariableName
                                + '\' with server variable key of: \'' + serverVariableKey + '\'.')
        return ubiVariableHandle

    def tryReadVariableFromUbiServer(self, ubiVariableHandle):
        returnedServerValue = self._ubiConnection.tryReadVariableFromServer(ubiVariableHandle)
        if returnedServerValue is False:
            TextOutputer.output('Failed to read from \'' + self._ubiHandleToVariableNameDict[ubiVariableHandle] + '\' on server.')
        return returnedServerValue

    def tryWriteVariableValueOnUbiServer(self, ubiVariableHandle, newValue):
        success = self._ubiConnection.tryWriteVariableToServer(ubiVariableHandle, newValue)
        if not success:
            TextOutputer.output('Failed to write to \'' + self._ubiHandleToVariableNameDict[ubiVariableHandle] + '\' on server.')
        return success