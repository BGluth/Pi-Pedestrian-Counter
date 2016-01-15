import unittest
import mock

import UbiConnect
from source import UbidotsHelper

from source.UbiConnect import UbiConnection
from source.tests.custom_mocks.fake_UbiConnection import Fake_UbiConnection
from source.tests import TestingUtilities

const_fakeAccountKey = '12345'

const_fakeServerVariableKeyOne = '54321'
const_fakeLocalVariableNameOne = 'testVariable1'

const_fakeServerValueToWrite = 6

const_mockManagerUbiConnectKey = 0
const_mockManagerUbiConnectionKey = 1
const_mockManagerTextOutputterKey = 2

class WhenTryingToConnectToAccount(unittest.TestCase):

    @mock.patch('source.UbidotsHelper.UbiConnect', autospec = True)
    def test_then_it_should_return_false_when_no_connection_availiable(self, mockUbiConnect):
        mockUbiConnect.tryConnectToUbidotsAccount.return_value = False
        success = _tryConnectUbidotsHelper(self)
        self.assertFalse(success)

    @mock.patch('source.UbidotsHelper.UbiConnect', autospec = True)
    def test_then_it_should_return_true_when_connection_availiable(self, mockUbiConnect):
        mockUbiConnect.tryConnectToUbidotsAccount.return_value = True
        success = _tryConnectUbidotsHelper(self)
        self.assertTrue(success)
        
class WhenHaveConnectionToServer(unittest.TestCase):

    def givenAConnectedUbidotsHelper(self):
        _setupUbidotsHelper(self)

    def after_getting_and_writing_to_an_ubivariable_handle(self):
        self.variableHandle = _getFakeHandleToUbiServerVariable(self.ubidotsHelper, const_fakeLocalVariableNameOne)
        self.ubidotsHelper.tryWriteVariableValueOnUbiServer(self.variableHandle, const_fakeServerValueToWrite)

    def test_then_i_should_be_able_to_read_the_newly_writen_value(self):
        readValue = self.ubidotsHelper.tryReadVariableFromUbiServer(self.variableHandle)
        self.assertEquals(readValue, const_fakeServerValueToWrite)

    def setUp(self):
        self.givenAConnectedUbidotsHelper()
        self.after_getting_and_writing_to_an_ubivariable_handle()

    def tearDown(self):
        self.mockManager.cleanUp()

class WhenLostConnectionToServerThenAddingVariable(unittest.TestCase):
    
    def givenAConnectedUbidotsHelper(self):
        _setupUbidotsHelper(self)

    def afterLoosingConnectionThenAddingVariable(self):
        _setConnectionStatusOfFakeUbiConnection(self.ubidotsHelper, False)
        self.variableHandle = _getFakeHandleToUbiServerVariable(self.ubidotsHelper, const_fakeLocalVariableNameOne)

    def test_then_variable_handle_should_be_false(self):
        self.assertFalse(self.variableHandle)

    def test_then_try_get_handle_error_message_should_contain_variable_name(self):
        _assertTextOutputerTextContainsVariableName(self, const_fakeLocalVariableNameOne)

    def setUp(self):
        self.givenAConnectedUbidotsHelper()
        self.afterLoosingConnectionThenAddingVariable()

    def tearDown(self):
        self.mockManager.cleanUp()


class WhenLostConnectionToServerThenReadingVariable(unittest.TestCase):

    def givenAConnectedUbidotsHelper(self):
        _setupUbidotsHelper(self)

    def afterAddingVariableThenLoosingConnectionThenReadingVariable(self):
        _addVariableAndLooseConnection(self)
        self.readResults = self.ubidotsHelper.tryReadVariableFromUbiServer(self.variableHandle)

    def test_then_the_read_results_should_be_false(self):
        self.assertFalse(self.readResults)

    def test_then_try_read_error_message_should_contain_variable_name(self):
        _assertTextOutputerTextContainsVariableName(self, const_fakeLocalVariableNameOne)

    def setUp(self):
        self.givenAConnectedUbidotsHelper()
        self.afterAddingVariableThenLoosingConnectionThenReadingVariable()

    def tearDown(self):
        self.mockManager.cleanUp()

class WhenLostConnectionToServerThenWritingToVariable(unittest.TestCase):

    def givenAConnectedUbidotsHelper(self):
        _setupUbidotsHelper(self)

    def afterAddingVariableThenLoosingConnectionThenWritingToVariable(self):
        _addVariableAndLooseConnection(self)
        self.writeResults = self.ubidotsHelper.tryWriteVariableValueOnUbiServer(self.variableHandle, const_fakeServerValueToWrite)

    def test_then_try_write_should_return_false(self):
        self.assertFalse(self.writeResults)
        
    def test_then_try_write_error_message_should_contain_variable_name(self):
        _assertTextOutputerTextContainsVariableName(self, const_fakeLocalVariableNameOne)

    def setUp(self):
        self.givenAConnectedUbidotsHelper()
        self.afterAddingVariableThenLoosingConnectionThenWritingToVariable()

    def tearDown(self):
        self.mockManager.cleanUp()





def _setupUbidotsHelper(testObject):
    _setUpMocks(testObject)
    _tryConnectUbidotsHelper(testObject)

def _setUpMocks(testObject,):
    testObject.mockManager = TestingUtilities.MockManager()
    _setUpTryConnectMock(testObject.mockManager)
    _setUpTextOutputerMock(testObject.mockManager)

def _setUpTextOutputerMock(mockManager):
    mockManager.addMock(const_mockManagerTextOutputterKey, 'source.UbidotsHelper.TextOutputer')
    mockTextOutputer = mockManager.getMock(const_mockManagerTextOutputterKey)
    mockTextOutputer.output = mock.MagicMock()

def _setUpTryConnectMock(mockManager):
    mockManager.addMock(const_mockManagerUbiConnectKey, 'source.UbidotsHelper.UbiConnect')
    ubiConnectMock = mockManager.getMock(const_mockManagerUbiConnectKey)
    ubiConnectMock.tryConnectToUbidotsAccount = (lambda _:  Fake_UbiConnection())

def _tryConnectUbidotsHelper(testObject):
    testObject.ubidotsHelper = UbidotsHelper.tryConnectToAccount(const_fakeAccountKey)
    success = testObject.ubidotsHelper != False
    return success

def _getFakeHandleToUbiServerVariable(ubidotsHelper, variableName):
    handle = ubidotsHelper.tryGetHandleToUbiServerVariable(const_fakeServerVariableKeyOne, variableName)
    return handle

def _setConnectionStatusOfFakeUbiConnection(ubidotsHelper, connectionState):
    ubidotsHelper._ubiConnection.testMethod_setIsConnected(False)

def _assertTextOutputerTextContainsVariableName(testObject, variableName):
    mockTextOutputer = testObject.mockManager.getMock(const_mockManagerTextOutputterKey)
    callsToTextOutputer = mockTextOutputer.output.call_args_list

    for call in callsToTextOutputer:
        printedMessage = TestingUtilities.extractArgumentValueFromMockCallArgs(call, 0)
        if variableName in printedMessage:
            return
    testObject.fail(str.format('Failed to find \'{}\' in output texts. (TODO: Show outputed texts?)'))

def _addVariableAndLooseConnection(testObject):
    testObject.variableHandle = _getFakeHandleToUbiServerVariable(testObject.ubidotsHelper, const_fakeLocalVariableNameOne)
    _setConnectionStatusOfFakeUbiConnection(testObject.ubidotsHelper, False)

if __name__ == '__main__':
    unittest.main()
