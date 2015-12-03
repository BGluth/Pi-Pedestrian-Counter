import Utilities



def createLoggingFunction(filePath, useTimeStamp):
    def loggingFunction(logMessage):
        if useTimeStamp:
            logMessage = _addTimestampToMessage(logMessage)
        Utilities.openAndAppendToFile(filePath, logMessage)

    return loggingFunction

def _addTimestampToMessage(message):
    currentDateTime = datetime.datetime.now()
    return '[' + str(currentDateTime) + '] - ' + message + '\n'

#def getOutputFunction(writeToConsole, logToFile):
#    def addMethodsToList():
#        if writeToConsole:
#            functionsToCall.append(wrappedPrint)
#        if logToFile:
#            functionsToCall.append(_log);

#    def outputFunction(messageToOutput):
#        for function in functionsToCall:
#            function(messageToOutput)

#    functionsToCall = []
#    addMethodsToList();
#    return outputFunction

def wrappedPrint(string):
    print(string)