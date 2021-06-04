import numpy as np
from scipy import stats

class MoD2:
    # Model-guided model Deviation Detector

    def __init__(self):

        # Nominal model parameters
        self.A = 0.0
        self.B = 3.0959
        self.C = 1.0

        # Deviated model parameter
        self.B_k = self.B
        self.P_k = 0.5

        # System state
        self.deltaState = 0.0
        self.deltaStateVar  = 0.0

        # Uncertainty of model parameter value
        self.Q = 0.02955

        # Uncertainty compensation terms
        self.gamma = 0.17184
        self.W = 0.50961
        self.V = 1.0e-16

        # Safe region of model parameter value
        self.pole = 0.6
        self.safeRegion = [0.0, 1.0/(1-self.pole)*self.B]

        # Probability threshold
        self.probThreshold = 0.9973  # 3sigma

        # Alarm signal
        self.alarm = 0

        # Historical measurements
        self.list_u = []
        self.list_a = []
        self.list_y = []

    def deviationDetector(self, u_1, a, y):

        if len(self.list_u)<3:
            self.list_u.append(u_1)
            self.list_a.append(a)
            self.list_y.append(y)
        else:
            self.list_u.append(u_1)
            self.list_a.append(a)
            self.list_y.append(y)

            # State estimation
            delta_y_2 = self.list_y[1] - self.list_y[0]
            delta_u_2 = self.list_u[2] - self.list_u[1]
            delta_a_1 = self.list_a[2] - self.list_a[1]

            self.deltaState, \
            self.deltaStateVar = self.observer(self.B_k, self.deltaState, self.deltaStateVar,
                                               delta_y_2, delta_u_2, delta_a_1)
            # Model parameter estimation and deviation detection
            delta_u_1 = self.list_u[3] - self.list_u[2]

            if abs(delta_u_1)>0:
                delta_a_0 = self.list_a[3] - self.list_a[2]
                delta_y_0 = self.list_y[3] - self.list_y[2]

                self.B_k, self.P_k = self.estimator(self.deltaState, self.deltaStateVar, self.B_k, self.P_k,
                                                    delta_u_1, delta_a_0, delta_y_0)
                self.alarm = self.passiveDetector(self.B_k, self.P_k)

            else:
                setpoint = 200
                delta = self.list_y[3] - setpoint
                self.alarm = self.activeDetector(delta)

            # Update historical measurements
            self.list_u.remove(self.list_u[0])
            self.list_a.remove(self.list_a[0])
            self.list_y.remove(self.list_y[0])

        return self.alarm

    def observer(self, B_k, deltaState, deltaStateVar, delta_y_2, delta_u_2, delta_a_1):

        # Update process
        ## innovation variance
        R_k = self.C*deltaStateVar*self.C + self.V

        ## updated Kalman gain
        K = deltaStateVar*self.C*(1.0/R_k)

        ## updated (a posteriori) state estimate
        error = delta_y_2 - self.C*deltaState
        deltaState = deltaState + K*error

        ## updated (a posteriori) state estimate variance
        deltaStateVar = (1.0 - K*self.C)*deltaStateVar

        # Prediction process
        ## predicted (a priori) state estimate
        deltaState = self.A*deltaState + B_k*delta_u_2 + self.gamma*delta_a_1

        ## predicted (a priori) state estimate variance
        deltaStateVar = self.A*deltaStateVar*self.A + self.W

        return deltaState, deltaStateVar

    def estimator(self, deltaState, deltaStateVar, B_k, P_k, delta_u_1, delta_a_0, delta_y_0):

        # Prediction process
        ## predicted (a priori) model parameter estimate
        B_k = B_k

        ## predicted (a priori) model parameter estimate variance
        P_k = P_k + self.Q

        # Update process
        ## innovation variance
        H = self.C*delta_u_1
        R_k = (self.C*self.A)*deltaStateVar*(self.C*self.A) + H*P_k*H + self.C*self.W*self.C + self.V

        ## updated Kalman gain
        K = P_k*H*(1.0/R_k)

        ## updated (a posteriori) model parameter estimate
        error = delta_y_0 - (self.C*self.A*deltaState + H*B_k + self.C*self.gamma*delta_a_0)
        B_k = B_k + K*error

        ## updated (a posteriori) model parameter estimate variance
        P_k = (1-K*H)*P_k

        return B_k, P_k

    def passiveDetector(self, B_k, P_k):

        # Alarm if the derived probability that model parameter value
        # falls into safe region does not exceed the probability threshold

        loc = B_k
        scale = np.sqrt(P_k)
        cdf = stats.norm.cdf(self.safeRegion[1], loc, scale) - stats.norm.cdf(self.safeRegion[0], loc, scale)

        passive_alarm = 0
        if cdf < self.probThreshold:
            passive_alarm = 1

        return passive_alarm

    def activeDetector(self, delta):

        # Alarm if derived probability of occuring delta value of
        # the managed system's ouput does not exceed the probability threshold

        loc = 0.0
        scale = 4.2078
        prob6sigma = 0.999999981

        if delta<=loc:
            cdf = stats.norm.cdf(delta,loc,scale)
        else:
            cdf = 1.0-stats.norm.cdf(delta,loc,scale)

        active_alarm = 0
        if cdf < 1.0-prob6sigma:
            active_alarm = 1

        return active_alarm

    def getBEstimate(self):
        return self.B_k

    def getBEstimateVariance(self):
        return self.P_k