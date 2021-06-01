import os

from io_plc.IO_PLC import DI_WIFI
from IO import *
from SCADA import H
from plc import plc1,plc2,plc3,plc4,plc5,plc6
from plant.plant import plant

from supervision.MoD2 import *
from supervision.switcher import *

# save data
if not os.path.exists("result"):
    os.makedirs("result")

resultFilePath = "result/swatRes.txt"
resultFile = open(resultFilePath, 'w+')

# time is counted in tau seconds, (1.0/tau)*x*y, x unit seconds, y unit minutes
tau = 0.05
maxstep = int(1.0/tau)*60*30
print("tau: {}s, maxstep: {}\n".format(tau, maxstep))

# supervision interval
d = 1.0
intervalNum = int(d/tau)
print("d: {}s, intervalNum: {}\n".format(d, intervalNum))

print("Initializing Plant\n")
init = [498.5885,827.4722,875.6601,351.1663,273.3779]
print("init: {}\n".format(init))

Plant = plant(tau, init)

print("Defining I/Os\n")
IO_DI_WIFI = DI_WIFI() # Whether PLC processes wireless signal
IO_P1 = P1()           # Define I/Os for sensors and actuators of each process
IO_P2 = P2()
IO_P3 = P3()
IO_P4 = P4()
IO_P5 = P5()
IO_P6 = P6()

print("Initializing SCADA HMI\n")
HMI = H()

print("Initializing PLCs\n")
PLC1 = plc1.plc1(HMI)
PLC2 = plc2.plc2(HMI)
PLC3 = plc3.plc3(HMI)
PLC4 = plc4.plc4(HMI)
PLC5 = plc5.plc5(HMI)
PLC6 = plc6.plc6(HMI)

print("Initializing supervision\n")
detector = MoD2()
switcher = Switcher()

# control signal and measured water level
U_101 = np.zeros(2)
U_301 = np.zeros(2)
U_401 = np.zeros(2)
list_YS = []

print("Now starting simulation\n")
outline = "time, U_{k-1}, Y_k, B_k, BVar, alarm"
resultFile.write(outline + "\n")
resultFile.flush()
#print(outline)

# Main Loop Body
num = 0
alarmTime = -1
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
        if int(time/intervalNum)>=1 and time%intervalNum==0:

            U = np.array([[U_101[0], 0.0, 0.0],
                          [U_101[1], 0.0, 0.0],
                          [0.0, U_301[0], 0.0],
                          [0.0, U_301[1], 0.0],
                          [0.0, 0.0, U_401[0]],
                          [0.0, 0.0, U_401[1]]])

            Y = np.array([[list_YS[len(list_YS)-1][0] - list_YS[len(list_YS)-2][0], 0.0, 0.0],
                          [0.0, list_YS[len(list_YS)-1][1] - list_YS[len(list_YS)-2][1], 0.0],
                          [0.0, 0.0, list_YS[len(list_YS)-1][2] - list_YS[len(list_YS)-2][2]]])

            # print(time, U[0][0], U[1][0], Y[0][0])
            # print(time, U[2][1], U[3][1], Y[1][1])
            # print(time, U[4][2], U[5][2], Y[2][2], "\n")

            # u(k-1), y(k)
            alarm = detector.deviationDetector(U, Y)
            B_k = detector.getBEstimate()
            BVar = detector.getBEstimateVariance()

            # save trace
            outline_u = "[" + str(U[0][0]) + ", " + str(U[1][0]) + ", "  + str(U[2][1]) + ", " + str(U[3][1]) + ", " + str(U[4][2]) + ", " + str(U[5][2]) + "]"
            outline_y = "[" + str(Y[0][0]) + ", " + str(Y[1][1]) + ", " + str(Y[2][2]) + "]"
            outline_B = "[" + str(B_k[0][0]) + ", " + str(B_k[1][0]) + ", "  + str(B_k[2][1]) + ", " + str(B_k[3][1]) + ", " + str(B_k[4][2]) + ", " + str(B_k[5][2]) + "]"
            outline_Var = "[" + str(BVar[0][0]) + ", " + str(BVar[1][1]) + ", " + str(BVar[2][2]) + ", " + str(BVar[3][3]) + ", " + str(BVar[4][4]) + ", " + str(BVar[5][5]) + "]"

            outline = str(int(time*tau)) + "s, " + outline_u + ", " + outline_y + ", " + outline_B + ", " + outline_Var + ", " + str(alarm) + "\n"
            resultFile.write(outline)
            resultFile.flush()

            #print("{}, {}, {}, {}, {}, {}".format(time, outline_u, outline_y, outline_B, outline_Var, alarm))

            for i in range(0, len(alarm)):
                if alarm[i] == 1:
                    switcher.setSwitchMode(alarm[i])
                    alarmTime = time
                    print("Ending simulation:")
                    print("alarm at time: {}s for B_{}".format(alarmTime, i))
                    print("B_k:\n{}".format(B_k))
                    print("BVar:\n{}\n".format(BVar))
                    break

            num = num + 1

    # Control signal
    if switcher.getSwithMode() == 0:
        if time%intervalNum == 0:
            U_101 = np.zeros(2)
            U_301 = np.zeros(2)
            U_401 = np.zeros(2)

        # U_101 = [sum(MV101), sum(P101||P102)]
        if IO_P1.MV101.DO_Open == 1:
            U_101[0] = round(U_101[0] + tau, 3)
        if IO_P1.P101.DO_Start == 1 or IO_P1.P102.DO_Start == 1:
            U_101[1] = round(U_101[1] + tau, 3)

        # U_301 = [sum(MV201&&(P101||P102)), sum(P301||P302)]
        if IO_P2.MV201.DO_Open == 1 and (IO_P1.P101.DO_Start == 1 or IO_P1.P102.DO_Start == 1):
            U_301[0] = round(U_301[0] + tau, 3)
        if IO_P3.P301.DO_Start == 1 or IO_P3.P302.DO_Start == 1:
            U_301[1] = round(U_301[1] + tau, 3)

        # U_401 = [sum((P301||P302)&&~MV301&&MV302&&~MV303&&~MV304&&~P602),
        #          sum(P401||P402)]
        if (IO_P3.P301.DO_Start == 1 or IO_P3.P302.DO_Start == 1) and \
            IO_P3.MV301.DO_Open == 0 and IO_P3.MV302.DO_Open == 1 and IO_P3.MV303.DO_Open == 0 and IO_P3.MV304.DO_Open == 0 and \
            IO_P6.P602.DO_Start == 0:
            U_401[0] = round(U_401[0] + tau, 3)
        if IO_P4.P401.DO_Start == 1 or IO_P4.P402.DO_Start == 1:
            U_401[1] = round(U_401[1] + tau, 3)

    # PLC working
    PLC1.Pre_Main_Raw_Water(IO_P1,HMI)
    PLC2.Pre_Main_UF_Feed_Dosing(IO_P2,HMI)
    PLC3.Pre_Main_UF_Feed(IO_P3,HMI,Sec_P,Min_P)
    PLC4.Pre_Main_RO_Feed_Dosing(IO_P4,HMI)
    PLC5.Pre_Main_High_Pressure_RO(IO_P5,HMI,Sec_P,Min_P)
    PLC6.Pre_Main_Product(IO_P6,HMI)

resultFile.close()

if alarmTime==-1:
    print("Ending simulation: no alarm\n")
