const_startingVariableValue = 0

def _returnFalseIfNotConnected(func):
    def wrapper(self, *args, **kwargs):
        if self.isConnected():
            return func(self, *args, **kwargs)
        return False
    return wrapper

class Fake_UbiConnection:

    def __init__(self):
        self._variables = {}
        self._variableIDGenerator = 0
        self._isConnected = True

    @_returnFalseIfNotConnected
    def tryReadVariableFromServer(self, variableHandle):
        return self._variables[variableHandle]

    @_returnFalseIfNotConnected
    def tryWriteVariableToServer(self, variableHandle, valueToWrite):
        self._variables[variableHandle] = valueToWrite

    @_returnFalseIfNotConnected
    def tryAddNewVariableAndReturnHandle(self, variableServerKey):
        handle = self._variableIDGenerator
        self._variableIDGenerator += 1
        self._variables[variableServerKey] = const_startingVariableValue
        return handle

    def isConnected(self):
        return self._isConnected

    def testMethod_setIsConnected(self, value):
        self._isConnected = value
