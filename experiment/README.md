## Experiment

For each subject, collecting execution traces of MoD2-based adaptation-supervision mechanism under different test configurations is time-consuming. Therefore, we provide an offline MoD2, control execution traces (collected without adaptation-supervision mechanism), and experimental scripts (for the reproduction of expriememtal results) for each suject.

### Structure

The **experiment artifact** is organized as follows:
```
.
├── RUBiS
    ├── README.md
    ├── detector
    │   └── evaluateEffectiveness4RUBiS.py
    │   └── evaluateUsefulness4RUBiS.py
    │   └── MoD2RUBiS.py
    └── trace
        └── evalNegativeTrace
        └── evalPositiveTrace
        └── realworld workload
└── SWaT
    ├── README.md
    ├── detector
    │   └── evaluateEffectiveness4SWaT.py
    │   └── evaluateEffectiveness4SWaTAttack.py
    │   └── evaluateUsefulness4SWaT.py
    │   └── MoD2SWaT.py
    └── trace
        └── swat_network_attacks.xlsx
        └── evalAttackTrace_tau_0.05
        └── evalNegativeTrace_tau_0.05
        └── evalPositiveTrace_tau_0.05
└── VideoEncoder
    ├── README.md
    ├── detector
    │   └── evaluateEffectiveness4VideoEncoder.py
    │   └── evaluateUsefulness4VideoEncoder.py
    │   └── MoD2VideoEncoder.py
    └── trace
        └── evalNegativeTrace
        └── evalPositiveTrace
  ```
  
#### Each sub-floder named after the suject (e.g., RUBiS) includes: 

* A README file that introduces how to reproduce expermental results
* A sub-folder that contains the MoD2 and scripts for statistical analysis of MoD2's effectiveness and usefulness.
* A sub-folder that contains execution traces under negative and positive (addition of attack for SWaT) test configuration without any adaptation-supervision mechanism.

#### Go to each sub-floder to reproduce experimental results now !!!
