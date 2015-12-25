import mock
import unittest

from source import UbiConnect
from source.tests.custom_mocks.fake_ubivariable import Fake_UbiVariable

const_fakeUbiAccountKey = '12345'
const_fakeVariableName = 'MyFakeVariable'
const_fakeServerValueToChangeTo = 42



class WhenCreatingAnUbiConnectObjectWhenCanNotConnect(unittest.TestCase):

    def given_a_connected_ubiconnect_object(self):
        _createUbiConnectionObject(self)

    def test_then_the_connection_object_itself_should_be_false(self):
        self.assertFalse(self.ubiConnect)

    def setUp(self):
        self.given_a_connected_ubiconnect_object()

class WhenCreatingAnUbiConnectObjectWhenCanConnect(unittest.TestCase):

    def given_a_unconnected_ubiconnect_object(self):
        _createUbiConnectionObject(self)

    def test_then_the_connection_object_itself_should_be_not_false(self):
        self.assertTrue(self.ubiConnect is not False)

    def clean_up_mocks(self):
       _cleanUpApiClientMock(self)

    def setUp(self):
        _setUpApiClientMock(self)
        self.given_a_unconnected_ubiconnect_object()

    def tearDown(self):
        self.clean_up_mocks()



class WhenUsingAnUbiConnectObjectWithAUnsuccessfulConnection(unittest.TestCase):

    def given_a_unconnected_ubiconnect_object(self):
        _createUbiConnectionObject(self)

    def test_then_reading_a_non_existing_variable_should_throw_exception(self):
        with self.assertRaises(Exception):
            self.ubiConnect.tryReadVariableFromServer(const_fakeUbiVariableHandle)

    def test_then_writting_to_a_non_existing_variable_should_throw_exception(self):
        with self.assertRaises(Exception):
            self.ubiConnect.tryWriteVariableToServer(const_fakeUbiVariableHandle, const_fakeServerValueToChangeTo)

    def setUp(self):
        _setUpApiClientMock(self)
        self.given_a_unconnected_ubiconnect_object()

class WhenUsingAnUbiConnectObjectWithASuccessfulConnection(unittest.TestCase):

    def given_a_connected_ubiconnect_object(self):
        _createUbiConnectionObject(self)

    def test_then_isConnected_returns_true(self):
        result = self.ubiConnect.isConnected()
        self.assertTrue(result)

    def clean_up_mocks(self):
        _cleanUpApiClientMock(self)

    def setUp(self):
        _setUpApiClientMock(self)
        self.given_a_connected_ubiconnect_object()
        
    def tearDown(self):
        self.clean_up_mocks()


class WhenAddingAnUbiVariableWithAConnection(unittest.TestCase):

    def given_a_connected_ubiconnection_object(self):
        _createUbiConnectionObject(self)

    def after_adding_a_ubivariable_successfully(self):
        _addVariable(self)

    def test_then_i_can_read_the_variables_value(self):
        _assertUbiVariableValueIsEqualToValue(self, Fake_UbiVariable.const_valueToInitializeTo)

    def clean_up_mocks(self):
        _cleanUpApiClientMock(self)

    def setUp(self):
        _setUpApiClientAndVariableMock(self)
        self.given_a_connected_ubiconnection_object()
        self.after_adding_a_ubivariable_successfully()
        
    def tearDown(self):
        self.clean_up_mocks()

class WhenWritingToAVariableWithAConection(unittest.TestCase):

    def given_a_connected_ubiconnection_object(self):
        _createUbiConnectionObject(self)

    def after_writing_to_an_ubivariable(self):
        _writeToVariable(self)

    def test_then_i_should_be_able_to_read_the_newly_changed_value(self):
        _assertUbiVariableValueIsEqualToValue(self, const_fakeServerValueToChangeTo)

    def clean_up_mocks(self):
        _cleanUpApiClientMock(self)

    def setUp(self):
        _setUpApiClientAndVariableMock(self)
        self.given_a_connected_ubiconnection_object()
        self.after_writing_to_an_ubivariable()
        
    def tearDown(self):
        self.clean_up_mocks()




def _createUbiConnectionObject(objectToAddToo):
    objectToAddToo.ubiConnect = UbiConnect.tryConnectToUbidotsAccount(const_fakeUbiAccountKey)

def _writeToVariable(testObject):
    _addVariable(testObject)
    testObject.ubiConnect.tryWriteVariableToServer(testObject.variableHandle, const_fakeServerValueToChangeTo)

def _addVariable(testObject):
    testObject.variableHandle = testObject.ubiConnect.addNewVariableAndReturnHandle(const_fakeVariableName)

def _assertUbiVariableValueIsEqualToValue(testObject, valueToEqual):
    readValue = testObject.ubiConnect.tryReadVariableFromServer(testObject.variableHandle)
    testObject.assertEquals(readValue, valueToEqual)

def _setUpApiClientAndVariableMock(testObject):
    _setUpApiClientMock(testObject)
    _setUpUbiVariableFakeOnTestObject(testObject)

def _setUpApiClientMock(testObject):
    testObject.ApiClientPatcher = mock.patch('ubidots.apiclient.ApiClient', autospec = True)
    testObject.apiClientMock = testObject.ApiClientPatcher.start();

def _setUpUbiVariableFakeOnTestObject(testObject):
    testObject.FakeUbiVariablePatcher = mock.patch('ubidots.apiclient.Variable', new = Fake_UbiVariable)
    testObject.FakeUbiVariablePatcher.start()
    
    apiClientInstance = testObject.apiClientMock.return_value
    apiClientInstance.get_variable.return_value = Fake_UbiVariable()   

def _cleanUpApiClientMock(testObject):
    testObject.ApiClientPatcher.stop()


if __name__ == '__main__':
    unittest.main()
