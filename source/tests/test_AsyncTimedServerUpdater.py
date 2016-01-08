import unittest
import mock
import time

import AsyncServerUpdater

from source.tests import TestingUtilities
from source.tests.custom_mocks import fake_timer

const_updateFrequency = 0.2
const_testVariableName1 = 'MyFirstVariable'

class AddingVariableToAsyncTimedServerUpdater(unittest.TestCase):

    def given_a_async_updater(self):
        _setUpUpdater(self)

    def after_adding_a_variable_and_queing_a_value(self):
        _createMockUpdateFunctionAndAddVariable(self)
        _executeTimedUpdatedUpdateMethod()

    def test_then_the_server_update_function_should_be_called_once(self):
        callCount = self.mockServerUpdateFunction.call_count
        self.assertEquals(callCount, 1)

    def setUp(self):
        self.given_a_async_updater()
        self.after_adding_a_variable_and_queing_a_value()




def _setUpUpdater(testObject):
    _setUpTimerFake(testObject)
    testObject.updater = AsyncServerUpdater.AsyncTimedServerVariableUpdater(const_updateFrequency)

def _createMockUpdateFunctionAndAddVariable(testObject):
    _createMockServerVariableUpdateFunction(testObject)
    testObject.updater.addVariable(const_testVariableName1, testObject.mockServerUpdateFunction)

def _createMockServerVariableUpdateFunction(testObject):
    testObject.mockServerUpdateFunction = mock.MagicMock()

def _setUpTimerFake(testObject):
    TestingUtilities.setUpFakeInstanceOfObject(testObject, 'Timer', 'threading.Timer', fake_timer.FakeTimerRemote)

def _executeTimedUpdatedUpdateMethod():
    # Not great, but...
    fake_timer.callFunctionCallbacks(AsyncServerUpdater.AsyncTimedServerVariableUpdater._updateVariableValues.__name__)

if __name__ == '__main__':
    unittest.main()
