## Rice University Bidding System (RUBiS)

RUBiS is a web auction system that can adapt to workload/network changes by adjusting the number of servers to satisfy quality-of-service levels. 

### Negative and positive test configurations
* The negative test configurations use the original settings of [RUBiS](https://github.com/tongyanxiang/MoD2/tree/main/subject/RUBiS) and the environmental input (user workload) is generated based on two real-world workloads (provided in subfolder **trace/realworldworkload**).
* The positive configurations are derived by introducing network jamming, simulated by changing `serviceTime` of the configuration file **swim.ini** in folder [RUBiS/swim/simulations/](https://github.com/tongyanxiang/MoD2/tree/main/subject/RUBiS) at a random model deviation time point.

### Collected traces
For each test configuration, the execution trace records time steps, optimal controller's ouput, arrival rate of user requests, and measured average response time, as follows:
```
15,1,22.1833,0.259712
16,1,23.1167,0.437486
17,1,21.45,0.161149
18,1,24.2,0.49579
19,1,21.9833,0.227609
20,1,22.0333,0.36344
21,1,21.9167,0.246306
22,1,22.3167,0.246975
...
```
We have collected 200 negative traces and 200 positive traces at the length of 90 adaptation loops

### Reproduction of experimental results
We provide two scripts to reproduce experimental reuslts of the effectiveness and usefulness.

* **Effectiveness**
  * Unzip RUBiSTraces.zip and move subfolders *evalNegativeTrace* and *evalPositiveTrace* to *RUBiS/trace*
  * Go to *RUBiS/detector* and run *evaluateEffectiveness4RUBiS.py* in a terminal. The output looks like this:
    ```
    ~~~~~ Evaluating effectiveness of MoD2 ~~~~~

    load test configurations...

    apply MoD2...

    *** statistical result ***
    False Positive Rate: 0.25%
    False Negative Rate: 0.0%
    Mean Time Delay: 0.0s
    ```
    The mean time delay turns out better due to the addition of activeDetector which is mentioned in our paper and there exists only one false positive trace due to activeDetector. We will revise this in the camera ready version.

* **Usefulness**
  * Unzip RUBiSTraces.zip and move subfolders *evalNegativeTrace* and *evalPositiveTrace* to *RUBiS/trace*
  * Go to subfoler *RUBiS/detector* and run *evaluateUsefulness4RUBiS.py* in a terminal. The output looks like this:
    ```
    ~~~~~~ Evaluating usefulness of MoD2 ~~~~~

    processing...

    *** original control-SAS ***
    deviation time: 3173.4s
    abnormal time: 1953.0s
    abnormal rate: 61.1%


    processing...

    *** MoD2-based adaptation-supervision mechanism ***
    deviation time: 3173.4s
    abnormal time: 60.0s
    abnormal rate: 2.0%
    ```
    Also, the abnormal rate turns out better due to the addition of activeDetector.
