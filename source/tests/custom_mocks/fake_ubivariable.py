class Fake_UbiVariable:
    
    const_valueToInitializeTo = 2

    def __init__(self, startingValue = const_valueToInitializeTo):
        self.currentStoredValue = startingValue

    def get_values(self, numofvals=1):
        fakeValues = []
        for x in range(numofvals):
            fakeValues.append({'value': self.currentStoredValue})

        return fakeValues

    def save_value(self, data):
        self.currentStoredValue = data['value']


