__author__ = 'Brendan Gluth'

import os
import xml.etree.ElementTree as ET


class XMLUnexpectedValue(ValueError):
    def __init__(self, message):
        super(XMLUnexpectedValue, self).__init__(message)
        self.message = message

def makeDirIfNotExists(path):
    directoryPath = os.path.dirname(path)
    if not os.path.exists(directoryPath):
        os.mkdir(directoryPath)
 
# Hacky attempt to read in any values stored in a specific format stored in an XML file
def readInXMLValues(filePath):  
    makeDirIfNotExists(filePath)
    if not os.path.exists(filePath):
        raise XMLUnexpectedValue('Could not load in XML values because ' + filePath + ' does not exist!')
        
    tree = ET.parse(filePath)
    data = tree.getroot()
    if data.tag != 'data':
        raise XMLUnexpectedValue('Could not load in XML values because the root element is not called data!') 
        
    # Read in any of data's attributes
    return data.attrib

def openAndAppendToFile(filePath, textToAppend):
    makeDirIfNotExists(filePath)
    file = open(filePath, mode='a')
    file.write(textToAppend)
    file.close()