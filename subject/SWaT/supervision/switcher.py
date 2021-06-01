class Switcher:

    def __init__(self):

        # switcher parameter
        self.switchMode = 0

    def setSwitchMode(self, alarm):
        if alarm==1:
            self.switchMode=1

    def getSwithMode(self):
        return self.switchMode