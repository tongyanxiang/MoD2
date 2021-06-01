class OptimalController:

    def __init__(self):

        # nominal model parameters
        self.A = 0.0
        self.B = 3.0959
        self.C = 1.0

        # controller parameters
        self.beta = self.C*(1.0-self.A)*self.B

        self.setpoint = 200
        self.pole = 0.6
        self.uRange = [1, 100]
        self.deltaURange = [-5, 5]

    def PIControl(self, quality, compressedSize):
        # u_k = u_{k-1} + K_p*(setpoint-y_k)

        coeff_error = (1.0-self.pole)/self.beta
        delta_quality = coeff_error*(self.setpoint-compressedSize)
        delta_quality = min(max(delta_quality,self.deltaURange[0]),self.deltaURange[1])
        quality = int(quality + delta_quality)
        quality = min(max(quality,self.uRange[0]),self.uRange[1])

        return quality