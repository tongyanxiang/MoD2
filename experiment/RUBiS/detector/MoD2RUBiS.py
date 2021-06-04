import numpy as np
from scipy import stats

class MoD2RUBiS:
    # Model-guided model Deviation Detector

    def __init__(self):

        # Nominal model parameters
        self.A = np.array([[0.0, 0.0],
                           [1.0, 0.0]])

        self.B = np.array([[1.0],
                           [0.0]])

        self.C = np.array([[0.0, -0.076]])

        # Deviated model parameter
        self.B_k = self.B
        self.P_k = np.array([[0.001, 0.0],
                             [0.0,   0.0]])

        # System state
        self.deltaState = np.zeros((2,1))
        self.deltaStateVar = np.zeros((2,2))

        # Uncertainty of model parameter value
        self.Q = np.array([[0.0008, 0.0],
                           [0.0,   0.0]])

        # Uncertainty compensation terms
        self.gamma = np.array([[0.0],
                               [0.02930]])
        self.W = np.array([[0.0, 0.0],
                           [0.0, 0.006891]])
        self.V = np.array([[2.0e-06]])

        # Safe region of model parameter value
        self.pole = 0.9
        self.safeRegion = [0.0, 1.0/(4.0*(1-self.pole))*self.B[0][0]]

        # Probability threshold
        self.probThreshold = 0.9973  # 3sigma

        # Alarm signal
        self.alarm = 0

        # Historical measurements
        self.list_u = []
        self.list_a = []
        self.list_y = []

    def deviationDetector(self, u_1, a, y):

        if len(self.list_u)<4:
            self.list_u.append(u_1)
            self.list_a.append(a)
            self.list_y.append(y)
        else:
            self.list_u.append(u_1)
            self.list_a.append(a)
            self.list_y.append(y)

            # State estimation
            delta_y_3 = self.list_y[1] - self.list_y[0]
            delta_u_3 = self.list_u[2] - self.list_u[1]
            delta_a_2 = self.list_a[2] - self.list_a[1]

            self.deltaState, \
            self.deltaStateVar = self.observer(self.B_k, self.deltaState, self.deltaStateVar,
                                               delta_y_3, delta_u_3, delta_a_2)

            # Model parameter estimation and deviation detection
            delta_u_2 = self.list_u[3] - self.list_u[2]
            if abs(delta_u_2)>0:
                delta_a_1 = self.list_a[3] - self.list_a[2]
                delta_a_0 = self.list_a[4] - self.list_a[3]
                delta_y_0 = self.list_y[4] - self.list_y[3]

                self.B_k, self.P_k = self.estimator(self.deltaState, self.deltaStateVar, self.B_k, self.P_k,
                                                    delta_u_2, delta_a_1, delta_a_0, delta_y_0)
                self.alarm = self.passiveDetector(self.B_k, self.P_k)

            else:
                setpoint = 0.3
                delta = self.list_y[4] - setpoint
                self.alarm = self.activeDetector(delta)

            # Update historical measurements
            self.list_u.remove(self.list_u[0])
            self.list_a.remove(self.list_a[0])
            self.list_y.remove(self.list_y[0])

        return self.alarm

    def observer(self, B_k, deltaState, deltaStateVar, delta_y_3, delta_u_3, delta_a_2):

        # Update process
        ## innovation variance
        R_k = np.dot(np.dot(self.C,deltaStateVar),self.C.T) + self.V

        ## updated Kalman gain
        K = np.dot(np.dot(deltaStateVar,self.C.T),np.linalg.inv(R_k))

        ## updated (a posteriori) state estimate
        error = delta_y_3 - np.dot(self.C,deltaState)
        deltaState = deltaState + np.dot(K,error)

        ## updated (a posteriori) state estimate variance
        deltaStateVar = np.dot((np.eye(len(deltaStateVar))-np.dot(K,self.C)),deltaStateVar)

        # Prediction process
        ## predicted (a priori) state estimate
        deltaState = np.dot(self.A,deltaState) + np.dot(B_k,delta_u_3) + np.dot(self.gamma,delta_a_2)

        ## predicted (a priori) state estimate variance
        deltaStateVar = np.dot(np.dot(self.A,deltaStateVar),self.A.T) + self.W

        return deltaState, deltaStateVar

    def estimator(self, deltaState, deltaStateVar, B_k, P_k,
                        delta_u_2, delta_a_1, delta_a_0, delta_y_0):

        # Prediction process
        ## predicted (a priori) model parameter estimate
        B_k = B_k

        ## predicted (a priori) model parameter estimate variance
        P_k = P_k + self.Q

        # Update process
        ## innovation variance
        H = np.dot(np.dot(self.C,self.A),delta_u_2)
        Matrix = np.dot(self.C,np.dot(self.A,self.A))
        R_k = np.dot(np.dot(Matrix,deltaStateVar),Matrix.T) + np.dot(np.dot(H,P_k),H.T) + \
              np.dot(np.dot(np.dot(self.C,self.A),self.W),np.dot(self.C,self.A).T) + np.dot(np.dot(self.C,self.W),self.C.T) + self.V

        ## updated Kalman gain
        K = np.dot(np.dot(P_k,H.T),np.linalg.inv(R_k))

        ## updated (a posteriori) model parameter estimate
        error = delta_y_0-(np.dot(np.dot(np.dot(self.C,self.A),self.A),deltaState) + np.dot(H,B_k) +
                           np.dot(np.dot(np.dot(self.C,self.A),self.gamma),delta_a_1) + np.dot(np.dot(self.C,self.gamma),delta_a_0))
        B_k = B_k + np.dot(K,error)

        ## updated (a posteriori) model parameter estimate variance
        P_k = np.dot((np.eye(len(P_k))-np.dot(K,H)),P_k)

        return B_k, P_k

    def passiveDetector(self, B_k, P_k):

        # Alarm if the derived probability that model parameter value
        # falls into safe region does not exceed the probability threshold

        loc = B_k[0][0]
        scale = np.sqrt(P_k[0][0])
        cdf = stats.norm.cdf(self.safeRegion[1],loc,scale) - stats.norm.cdf(self.safeRegion[0],loc,scale)

        passive_alarm = 0
        if cdf<self.probThreshold:
            passive_alarm = 1

        return passive_alarm

    def activeDetector(self, delta):

        # Alarm if derived probability of occuring delta value of
        # the managed system's ouput does not exceed the probability threshold

        loc = 0.0
        scale = 0.1699
        prob6sigma = 0.999999981

        if delta<=loc:
            cdf = stats.norm.cdf(delta,loc,scale)
        else:
            cdf = 1.0-stats.norm.cdf(delta,loc,scale)

        active_alarm = 0
        if cdf<1.0-prob6sigma:
            active_alarm = 1

        return active_alarm