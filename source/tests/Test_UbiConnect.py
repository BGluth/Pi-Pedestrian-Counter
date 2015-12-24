import mock
import unittest

from source import UbiConnect
from source.tests.custom_mocks.fake_ubivariable import Fake_UbiVariable

const_fakeVariableName = 'MyFakeVariable'
const_fakeServerValueToChangeTo = 42



class WhenCreatingAnUbiConnectObjectWhenCanNotConnect(unittest.TestCase):

    def given_an_ubiconnect_object(self):
        _createUbiconnectObject(self)

    def test_then_attempting_to_connect_to_account_should_return_false(self):
        results = self.ubiConnect.tryAccountConnect()
        self.assertFalse(results)

    def setUp(self):
        self.given_an_ubiconnect_object()

class WhenCreatingAnUbiConnectObjectWhenCanConnect(unittest.TestCase):

    def given_an_ubiconnect_object(self):
        _createUbiconnectObject(self)

    def after_it_has_tried_to_connect_successfully(self):
        self.ubiConnect.tryAccountConnect()

    def test_then_attempting_to_connect_to_account_should_return_True(self):
        results = self.ubiConnect.tryAccountConnect()
        self.assertTrue(results)

    def clean_up_mocks(self):
       _cleanUpApiClientMock(self)

    def setUp(self):
        _setUpApiClientMock(self)
        self.given_an_ubiconnect_object()

    def tearDown(self):
        self.clean_up_mocks()



class WhenUsingAnUbiConnectObjectWithAUnsuccessfulConnection(unittest.TestCase):

    def given_an_ubiconnect_object(self):
        _createUbiconnectObject(self)

    def after_it_has_tried_to_connect_unsuccessfully(self):
        self.ubiConnect.tryAccountConnect()

    def test_then_reading_a_non_existing_variable_should_throw_exception(self):
        with self.assertRaises(Exception):
            self.ubiConnect.tryReadVariableFromServer(const_fakeUbiVariableHandle)

    def test_then_writting_to_a_non_existing_variable_should_throw_exception(self):
        with self.assertRaises(Exception):
            self.ubiConnect.tryWriteVariableToServer(const_fakeUbiVariableHandle, const_fakeServerValueToChangeTo)

    def setUp(self):
        _setUpApiClientMock(self)
        self.given_an_ubiconnect_object()
        self.after_it_has_tried_to_connect_unsuccessfully()

class WhenUsingAnUbiConnectObjectWithASuccessfulConnection(unittest.TestCase):

    def given_an_ubiconnect_object(self):
        _createUbiconnectObject(self)

    def after_it_has_tried_to_connect_successfully(self):
        self.ubiConnect.tryAccountConnect()

    def test_then_isConnectedToAccount_returns_true(self):
        result = self.ubiConnect.isConnectedToAccount()
        self.assertTrue(result)

    def test_then_isConnected_returns_true(self):
        result = self.ubiConnect.isConnected()
        self.assertTrue(result)

    def clean_up_mocks(self):
        _cleanUpApiClientMock(self)

    def setUp(self):
        _setUpApiClientMock(self)
        self.given_an_ubiconnect_object()
        self.after_it_has_tried_to_connect_successfully()
        
    def tearDown(self):
        self.clean_up_mocks()


class WhenAddingAnUbiVariableWithAConnection(unittest.TestCase):

    def given_an_ubiconnect_object(self):
        _createUbiconnectObject(self)

    def after_connecting_and_adding_an_ubivariable_successfully(self):
        _connectAndAddVariable(self)

    def test_then_i_can_read_the_variables_value(self):
        _assertUbiVariableValueIsEqualToValue(self, Fake_UbiVariable.const_valueToInitializeTo)

    def clean_up_mocks(self):
        _cleanUpApiClientMock(self)

    def setUp(self):
        _setUpApiClientAndVariableMock(self)
        self.given_an_ubiconnect_object()
        self.after_connecting_and_adding_an_ubivariable_successfully()
        
    def tearDown(self):
        self.clean_up_mocks()

class WhenWritingToAVariableWithAConection(unittest.TestCase):

    def given_an_ubiconnect_object(self):
        _createUbiconnectObject(self)

    def after_connecting_and_writing_to_an_ubivariable(self):
        _connectAndWriteToVariable(self)

    def test_then_i_should_be_able_to_read_the_newly_changed_value(self):
        _assertUbiVariableValueIsEqualToValue(self, const_fakeServerValueToChangeTo)

    def clean_up_mocks(self):
        _cleanUpApiClientMock(self)

    def setUp(self):
        _setUpApiClientAndVariableMock(self)
        self.given_an_ubiconnect_object()
        self.after_connecting_and_writing_to_an_ubivariable()
        
    def tearDown(self):
        self.clean_up_mocks()




def _createUbiconnectObject(objectToAddToo):
    objectToAddToo.ubiConnect = UbiConnect.UbiConnection('12345')

def _connectUbiconnectObject(ubiConnect):
    ubiConnect.tryAccountConnect()

def _connectAndWriteToVariable(testObject):
    _connectAndAddVariable(testObject)
    testObject.ubiConnect.tryWriteVariableToServer(testObject.variableHandle, const_fakeServerValueToChangeTo)

def _connectAndAddVariable(testObject):
    _connectUbiconnectObject(testObject.ubiConnect)
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














































#mock_ApiClient = mock.MagicMock()

#@mock.patch('ubidots.apiclient.Variable', new = Fake_UbiVariable)
#@mock.patch('ubidots.apiclient.ApiClient', autospec = True)
#class Test_UbiConnectWhenCanConnect(unittest.TestCase):
    
#    def setUp(self):
#        self.ubiConnect = UbiConnect.UbiConnection('12345')

#    def test_Connected_tryAccountConnectReturnsSuccess(self, mock_APIClient):
#        success = self.ubiConnect.tryAccountConnect()
#        self.assertTrue(success)

#    def test_Connected_tryConnectToAccountMakesIsConnectedReturnTrue(self, mock_ApiClient):
#        self._callTryConnectAndInitializeVariableFake(mock_ApiClient)

#        self.assertTrue(self.ubiConnect.isConnected and self.ubiConnect.isConnectedToAccount)

#    def test_Connected_addNewVariableToServerReturnsHandle(self, mock_ApiClient):
#        self._callTryConnectAndInitializeVariableFake(mock_ApiClient)

#        variableHandle = self._addFakeUbiVariableAndGetHandle()

#        self.assertIsNotNone(variableHandle)
    
#    def test_Connected_tryGetVariableFromUbiServerReturnsCorrectValue(self, mock_ApiClient):
#        self._callTryConnectAndInitializeVariableFake(mock_ApiClient)

#        variableHandle = self._addFakeUbiVariableAndGetHandle()
#        fakeValueReturned = self.ubiConnect.tryGetVariableFromServer(variableHandle)
        
#        self.assertEquals(fakeValueReturned, const_fakeServerValue)

#    def test_Connected_tryWriteVariableToUbiServerWritesValue(self, mock_ApiClient):
#        self._callTryConnectAndInitializeVariableFake(mock_ApiClient)

#        variableHandle = self._addFakeUbiVariableAndGetHandle()
#        self.ubiConnect.tryWriteVariableToServer(variableHandle, const_fakeServerValueToChangeTo)
#        variableValue = self.ubiConnect.tryGetVariableFromServer(variableHandle)
        
#        self.assertEquals(variableValue, const_fakeServerValueToChangeTo)

    
#    ## Disconnected Tests

#    #def test_Disconnected_tryAccountConnectReturnsFailure(self, mock_APIClient):


#    #def test_Connected_addNewVariableToServerReturnsHandle(self, mock_ApiClient):

#    #def test_Disconnected_tryConnectToAccountMakesIsConnectedReturnFalse(self, mock_ApiClient):

#    #def test_Disconnected_tryGetVariableFromUbiServerReturnsCorrectValue(self, mock_ApiClient):

#    #def test_Discnnected_tryWriteVariableToUbiServerWritesValue(self, mock_ApiClient):


#    def _callTryConnectAndInitializeVariableFake(self, mock_ApiClient):
#        self._setupGetVariableReturnValue(mock_ApiClient)
#        self.ubiConnect.tryAccountConnect()

#    def _setupGetVariableReturnValue(self, mock_ApiClient):
#        apiClientInstance = mock_ApiClient.return_value
#        apiClientInstance.get_variable.return_value = Fake_UbiVariable(const_fakeServerValue)

#    def _addFakeUbiVariableAndGetHandle(self):
#        return self.ubiConnect.addNewVariableAndReturnHandle('Some Ubidots Key')

    #def _setUpApiClientToNotConnect(self, mock_ApiClient


#def _setUpFunction_Bare(self):
#    self.ubiConnect = UbiConnect.UbiConnection('12345')

#def _setUpFunction_JustConnect(self):
#    _setUpFunction_Bare(self)
#    self.ubiConnect.tryAccountConnect()

#@patch('ubidots.apiclient.Variable', new = Fake_UbiVariable)
#@patch('ubidots.apiclient.ApiClient', autospec = True)
#def _addNewVariableToServerReturnsHandle_Connected(self):
#    handle = _addFakeUbiVariableAndGetHandle()
#    return TestingUtilities.TestResult(


#def _generate_addNewVariableTests(testGenerator):
#    testGenerator.generateTestForDifferentStates

#def _addFakeUbiVariableAndGetHandle(self):
#    return self.ubiConnect.addNewVariableAndReturnHandle('Some Ubidots Key')


if __name__ == '__main__':
    unittest.main()
