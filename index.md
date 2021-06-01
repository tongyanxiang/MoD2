---
title: "MoD2"
---

**MoD2** is a tool for timely and accurate detection of model deviation. Given runtime measurements of a control-based self-adaptive system, MoD2 gives an alarm when model deviation is detected.

* Research Paper: “Timely and Accurate Detection of Model Deviation in Self-adaptive Software-intensive Systems” (FSE'21)
    * [Paper preprint (PDF)](artifact/MoD2-fse2021.pdf)
* Research Artifact
    * [Subjects](https://github.com/tongyanxiang/MoD2/tree/main/subject): control-SASs with MoD2-based adaptation-supervision mechanism
    * [Experiments](https://github.com/tongyanxiang/MoD2/tree/main/experiment): offline MoD2 with the collected execution traces and reproduction of experimental results
    
----

## MoD2 
MoD2 is mainly composed of six functions which is implemented by Python. Please refer to [MoD2Template](https://github.com/tongyanxiang/MoD2/blob/main/subject/MoD2Template.py) for details.

### init
The init function holds the knowledge for detecting model deviation as follows:

**Nominal model (unary)**

```python
x(k) = A*x(k-1) + B*u(k-1)
y(k) = C*x(k)
```
where `x` is system state, `u` is the controller's output, and `y` is the managed system's output. `A` describes system’s delay property, `B` describes system’s controllability, and `C` describes system’s observability. The values of model parameters are determined by *system identification*. 

**Deviated model parameter value**

MoD2 focuses on model parameter that describes system's controllability. It estimates model parameter value `B_k` by calculating its posteriori distribution based on a priori estimate and the measurements (i.e., *Bayesian estimation*). Thus, we need to record the last estmate of model paramater value `B_k` and its estimate variance `P_k`. We can simply initialize `B_k` to its nominal value. The value of `P_k` can be estimated with execution traces or set from experience which quickly converges to the true value.

**System state**

Considering that system state value cannot be directly measured, MoD2 also needs to estimate system state value `deltaState` by calculating its posteriori distribution based on its priori estimate and the measurements. Thus, we also record the last estimate of system state value `deltaState` and its estimate variance `deltaStateVar`. We can simply initialize `deltaState` and `deltaStateVar` to zero/zeros.

**Uncertainty of model parameter value**

Due to the dynamic characteristics of software-intensive systems, model parameter value often changes over time. We call this *process noise*. MoD2 makes use of this feature and describes it as white Gaussian noise with variance `Q`. The `Q` can be variance of the difference values between direct compution values from execution traces and its nominal value.

**Uncertainty compensation terms**

  * `gamma`: slope of LTI model which describes the effect of environmental input on system state.
  * `w(k)`: measurement error of environmental input, described as white Gaussian noise with variance `W`.
  * `v(k)`: sensor noise of the managed system's output, described as white Gaussian noise with variance `V`.
  
The values of `gamma` and `W` are determined by system identification (e.g., linear regression), and `V` is given by knowledge or estimated by execution traces.

**Safe region**

The `safeRegion` is the necessary condition under which the controller’s behavior is guaranteed by control theory. For unary model paramter, it can be defined as the interval between a lower and upper bound which is derived from formal analysis or experimental study.

**Probability threshold**

The `probThreshold` is the probability over which an alarm is given. Its value is determined by users, generally set to 0.9973 (*three-sigma rule*) or 0.999999998 (*six-sigma rule*).

### observer

The observer function estimates system state value by Kalman filter, like the following one (unary system state value):

```python
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
  ## predicted (a priori) state estimate variance
  deltaState = self.A*deltaState + B_k*delta_u_2 + self.gamma*delta_a_1
  
  ## predicted (a priori) state estimate variance
  deltaStateVar = self.A*deltaStateVar*self.A + self.W

  return deltaState, deltaStateVar
```
For each adaptation loop, the observer updates the last predicted system state value (the input `deltaState` and `deltaStateVar`) with historical managed system's output `delta_y_2` and predicts current system state (the output `deltaState` and `deltaStateVar`) with the controller's output `delta_u_2` and the environmental input `delta_a_1` based on the nominal model (i.e, `self.A`,  `self.B` and `self.C`), environmental uncertainty (i.e, `self.gamma`) and measurement error (i.e, `self.W` and `self.V`).

### estimator

The estimator function estimates model parameter value by Kalman filter, like the following one (unary model parameter value):

```python
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
```
For each adaptation loop, the estimator predicts current model parameter value based on the last estimate (i.e, the input `B_k` and `P_k`) and process noise. Then, it uses the last system state estimate (i.e, the input `deltaState` and `deltaStateVar`) and current measurements (i.e., the input `delta_u_1`, `delta_a_0` and `delta_y_0`) to update current model parameter value (i.e, the output `B_k` and `P_k`) based on the nominal model (i.e, `self.A`,  `self.B` and `self.C`), environmental uncertainty (i.e, `self.gamma`) and measurement error (i.e, `self.W` and `self.V`).

### passiveDetector

Given the controller’s safe region (i.e, `safeRegion`) and probability threshold (i.e, `probThreshold`), the passiveDetector calculates the probability that estimated model parameter value falls within safe region by a cumulative distribution function (i.e, the CDF of normal distribution). An alarm will be given when the derived `probability` exceeds `probThreshold`.
```python
def passiveDetector(self, B_k, P_k):

  ## mean
  loc = B_k

  ## standard deviation
  scale = np.sqrt(P_k)

  ## derived probability that calculated by cumulative distribution function
  probability = stats.norm.cdf(safeRegion[1],loc,scale) - \
                stats.norm.cdf(safeRegion[0],loc,scale)

  ## whether give the alarm
  passive_alarm = 0
  if probability<probThreshold:
      passive_alarm = 1

  return passive_alarm
```

### activeDetector

The activeDetector gives an alarm if the `probability` of occurring  `delta` value (e.g., residual) of measured system's output is less than a small probability threshold (e.g., `1.0-prob6sigma`).

```python
def activeDetector(self, delta):

  ## mean
  loc = 0.0

  ## standard deviation
  ## etimate with execution traces
  scale = 0

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
```

### deviationDetector

The deviationDetector is main function of MoD2 with the input of runtime controller's output `u_1`, environmental input `a`, and the managed system's output `y`, like this:

```python
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
```
   * First, the deviationDetector uses the difference values (i.e, `delta_y_2`, `delta_u_2`, `delta_a_1` and `delta_u_1`, `delta_a_0`, `delta_y_0`) of the inputs (i.e, ` self.list_u`, ` self.list_a`, ` self.list_y`) to estimate model parameter value for avoiding the multiplier effect of environmental uncertainty and measurement error.
   * Second, the deviationDetector invokes *observer* and *estimator* to estimate system state and model parameter values iteratively. 
   * Third, the passiveDetector judges whether gives an alarm with the estimated normal distribution (i.e, `N(B_k,P_k)`) of model parameter value and the activeDetector is supplemented to judge whether gives an alarm with the managed system's output when the controller's output is unchanged or zeros. 

----

MoD2 is an open-source tool published under [GPLv3](artifact/LICENSE).
