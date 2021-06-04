import numpy as np
from scipy import stats

class MoD2Template:
    # Model-guided model Deviation Detector

    def __init__(self):

        # Notation:
        ## 'xxx': a scalar or numerical array/matrix

        # Nominal model parameters
        self.A = 'xxx'       # describe system’s delay property
        self.B = 'xxx'       # describe system’s controllability
        self.C = 'xxx'       # describe system’s observability

        # Deviated model parameter
        ## focus on model parameter that describes system's controllability
        ## initialize to its nominal value
        self.B_k = self.B

        ## estimate variance of model parameter value
        ## initial value can be etimated with execution traces
        self.P_k = 'xxx'

        # System state
        ## focus on difference of current and the last system state
        ## initialize to zero/zeros
        self.deltaState = 'xxx'

        ## estimate variance of system state
        ## initialize to zero/zeros
        self.deltaStateVar = 'xxx'

        # Uncertainty of model parameter value
        ## process noise of deviated model parameter
        ## etimated with execution traces
        self.Q = 'xxx'

        # Uncertainty compensation terms
        ## LTI model which describes the effect of environmental input on system state
        ## etimated by system identification (e.g., linear regression)
        self.gamma = 'xxx'

        ## measurement error of environmental input
        ## etimated by system identification (e.g., variance of linear regression)
        self.W = 'xxx'

        ## sensor noise of the managed system's output
        ## given by knowledge or estimated by execution traces
        self.V = 'xxx'

        # Safe region of model parameter value
        ## derived from formal analysis or experimental study (e.g.,[0.0, 7.73975])
        self.safeRegion = 'xxx'

        # Probability threshold
        ## determined by users, generally 0.9973 (3sigma) or 0.999999998 (6sigma)
        self.probThreshold = 'xxx'

        # Alarm signal
        self.alarm = 0
        
        # Historical measurements
        self.list_u = []    # historical controller's output
        self.list_a = []    # historical environmental input
        self.list_y = []    # historical managed system’s output

        # Settings
        ## control delay d is the least positive integer that makes H=C*A^{d-1}*delta_u_{d} non-zeros
        ## d=1 when there is no delay of actuators
        self.d = 'xxx'

    def deviationDetector(self, u_1, a, y):

        # Main function of MoD2
        ## Input
        ###  u_1: the controller's output
        ###  a: the environmental input
        ###  y: the managed system’s output
        ## output: alarm(0/1)

        # Notation
        ## delta_u/a/y_dAn: difference value of the controller’s output/environmental/input/
        ##                  managed system’s output at time point k-(d+n) (k is current time point)
        ## delta_u/a/y_dMn: difference value of the controller’s output/environmental/input/
        ##                  managed system’s output at time point k-(d-n)

        if len(self.list_u) < self.d+2:
            self.list_u.append(u_1)
            self.list_a.append(a)
            self.list_y.append(y)
        else:
            self.list_u.append(u_1)
            self.list_a.append(a)
            self.list_y.append(y)

            # State estimation
            delta_y_dA1 = self.list_y[1] - self.list_y[0]
            delta_u_dA1 = self.list_u[2] - self.list_u[1]
            delta_a_dA0 = self.list_a[2] - self.list_a[1]

            self.deltaState, \
            self.deltaStateVar = self.observer(self.B_k, self.deltaState, self.deltaStateVar,
                                               delta_y_dA1, delta_u_dA1, delta_a_dA0)

            # Model parameter estimation and deviation detection
            delta_u_dM0 = self.list_u[3] - self.list_u[2]

            if abs(delta_u_dM0)>0:
                delta_a_dM1 = self.list_a[3] - self.list_a[2]
                ...
                delta_a_dMd = self.list_a[self.d+2] - self.list_a[self.d+1]
                delta_y_dMd = self.list_y[self.d+2] - self.list_y[self.d+1]

                self.B_k, self.P_k = self.estimator(self.deltaState, self.deltaStateVar, self.B_k, self.P_k,
                                                    delta_u_dM0, delta_a_dM1, "..." , delta_a_dMd, delta_y_dMd)

                self.alarm = self.passiveDetector(self.B_k, self.P_k)

            else:
                # Delta imformation about measured system output, it depends on applied controller
                ## e.g., PI controller
                setpoint = 'xxx'                           # tracking value of the managed system's ouput
                delta = self.list_y[self.d+2] - setpoint   # residual

                self.alarm = self.activeDetector(delta)

            # Update historical measurements
            self.list_u.remove(self.list_u[0])
            self.list_a.remove(self.list_a[0])
            self.list_y.remove(self.list_y[0])

        return self.alarm

    def observer(self, B_k, deltaState, deltaStateVar,
                       delta_y_dA1, delta_u_dA1, delta_a_dA0):

        # State estimation implemented by Kalman fiter

        # Notation
        ## *: scalar/matrix multiplication

        # Update process
        ## innovation variance
        R_k = self.C*deltaStateVar*self.C + self.V

        ## updated Kalman gain
        K = deltaStateVar*self.C*np.linalg.inv(R_k)

        ## updated (a posteriori) state estimate
        error = delta_y_dA1 - self.C*deltaState
        deltaState = deltaState + K*error

        ## updated (a posteriori) state estimate variance
        deltaStateVar = (np.eye(len(deltaStateVar)) - K*self.C)*deltaStateVar

        # Prediction process
        ## predicted (a priori) state estimate
        deltaState = self.A*deltaState + B_k*delta_u_dA1 + self.gamma*delta_a_dA0

        ## predicted (a priori) state estimate variance
        deltaStateVar = self.A*deltaStateVar*self.A + self.W

        return deltaState, deltaStateVar

    def estimator(self, deltaState, deltaStateVar, B_k, P_k,
                        delta_u_dM0, delta_a_dM1, ellipsis, delta_a_dMd, delta_y_dMd):

        # Model parameter estimation implemented by Kalman fiter

        # Notation
        ## *: scalar/matrix multiplication
        ## self.A^{n}: n scalar/matrix A are multiplied
        ## ellipsis: "..."

        # Prediction process
        ## predicted (a priori) model parameter estimate
        B_k = B_k

        ## predicted (a priori) model parameter estimate variance
        P_k = P_k + self.Q

        # Update process
        ## innovation variance
        H = self.C*self.A^{self.d-1}*delta_u_dM0
        R_k = (self.C*self.A^{self.d})*deltaStateVar*(self.C*self.A^{self.d}).T + H*self.P_k*H.T + \
              (self.C*self.A^{self.d-1})*self.W*(self.C*self.A^{self.d-1}).T + ... + self.C*self.W*self.C.T + self.V

        ## updated Kalman gain
        K = P_k*H*np.linalg.inv(R_k)

        ## updated (a posteriori) model parameter estimate
        error = delta_y_dMd - (self.C*self.A^{self.d}*deltaState + H*B_k + \
                               self.C*self.A^{self.d-1}*self.gamma*delta_a_dM1 + ... + self.C*self.gamma*delta_a_dMd)
        B_k = B_k + K*error

        ## updated (a posteriori) model parameter estimate variance
        P_k = (np.eye(len(P_k))-K*H)*P_k

        return B_k, P_k

    def passiveDetector(self, B_k, P_k):

        # Alarm if the derived probability that model parameter value
        # falls into safe region does not exceed the probability threshold

        ## mean
        loc = B_k

        ## standard deviation
        scale = np.sqrt(P_k)

        ## derived probability that calculated by cumulative distribution function
        probability = stats.norm.cdf(self.safeRegion[1],loc,scale) - \
                      stats.norm.cdf(self.safeRegion[0],loc,scale)

        ## whether give the alarm
        passive_alarm = 0
        if probability<self.probThreshold:
            passive_alarm = 1

        return passive_alarm

    def activeDetector(self, delta):

        # Alarm if derived probability of occuring delta value of
        # the managed system's ouput does not exceed the probability threshold

        ## mean
        loc = 0.0

        ## standard deviation
        ## etimate with execution traces
        scale = 'xxx'

        ## derived probability that calculated by cumulative distribution function
        prob6sigma = 0.999999981
        if delta<=loc:
            probability = stats.norm.cdf(delta,loc,scale)
        else:
            probability = 1.0-stats.norm.cdf(delta,loc,scale)

        ## whether give the alarm
        active_alarm = 0
        if probability<1.0-prob6sigma:
            active_alarm = 1

        return active_alarm