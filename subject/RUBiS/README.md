## Rice University Bidding System (RUBiS)

RUBiS is a web auction system that can adapt to workload/network changes by adjusting the number of servers to satisfy quality-of-service levels. We extend a [RUBiS simulator](https://github.com/cps-sei/swim) and implement our MoD2-based adaptation-supervision mechanism.

### The implementation of RUBiS is as follows:

* The swim/simulations directory contains the **configuration (swim.ini)**, **system architecture (swim.ned)** and **run script (runexp.sh)** files
    * The subfolder *traces* contains the **workload trace file (workloadTrace.delta)**.
* The swim/src/managers directory implements a managing system with probes and actuator.
    * The subfolder *execution* implements the **actuator** for adding or removing servers.
    * The subfolder *monitor* implements the **probes** for collecting observations in real time and the **monitor** for analyzing the collected data and triggering each adaptation loop.
    * The subfolder *plan* contains a control-based **optimal controller**.
* The swim/src/model directory implements the **model** for keeping and updating system status.
* The swim/src/modules directory contains the files for simulating the process of servers' handling incoming user requests.
    * The *GenerateSource* module generates **user requests (jobs)** according to arrival time intervals read from  **workloadTrace.delta**.
    * The *ArrivalMonitor* module receives the generated user requests and broadcasts their **creation time**.
    * The *AppServer* module processes user requests following **limited processor sharing queue (LPS)**.
    * The *SinkMonitor* module receives the processed user requests and broadcasts their **response time** to the **probes** based on the **creation time**.
* The swim/src/supervision/ directory contains **MoD2**, **mandatory controller**, and **switcher**.
* The swim/result directory contains the **detection trace (RUBiSRes.txt)** of running MoD2 online.
    * The *RUBiSRes.txt* records the measurements (i.e, `u_{k-1}`, `a_k` and `y_k`), model parameter value estimate (i.e, `B_k`, `P_k`), and the alarm signal (i.e, `alarm`) for each adaptation loop.

### Main control loop and model deviaton detection

The main control loop is implemented in **swim/src/managers/monitor/SimpleMonitormpleMonitor.cc** as follows:

```C++
void SimpleMonitor::handleMessage(cMessage *msg) {
  ...
  ...
        if (simTime() > simulationWarmTime) {
            // measurements
            measuredArrivalRate = pModel->getEnvironment().getArrivalRate();

            double sensorNoise = normal(0.0, 0.001, RNG);
            while(pModel->getObservations().avgResponseTime + sensorNoise<0.0){
                sensorNoise = normal(0.0, 0.001, RNG);
            }
            measuredAvgRespTime = pModel->getObservations().avgResponseTime + sensorNoise;

            // trigger control
            cMessage *controlEvent = new cMessage("controlEvent");
            send(controlEvent, "out");
        }
  ...
  ...
}
```
* For each 60s, the measurements `measuredArrivalRate` and `measuredAvgRespTime` will be updated and a control event will be triggered.
* The adaptation-supervision mechanism is implemented by sending `controlEvent` to the *MoD2* module instead of *OptimalController* module.
* The *MoD2* module performs model deviation detection and activates the *Switcher* module for updating the switching parameter `triggerMandatoryCtrl`.
* The *Switcher* module activates *OptimalController* module or *MandatoryController* module based on the value of `triggerMandatoryCtrl`.

### Installation
* Download OMNeT++ 5.5.1 and install it following the installation guide 
* Make sure that OMNeT++ bin directory is in the PATH, otherwise add it:
   ```
   export PATH=$PATH:/home/tong/omnetpp-5.5.1/bin
   ```
* Install boost
   ```
   sudo apt-get install libboost-all-dev
   ```
* Unzip the files **queueinglib.zip** and **swim.zip** in *RUBiS* directory
* Go to *RUBiS* and compile queueinglib
   ```
   cd queueinglib
   make
   ```
* Go to *RUBiS* and compile swim
   ```
   cd swim
   make  
   ```
   
### Running RUBiS
* Run the simulation
    ```
    cd RUBiS/swim/simulations
    ./runexp.sh
    ```
* The terminal output looks like this：
    ```
    OMNeT++ Discrete Event Simulation  (C) 1992-2019 Andras Varga, OpenSim Ltd.
    Version: 5.5.1, build: 190613-08ba16f914, edition: Academic Public License -- NOT FOR COMMERCIAL USE
    See the license for distribution terms and warranty disclaimer

    Setting up Cmdenv...

    Loading NED files from .:  1
    Loading NED files from ../src:  14
    Loading NED files from ../../queueinglib:  20

    Preparing for running configuration General, run #0...
    Assigned runID=General-0-20210601-11:44:42-2200
    Setting up network "SWIM"...
    Initializing...
    t=0 [GenerateSource] read 141679 elements from traces/workloadTrace.delta and arrivalTime is 6300s
    t=0 [Model] initialize server brownoutFactor=0 maxServers=10
    t=0 [Model] initialize uncertainty bootDelay=60
    t=0 [Model] initialize control loop controlPeriod=60 warmTimeSteps=15
    t=0 [OptimalController] controlServers=1
    t=0 [MoD2] Delete RUBiSRes.txt
    t=0 [Model] initialServers=1
    t=0 [ExecutionManagerMod] executing doAddServer(id=16)
    t=0 [Model] addServer bootDelay=0 serverCount=1 active=0 numServerBooting=1 numServerShutting=0 expected=1
    push id=16 time=0
    t=0 [ExecutionManagerMod] executing doAddServerBootComplete(id=16): update booted server name=server1 and connect gates
    t=0 [Model] serverBecameActive serverCount=1 active=1 numServerBooting=0 numServerShutting=0 expected=0
    t=0 [ExecutionManagerModBase] addServer(id=16) complete
    t=0 [SimpleMonitor] initialize simulationWarmTime=900

    Running simulation...
    ** Event #0   t=0   Elapsed: 1.5e-05s (0m 00s)   ev/sec=0
    t=960 [MoD2] controlServers[0]=1 measuredArrivalRate[0]=22.1 measuredAvgRespTime[0]=0.222468
    t=960 [OptimalController] measuredAvgRespTime[0]=0.222468 controlServers[0]=1
    t=1020 [MoD2] controlServers[1]=1 measuredArrivalRate[1]=22.4833 measuredAvgRespTime[1]=0.453465
    t=1020 [OptimalController] measuredAvgRespTime[1]=0.453465 controlServers[1]=1
    t=1080 [MoD2] controlServers[2]=1 measuredArrivalRate[2]=22.2167 measuredAvgRespTime[2]=0.20305
    t=1080 [OptimalController] measuredAvgRespTime[2]=0.20305 controlServers[2]=1
    t=1140 [MoD2] controlServers[3]=1 measuredArrivalRate[3]=23.4333 measuredAvgRespTime[3]=0.267316
    t=1140 [OptimalController] measuredAvgRespTime[3]=0.267316 controlServers[3]=1
    t=1200 [MoD2] controlServers[4]=1 measuredArrivalRate[4]=20.5333 measuredAvgRespTime[4]=0.221034
    t=1200 [MoD2] B_k=1 P_k=0.001 alarm=0
    ...
    ...
    t=6300 [MoD2] controlServers[89]=2 measuredArrivalRate[89]=22.0167 measuredAvgRespTime[89]=0.0500886
    t=6300 [MoD2] B_k=1.37309 P_k=0.00144148 alarm=0
    t=6300 [OptimalController] measuredAvgRespTime[89]=0.0500886 controlServers[89]=2
    ** Event #1133907   t=6320   Elapsed: 83.8887s (1m 23s)   ev/sec=15300.3

    <!> Simulation time limit reached -- at t=6320s, event #1133907

    Calling finish() at end of Run #0...

    End.
    ```
