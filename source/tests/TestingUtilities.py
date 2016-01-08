import mock

def setUpFakeInstanceOfObject(testObject, name, mockPath, fakeObjectToUse):

    patcher = None
    patcherVariableName = _createPatcherName(name)

    patcher = mock.patch(mockPath, fakeObjectToUse)

    setattr(testObject, patcherVariableName, patcher)
    patcher.start()

    patcher.return_value = fakeObjectToUse

def _createPatcherName(name):
    return 'fake' + name + 'Patcher'





























#class TestResult:
#    def __init__(self, expected, actual):
#        self.expected = expected
#        self.actual = actual

#class TestGenerator(unittest.TestCase):

#    def __init__(self, name, setupFunc = None, teardownFunc = None):
#        self.name = name
        
#        if setupFunc is not None:
#            setup = setupFunc
#        if teardownFunc is not None:
#            teardown = teardownFunc

#    def setup():
#        pass

#    def teardown():
#        pass

#    def generateTestForDifferentStates(testName, sequenceOfStates, functionsToCallBasedOnState):
#        def runTests(self):
#            stateTestFunction = _generateStateAwareFunction(functionsToCallBasedOnState)
#            self.RunStateTestFunctionForEachPossibleState(sequenceOfStates, stateTestFunction)

#        return runTests

#        #_addTestMethodToClass(testName, runTests)

#    def _generateStateAwareFunction(functionsToCallBasedOnState):
#        def stateAwareFunction(currentState):
#            functionToCallForCurrentState = functionsToCallBasedOnState[currentState]
#            functionToCallForCurrentState()
#        return stateAwareFunction

#    def _runStateTestFunctionForEachPossibleState(self, sequenceOfStates, stateTestFunction):
#        for state in sequenceOfStates:
#            testResults = stateTestFunction(state)
#            _checkTestSucceeded(testResults)

#    def _addTestMethodToClass(testName, testCode):
#        fullTestName = 'test_{0}_{1}'.format(self.name, testName)
#        setattr(TestGenerator, fullTestName, testCode)

#    def _assertTestSucceeded(self, testResults):
#        self.assertEqual(testResults.expected, testResults.actual)


        