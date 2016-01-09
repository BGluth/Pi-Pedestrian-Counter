import Queue
import threading

class AsyncTimedServerVariableUpdater():

    def __init__(self, updateFrequency):
        self.queuedVariableUpdates = Queue.Queue()
        self.variables = {}
        self.updateFrequency = updateFrequency

        self._callUpdateMethodAfterTime()

    def addVariable(self, variableName, sendUpdatedVariableToServerFunction, initialValue = 0):
        self.variables[variableName] = [initialValue, sendUpdatedVariableToServerFunction, True]

    def queueVariableUpdate(self, variableName, variableUpdateFunction):
        self.queuedVariableUpdates.put([variableName, variableUpdateFunction])        

    def stop(self):
        self.updateTimer.cancel()

    def _updateVariableValues(self):
        if self.queuedVariableUpdates.not_empty:
            self._applyQueuedVariableUpdates() 
            self._applyVariableUpdatesToServer()

        self._callUpdateMethodAfterTime()

    def _applyQueuedVariableUpdates(self):
        while self._variableUpdatesExist():
            queuedVariableUpdate = self.queuedVariableUpdates.get()
            self._applyUpdateToVariable(queuedVariableUpdate)
            self.queuedVariableUpdates.task_done()

    def _variableUpdatesExist(self):
        return self.queuedVariableUpdates.unfinished_tasks != 0

    def _applyUpdateToVariable(self, queuedVariableUpdate):
        variableName, updateAndReturnVariableValueFunction = queuedVariableUpdate
        variable = self.variables[variableName]
        currentValue, _, _ = variable
        updatedValue = updateAndReturnVariableValueFunction(currentValue)
        _setVariableCurrentValue(variable, updatedValue)
        _setVariableNeedsUpdate(variable, True)

    def _applyVariableUpdatesToServer(self):
        for variableNameKey in self.variables:
            variable = self.variables[variableNameKey]
            currentValue, updateServerVariableFunction, needsUpdate = variable
            if needsUpdate is True:
                updateServerVariableFunction(variableNameKey, currentValue)
                _setVariableNeedsUpdate(variable, False)

    def _callUpdateMethodAfterTime(self):
        self.updateTimer = threading.Timer(self.updateFrequency, self._updateVariableValues)
        self.updateTimer.start()

def _setVariableNeedsUpdate(variable, needsUpdate):
    variable[2] = needsUpdate

def _setVariableCurrentValue(variable, newValue):
    variable[0] = newValue