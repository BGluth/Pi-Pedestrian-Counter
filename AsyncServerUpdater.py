import Queue
import threading

_INCREMENT = 0
_SET = 1

def updateType_Increment(variableName):
    return [SET, variableName]

def updateType_Set(variableName, newValue):
    return [INCREMENT, variableName, newValue]

def _setVariableValue(variable, newValue):
    variable[const_variable_currentValueIndex] = newValue

def _incrementVariableValue(variable):
    variable[const_variable_currentValueIndex] += 1

class AsyncTimedServerVariableUpdater():

    const_variable_currentValueIndex = 0
    const_variable_updateFunctionIndex = 1
    const_variable_needsServerUpdateIndex = 2

    const_queuedVariableUpdate_functionKeyIndex = 0
    const_queuedVariableUpdate_variableNameIndex = 1


    updateVariableValueFunctionsDict = {
        _SET: _setVariableValue,
        _INCREMENT: _incrementVariableValue
        }

    def __init__(self, updateFrequency):
        self.queuedVariableUpdates = Queue.Queue()
        self.variables = {}
        self.updateFrequency = updateFrequency

        self._callUpdateMethodAfterTime()

    def addVariable(self, variableName, updateFunction, initialValue = 0):
        self.variables[variableName] = (initialValue, updateFunction, True)

    def queueVariableUpdate(self, variableName, variableUpdateFunction):
        self._addToUpdateQueue(variableName, variableUpdateFunction)

    def stop(self):
        self.updateTimer.cancel()

    def _updateVariableValues(self):
        if self.queuedVariableUpdates.not_empty:
            self._applyQueuedVariableUpdates() 
            self._applyVariableUpdatesToServer()

        self._callUpdateMethodAfterTime()

    def _applyQueuedVariableUpdates(self):
        while self.queuedVariableUpdates.not_empty is True:
            queuedVariableUpdate = self.queuedVariableUpdates.get()
            self._applyUpdateToVariable(queuedVariableUpdate)

    def _applyUpdateToVariable(self, queuedVariableUpdate):
        #functionKey = queuedVariableUpdate[0]
        #variableName = queuedVariableUpdate[1]
        updateVariableValueFunction = self.updateVariableValueFunctionsDict[functionKey]
        variable = self.variables[variableName]
        updateVariableValueFunction(variable, queuedVariableUpdate[2:]) # Any parameters after the second element are extra parameters that the update function needs.
        variable[const_variable_needsServerUpdateIndex] = True

    def _applyVariableUpdatesToServer(self):
        for variableNameKey in self.variables:
            currentValue, updateFunction, needsUpdate = self.variables[variableNameKey]
            if needsUpdate is True:
                updateFunction(variableNameKey, currentValue)
                needsUpdate = False

    def _callUpdateMethodAfterTime(self):
        self.updateTimer = threading.Timer(self.updateFrequency, self._updateVariableValues)
        self.updateTimer.start()

    def _addToUpdateQueue(self, variableName, updateFunction):
        self.queuedVariableUpdates.put([variableName, updateFunction])

                       