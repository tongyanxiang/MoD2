class MandatoryController:

    def __init__(self):

        # controller parameters
        self.setpoint = 200.0
        self.uRange = [1, 100]
        self.deltaU = 5

    def control(self, quality, compressedSize):

        if compressedSize > self.setpoint*0.8:
            quality = quality - self.deltaU
            quality = max(quality,self.uRange[0])

        return quality