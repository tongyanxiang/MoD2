## Secure Water Treatment testbed (SWaT)

SWaT is a fully operational scaled-down water treatment plant that produces doubly-filtered drinking water. SWaT consists of five water-processing tanks, as well as the pipes that connect those tanks. The in-coming valve and out-going valve of each tank can be controlled remotely via network. The objective of a self-adaptive SWaT system is to enable safe (e.g., no overflow or underflow in any of the tanks) and efficient (e.g., maximum clean water production) water filtering under different environmental situations (e.g., the
initial water level of the five tanks, and the in-coming water flow of the first tank). 

We extend a [SWaT simulator](https://sav.sutd.edu.sg/research/physical-attestation/sp-2018-paper-supplementary-material/) and implement our MoD2-based adaptation-supervision mechanism.

### The implementation of SWaT is as follows:
* The IO.py file instantiates the input output classes for communication between Programmable Logic Controller (PLC) and plant.
* The SCADA.py file instantiates the input output classes for communication between PLC and HMI.
* The plc/ directory contains 6 PLC classes files (**optimal controllers**).
* The HMI/HMI.py implements HMI classes to support SCADA.py.
* The controlblocks/logicblock.py implements PLC subfunction classes to support building the PLC classes.
* The io_plc/IO_PLC.py implements classes to support IO.py.
* The logicblock/controlblock.py implements useful functions like Timers and Alarms used in PLC class.
* The plant/plant.py implements the plant model and designed **mandatory controller**.
* The supervision/ directory contains **MoD2** and **switcher**.
* The result/swatRes.txt records the measurements (i.e, `U_{k-1}` and `Y_k`), model parameter value estimate (i.e, `B_k`, `BVar`), and the alarm signal (i.e, `alarm`) for each adaptation loop.

### Main control loop and model deviaton detection

The main control loop is implemented in **swat.py** as follows:
```Python
...
...

# Main Loop Body
...
for time in range(0, maxstep):
    # Second, Minute and Hour pulses
    Sec_P = not bool(time%int(1.0/tau))
    Min_P = not bool(time%(int(1.0/tau)*60))

    # Solving out plant odes in 0.05s
    Plant.Actuator(IO_P1,IO_P2,IO_P3,IO_P4,IO_P5,IO_P6,HMI,switcher)
    Plant.Plant(IO_P1,IO_P2,IO_P3,IO_P4,IO_P5,IO_P6,HMI)

    # Measured water levels
    if switcher.getSwithMode()==0 and time%intervalNum==0:
        list_YS.append([HMI.LIT101.Pv,HMI.LIT301.Pv,HMI.LIT401.Pv])

    # Supervision
    if switcher.getSwithMode() == 0:
	...

    # Control signal
    if switcher.getSwithMode() == 0:
    	...

    # PLC working
    PLC1.Pre_Main_Raw_Water(IO_P1,HMI)
    PLC2.Pre_Main_UF_Feed_Dosing(IO_P2,HMI)
    PLC3.Pre_Main_UF_Feed(IO_P3,HMI,Sec_P,Min_P)
    PLC4.Pre_Main_RO_Feed_Dosing(IO_P4,HMI)
    PLC5.Pre_Main_High_Pressure_RO(IO_P5,HMI,Sec_P,Min_P)
    PLC6.Pre_Main_Product(IO_P6,HMI)
...
...
```
* For each 50ms, water levels of five tanks will be measured and the optimal controllers will be activated.
* The adaptation-supervision mechanism is implemented by inserting model deviation detection before activating the controllers.
* The *MoD2* (supervision/MoD2.py) performs model deviation detection and updates the switching parameter `switchMode`(in supervision/switcher.py).
* The *mandatory controller* (in plant/plant.py) is activated based on the value of `switchMode`.

### Running SWaT

The main function is implemented in swat.py, you can run it in a terminal.

	python3 swat.py
	
and the terminal output looks like this：
```
tau: 0.05s, maxstep: 36000

d: 1.0s, intervalNum: 20

Initializing Plant

init: [498.5885, 827.4722, 875.6601, 351.1663, 273.3779]

Defining I/Os

Initializing SCADA HMI

Initializing PLCs

	PLC1 started

	PLC2 Started

	PLC3 Started

	PLC4 Started

	PLC5 Started

	PLC6 Started

Initializing supervision

Now starting simulation

Ending simulation: no alarm
```

### Requirements
* Unbutu 18.04
* Python 3.7 (with numpy, scipy)
