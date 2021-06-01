import numpy as np
from scipy import stats

class MoD2SWaT:
    # Model-guided model Deviation Detector

    def __init__(self):

        # Nominal model parameters
        self.A = np.zeros((3,3))

        self.B = np.array([[0.42592, -0.37037, 0.0, 0.0, 0.0, 0.0],
                           [0.0, 0.0, 0.37037, -0.37037, 0.0, 0.0],
                           [0.0, 0.0, 0.0, 0.0, 0.37037, -0.037036]])

        self.C = np.array([[1.0, 0.0, 0.0],
                           [0.0, 1.0, 0.0],
                           [0.0, 0.0, 1.0]])

        # Deviated model parameter
        self.B_k = self.B.T
        self.P_k = 2.0e-07*np.eye(6)

        # System state
        self.state = np.zeros((3,3))
        self.stateVar = np.zeros((3,3))

        # Uncertainty of model parameter value
        self.Q = 2.0e-07*np.eye(6)

        # Uncertainty compensation terms
        self.gamma = np.zeros((3,3))

        self.W = np.zeros((3,3))

        self.V = np.array([[0.00080, 0.0, 0.0],
                           [0.0, 0.00080, 0.0],
                           [0.0, 0.0, 0.00080]])

        # Safe region of model parameter values
        self.percent = [[0.35, 0.35], [0.35, 0.35],
                        [0.35, 0.35], [0.35, 0.35],
                        [0.35, 0.35], [3.50, 3.50]]

        self.safeRegion = np.array([[self.B[0][0]-self.percent[0][0]*abs(self.B[0][0]), self.B[0][0]+self.percent[0][1]*abs(self.B[0][0])],
                                    [self.B[0][1]-self.percent[1][0]*abs(self.B[0][1]), self.B[0][1]+self.percent[1][1]*abs(self.B[0][1])],

                                    [self.B[1][2]-self.percent[2][0]*abs(self.B[1][2]), self.B[1][2]+self.percent[2][1]*abs(self.B[1][2])],
                                    [self.B[1][3]-self.percent[3][0]*abs(self.B[1][3]), self.B[1][3]+self.percent[3][1]*abs(self.B[1][3])],

                                    [self.B[2][4]-self.percent[4][0]*abs(self.B[2][4]), self.B[2][4]+self.percent[4][1]*abs(self.B[2][4])],
                                    [self.B[2][5]-self.percent[5][0]*abs(self.B[2][5]), self.B[2][5]+self.percent[5][1]*abs(self.B[2][5])]])

        # Probability threshold
        self.probThreshold = 0.999999998  # 6sigma

        # Alarm signal
        self.alarm = np.zeros(6)

        # Historical measurements
        self.list_u = []
        self.list_y = []

    def deviationDetector(self, u_1, y):

        if len(self.list_u)<3:
            self.list_u.append(u_1)
            self.list_y.append(y)
        else:
            self.list_u.append(u_1)
            self.list_y.append(y)

            # State estimation
            y_2 = self.list_y[0]
            u_2 = self.list_u[1]

            if u_2[0][0]>0 or u_2[1][0]>0 or u_2[2][1]>0 or u_2[3][1]>0 or u_2[4][2]>0 or u_2[5][2]>0:
                self.state, self.stateVar = self.observer(self.B_k, self.state, self.stateVar, y_2, u_2)

            # Model parameter estimation and deviation detection
            u_1 = self.list_u[2]
            y_0 = self.list_y[2]

            # Passive detector
            if u_1[0][0]>0 or u_1[1][0]>0 or u_1[2][1]>0 or u_1[3][1]>0 or u_1[4][2]>0 or u_1[5][2]>0:
                self.B_k, self.P_k = self.estimator(self.state, self.stateVar, self.B_k, self.P_k, u_1, y_0)
                self.alarm = self.passiveDetector(self.B_k, self.P_k)

            # Active detector
            ## Tank101
            if u_1[0][0]==0 and u_1[1][0]==0:
                delta = y_0[0][0]
                self.alarm[0] = self.alarm[1] = self.activeDetector(delta)

            ## Tank301
            if u_1[2][1]==0 and u_1[3][1]==0:
                delta = y_0[1][1]
                self.alarm[2] = self.alarm[3] = self.activeDetector(delta)

            ## Tank401
            if u_1[4][2]==0 and u_1[5][2]==0:
                delta = y_0[2][2]
                self.alarm[4] = self.alarm[5] = self.activeDetector(delta)

            # Update historical measurements
            self.list_u.remove(self.list_u[0])
            self.list_y.remove(self.list_y[0])

        return self.alarm

    def observer(self, B_k, state, stateVar, y_2, u_2):

        # Update process
        ## innovation variance
        R_k = np.dot(np.dot(self.C,stateVar),self.C) + self.V

        ## updated Kalman gain
        K = np.dot(np.dot(stateVar,self.C.T),np.linalg.inv(R_k))

        ## updated (a posteriori) state estimate
        error = y_2 - np.dot(self.C,stateVar)
        state = state + np.dot(K,error)

        ## updated (a posteriori) state estimate variance
        stateVar = np.dot((np.eye(len(stateVar))-np.dot(K,self.C)),stateVar)

        # Prediction process
        ## predicted (a priori) state estimate
        state = np.dot(self.A,state) + np.dot(B_k.T,u_2)

        ## predicted (a priori) state estimate variance
        stateVar = np.dot(np.dot(self.A,stateVar),self.A) + self.W

        return state, stateVar

    def estimator(self, state, stateVar, B_k, P_k, u_1, y_0):

        # Prediction process
        ## predicted (a priori) model parameter estimate
        B_k = B_k

        ## predicted (a priori) model parameter estimate variance
        for i in range(0, len(P_k)):
            if abs(u_1[i][int(i/2)])>0.0:
                P_k[i,i] = P_k[i,i] + self.Q[i,i]

        # Update process
        ## innovation variance
        H = np.dot(self.C,u_1.T)
        R_k = np.dot(np.dot(np.dot(self.C,self.A),stateVar), np.dot(self.C,self.A).T) + np.dot(np.dot(H,P_k),H.T) + np.dot(np.dot(self.C,self.W),self.C.T) + self.V

        ## updated Kalman gain
        K = np.dot(np.dot(P_k,H.T),np.linalg.inv(R_k))

        ## updated (a posteriori) model parameter estimate
        error = y_0 - (np.dot(np.dot(self.C,self.A),state) + np.dot(H,B_k))
        B_k = B_k + np.dot(K,error)

        ## updated (a posteriori) model parameter estimate variance
        for i in range(0, len(P_k)):
            if abs(u_1[i][int(i/2)])>0.0:
                P_k[i,i] = (1.0 - np.dot(K,H)[i][i])*P_k[i,i]

        return B_k, P_k

    def passiveDetector(self, B_k, P_k):

        # Alarm if the derived probability that model parameter value
        # falls into safe region exceeds the probability threshold

        cdf = np.zeros(6)

        # tank101
        loc = B_k[0][0]
        scale = np.sqrt(P_k[0][0])
        cdf[0] = abs(stats.norm.cdf(self.safeRegion[0][1],loc,scale) - stats.norm.cdf(self.safeRegion[0][0],loc,scale))

        loc = B_k[1][0]
        scale = np.sqrt(P_k[1][1])
        cdf[1] = stats.norm.cdf(self.safeRegion[1][1],loc,scale) - stats.norm.cdf(self.safeRegion[1][0],loc,scale)

        # tank301
        loc = B_k[2][1]
        scale = np.sqrt(P_k[2][2])
        cdf[2] = stats.norm.cdf(self.safeRegion[2][1],loc,scale) - stats.norm.cdf(self.safeRegion[2][0],loc,scale)

        loc = B_k[3][1]
        scale = np.sqrt(P_k[3][3])
        cdf[3] = stats.norm.cdf(self.safeRegion[3][1],loc,scale) - stats.norm.cdf(self.safeRegion[3][0],loc,scale)

        # tank401
        loc = B_k[4][2]
        scale = np.sqrt(P_k[4][4])
        cdf[4] = stats.norm.cdf(self.safeRegion[4][1], loc, scale) - stats.norm.cdf(self.safeRegion[4][0], loc, scale)

        loc = B_k[5][2]
        scale = np.sqrt(P_k[5][5])
        cdf[5] = stats.norm.cdf(self.safeRegion[5][1], loc, scale) - stats.norm.cdf(self.safeRegion[5][0], loc, scale)

        size = len(P_k)
        passive_alarm = np.zeros(size)
        for i in range(0, size):
            if cdf[i] < self.probThreshold:
                passive_alarm[i] = 1

        return passive_alarm

    def activeDetector(self, delta):

        # Alarm if derived probability of occuring delta value of
        # the managed system's ouput is less tha probability threshold

        loc = 0.0
        scale = np.sqrt(self.V[0][0])

        if delta<=loc:
            cdf = stats.norm.cdf(delta,loc,scale)
        else:
            cdf = 1.0-stats.norm.cdf(delta,loc,scale)

        active_alarm = 0
        if cdf < 1.0-self.probThreshold:
            active_alarm = 1

        return active_alarm