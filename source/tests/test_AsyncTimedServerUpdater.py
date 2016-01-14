import unittest
import mock
import time

import AsyncServerUpdater

from source.tests import TestingUtilities
from source.tests.custom_mocks import fake_timer

const_updateFrequency = 0.2
const_testVariableName = 'MyVariable'

class WhenAddingFiveVariables(unittest.TestCase):

    def given_a_async_updater(self):
        _setUpUpdater(self)

    def after_adding_five_variables_and_queueing_updates(self):
        _createMockServerVariableUpdateFunction(self)
        _generateAndAddTestData(self)
        _executeTimedUpdatedUpdateMethod()

    def test_then_the_server_update_function_should_be_called_five_times(self):
        callCount = self.mockServerUpdateFunction.call_count
        self.assertEquals(callCount, 5)

    def test_then_the_test_data_values_should_have_been_updated(self):
        _assertTestValuesAreMultipliedByAmount(self, 2)

    def setUp(self):
        self.given_a_async_updater()
        self.after_adding_five_variables_and_queueing_updates()

    def cleanUp():
        TestingUtilities.mockManager.cleanUp()


class WhenTryingToUpdateWhenNoVariableNeedUpdates(unittest.TestCase):
    
    def given_a_async_updater(self):
        _setUpUpdater(self)

    def after_adding_variables_and_forcing_update_twice(self):
        _createMockServerVariableUpdateFunction(self)
        _generateAndAddTestData(self)
        _executeTimedUpdatedUpdateMethod()
        _executeTimedUpdatedUpdateMethod()

    def test_then_the_server_update_function_should_have_been_called_only_once_per_variable(self):
        callCount = self.mockServerUpdateFunction.call_count
        self.assertEquals(callCount, 5)

    def setUp(self):
        self.given_a_async_updater()
        self.after_adding_variables_and_forcing_update_twice()

    def cleanUp():
        TestingUtilities.mockManager.cleanUp()

class WhenEnqueueingManyUpdates(unittest.TestCase):

    def given_a_async_updater(self):
        _setUpUpdater(self)

    def after_adding_variables_and_enqueueing_two_doubling_updates_per_variable(testObject):
        _createMockServerVariableUpdateFunction(testObject)
        _generateAndAddTestData(testObject)
        _enqueueVariableUpdates(testObject.updater, testObject.testData.keys(), _doubleFunction)
        _executeTimedUpdatedUpdateMethod()

    def test_then_the_test_data_values_should_have_been_quadrupled(self):
        _assertTestValuesAreMultipliedByAmount(self, 4)

    def setUp(self):
        self.given_a_async_updater()
        self.after_adding_variables_and_enqueueing_two_doubling_updates_per_variable()

def _setUpUpdater(testObject):
    _setUpTimerFake(testObject)
    testObject.updater = AsyncServerUpdater.AsyncTimedServerVariableUpdater(const_updateFrequency)

def _createMockUpdateFunctionAndAddVariable(testObject):
    testObject.updater.addVariable(const_testVariableName1, testObject.mockServerUpdateFunction)
    _createMockServerVariableUpdateFunction(testObject)

def _createMockServerVariableUpdateFunction(testObject):
    testObject.mockServerUpdateFunction = mock.MagicMock()

def _setUpTimerFake(testObject):
    TestingUtilities.mockManager = TestingUtilities.MockManager()
    TestingUtilities.mockManager.addFake('Timer', 'threading.Timer', fake_timer.FakeTimerRemote)

def _executeTimedUpdatedUpdateMethod():
    # Not great, but...
    fake_timer.callFunctionCallbacks(AsyncServerUpdater.AsyncTimedServerVariableUpdater._updateVariableValues.__name__)

def _generateTestData():
    testData = {}
    for i in range(5):
        testData[const_testVariableName + str(i)] = i
    return testData

def _doubleFunction(x):
    return x * 2

def _generateAndAddTestData(testObject):
    testObject.testData = _generateTestData()
    _addTestDataToUpdater(testObject, testObject.testData)
    _enqueueVariableUpdates(testObject.updater, testObject.testData.keys(), _doubleFunction)

def _addTestDataToUpdater(testObject, testData):
    for variableName in testData:
        testObject.updater.addVariable(variableName, testObject.mockServerUpdateFunction, testData[variableName])

def _enqueueVariableUpdates(updater, variableNames, updateVariableFunction):
    for variableName in variableNames:
        updater.queueVariableUpdate(variableName, updateVariableFunction)

def _assertTestValuesAreMultipliedByAmount(testObject, multiplyAmount):
    serverUpdateCalls = testObject.mockServerUpdateFunction.call_args_list
    for updateCall in serverUpdateCalls:
        variableName, updatedValue = updateCall[0]
        initialValue = testObject.testData[variableName]
        testObject.assertEquals(updatedValue, initialValue * multiplyAmount)


if __name__ == '__main__':
    unittest.main()
