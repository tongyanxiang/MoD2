## Subject

For each subject, we instantiate a MoD2 following the provided MoD2 template and implement MoD2-based adaptation-supervision mechanism with the designed mandatory controller and switcher.

The **subject artifact** is organized as follows:

```
.
├── MoD2Template.py
└── RUBiS
    ├── README.md
    └── queueinglib.zip
    └── swim.zip
└── SWaT
    ├── README.md
    ├── controlblock
    │   └── controlblock.py
    ├── device
    │   └── device.py
    ├── HMI
    │   └── HMI.py   
    ├── io_plc
    │   └── IO_PLC.py
    ├── logicblock 
    │   └── logicblock.py
    ├── plant 
    │   └── plant.py
    ├── plc 
    │   └── plc1.py
    │   └── plc2.py 
    │   └── plc3.py
    │   └── plc4.py
    │   └── plc5.py   
    │   └── plc6.py
    ├── supervision
    │   └── MoD2.py  
    │   └── switcher.py
    ├── IO.py
    ├── SCADA.py  
    └── swat.py   
└── VideoEncoder
    ├── README.md
    └── code
        ├── encoder.py
        ├──adaptation
        │   └── optimalController.py 
        └── supervision
            └── mandatoryController.py
            └── MoD2.py 
            └── switcher.py
    └── original
        ├── negative
        └── positive
  ```
  
* MoD2Template.py gives the [framework](https://tongyanxiang.github.io/MoD2/) of implenenting model-guided model devaition detector.  
* Apart from functional code, each suject (e.g., RUBiS) should contains:
  * A README file that introduces the implementation and running of MoD2-based adaptation-supervision mechanism.
  * A subfolder named **supervision** that contains the MoD2, mandatory controller (SWaT implements it in plant.py) and switcher.
   
#### Go to each subfloder to learn more about MoD2-based adaptation-supervision mechanism now !!!
  
