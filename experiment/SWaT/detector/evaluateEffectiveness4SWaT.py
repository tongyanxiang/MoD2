import os
from MoD2SWaT import *

def evaluateEffectiveness4SWaT():

    # settings
    tau = 0.05
    d = 1.0
    intervalNum = int(d/tau)

    print("\nload negative test configurations and apply MoD2...")

    # load negative test configurations and apply MoD2
    evalNegativeTraceDir = "../trace/evalNegativeTrace_tau_" + str(tau)
    evalNegativeTracefiles = os.listdir(evalNegativeTraceDir)
    evalNegativeTraceNum = len(evalNegativeTracefiles)

    list_negative_alarm_index = []
    list_negative_alarm_location = []

    for file in evalNegativeTracefiles:
        #print(file)

        evalNegativeTraceFilePath = evalNegativeTraceDir + "/" + file
        fr = open(evalNegativeTraceFilePath, "r")
        evalNegativeTraceLines = fr.readlines()
        fr.close()

        # apply detector
        detetcor = MoD2SWaT()

        lineNum = 4
        maxstep = int(len(evalNegativeTraceLines)/lineNum/intervalNum)
        alarmIndex = -1
        alarmLocate = -1
        alarmFlag = 0

        for n in range(0, maxstep-1):

            U_101 = np.zeros(2)
            U_301 = np.zeros(2)
            U_401 = np.zeros(2)
            YS = np.zeros(3)

            # calculate U loop
            for i in range(0, intervalNum):
                # MV101,MV201,MV301,MV302,MV303,MV304,MV501,MV502,MV503,MV504
                mvRes = evalNegativeTraceLines[lineNum*intervalNum*n+lineNum*i+1].strip().split(",")
                MV101 = int(mvRes[0])
                MV201 = int(mvRes[1])
                MV301 = int(mvRes[2])
                MV302 = int(mvRes[3])
                MV303 = int(mvRes[4])
                MV304 = int(mvRes[5])
                MV501 = int(mvRes[6])
                MV502 = int(mvRes[7])
                MV503 = int(mvRes[8])
                MV504 = int(mvRes[9])

                # P101,P102,P301,P302,P401,P402,P501,P502,P601,P602
                pumpRes = evalNegativeTraceLines[lineNum*intervalNum*n+lineNum*i+3].strip().split(",")
                P101 = int(pumpRes[0])
                P102 = int(pumpRes[1])
                P301 = int(pumpRes[2])
                P302 = int(pumpRes[3])
                P401 = int(pumpRes[4])
                P402 = int(pumpRes[5])
                P501 = int(pumpRes[6])
                P502 = int(pumpRes[7])
                P601 = int(pumpRes[8])
                P602 = int(pumpRes[9])

                # U_101 = [sum(MV101), sum(P101||P102)]
                if MV101==1:
                    U_101[0] = round(U_101[0] + tau, 3)
                if P101==1 or P102==1:
                    U_101[1] = round(U_101[1] + tau, 3)

                # U_301 = [sum(MV201&&(P101||P102)), sum(P301||P302)]
                if MV201==1 and (P101==1 or P102==1):
                    U_301[0] = round(U_301[0] + tau, 3)
                if P301==1 or P302==1:
                    U_301[1] = round(U_301[1] + tau, 3)

                # U_401 = [sum((P301||P302)&&~MV301&&MV302&&~MV303&&~MV304&&~P602),
                #          sum(P401||P402)]
                if (P301==1 or P302==1) and MV301==0 and MV302==1 and MV303==0 and MV304==0 and P602==0:
                    U_401[0] = round(U_401[0] + tau, 3)
                if P401==1 or P402==1:
                    U_401[1] = round(U_401[1] + tau, 3)

            # YS101(k),YS301(k),YS401(k)
            yRes_old = evalNegativeTraceLines[lineNum*intervalNum*n].strip().split(",")
            yRes = evalNegativeTraceLines[lineNum*intervalNum*(n+1)].strip().split(",")
            for i in range(0, 3):
                YS[i] = float(yRes[i]) - float(yRes_old[i])

            # u(k-1), y(k)
            U = np.array([[U_101[0], 0.0, 0.0],
                          [U_101[1], 0.0, 0.0],
                          [0.0, U_301[0], 0.0],
                          [0.0, U_301[1], 0.0],
                          [0.0, 0.0, U_401[0]],
                          [0.0, 0.0, U_401[1]]])

            Y = np.array([[YS[0], 0.0, 0.0],
                          [0.0, YS[1], 0.0],
                          [0.0, 0.0, YS[2]]])

            alarm = detetcor.deviationDetector(U, Y)

            for i in range(0, len(alarm)):
                if alarm[i] == 1:
                    alarmIndex = n
                    alarmLocate = i
                    alarmFlag = 1
                    #print("MoD2 alarm index: {} locate at B_{}\n".format(alarmIndex, i))
                    break

            if alarmFlag==1: break

        list_negative_alarm_index.append(alarmIndex)
        list_negative_alarm_location.append(alarmLocate)

    print("\nload positive test configurations and apply MoD2...")

    # load positive test configurations and apply MoD2
    evalPositiveTraceFileDir = "../trace/evalPositiveTrace_tau_" + str(tau)
    evalPositiveTracefiles = os.listdir(evalPositiveTraceFileDir)
    evalPositiveTraceNum = len(evalPositiveTracefiles)

    list_positive_modelDeviationTime = []
    list_positive_alarm_index = []
    list_positive_alarm_location = []

    for file in evalPositiveTracefiles:
        #print(file)

        fileStr = str.split(file, "_")
        index = fileStr.index("modelDeviationTime")
        modelDeviationTime = int(np.ceil(int(fileStr[index+1].split(".")[0])/intervalNum))
        list_positive_modelDeviationTime.append(modelDeviationTime)

        evalPositiveTraceFilePath = evalPositiveTraceFileDir + "/" + file
        fr = open(evalPositiveTraceFilePath, "r")
        evalPositiveTraceLines = fr.readlines()
        fr.close()

        # apply detector
        detetcor = MoD2SWaT()

        lineNum = 5
        maxstep = int(len(evalPositiveTraceLines)/lineNum/intervalNum)
        alarmIndex = -1
        alarmLocate = -1
        alarmFlag = 0

        for n in range(0, maxstep-1):

            U_101 = np.zeros(2)
            U_301 = np.zeros(2)
            U_401 = np.zeros(2)
            YS = np.zeros(3)

            # calculate U loop
            for i in range(0, intervalNum):
                # MV101,MV201,MV301,MV302,MV303,MV304,MV501,MV502,MV503,MV504
                mvRes = evalPositiveTraceLines[lineNum*intervalNum*n+lineNum*i+2].strip().split(",")
                MV101 = int(mvRes[0])
                MV201 = int(mvRes[1])
                MV301 = int(mvRes[2])
                MV302 = int(mvRes[3])
                MV303 = int(mvRes[4])
                MV304 = int(mvRes[5])
                MV501 = int(mvRes[6])
                MV502 = int(mvRes[7])
                MV503 = int(mvRes[8])
                MV504 = int(mvRes[9])

                # P101,P102,P301,P302,P401,P402,P501,P502,P601,P602
                pumpRes = evalPositiveTraceLines[lineNum*intervalNum*n+lineNum*i+4].strip().split(",")
                P101 = int(pumpRes[0])
                P102 = int(pumpRes[1])
                P301 = int(pumpRes[2])
                P302 = int(pumpRes[3])
                P401 = int(pumpRes[4])
                P402 = int(pumpRes[5])
                P501 = int(pumpRes[6])
                P502 = int(pumpRes[7])
                P601 = int(pumpRes[8])
                P602 = int(pumpRes[9])

                # U_101 = [sum(MV101), sum(P101||P102)]
                if MV101 == 1:
                    U_101[0] = round(U_101[0] + tau, 3)
                if P101 == 1 or P102 == 1:
                    U_101[1] = round(U_101[1] + tau, 3)

                # U_301 = [sum(MV201&&(P101||P102)), sum(P301||P302)]
                if MV201 == 1 and (P101 == 1 or P102 == 1):
                    U_301[0] = round(U_301[0] + tau, 3)
                if P301 == 1 or P302 == 1:
                    U_301[1] = round(U_301[1] + tau, 3)

                # U_401 = [sum((P301||P302)&&~MV301&&MV302&&~MV303&&~MV304&&~P602),
                #          sum(P401||P402)]
                if (P301 == 1 or P302 == 1) and MV301 == 0 and MV302 == 1 and MV303 == 0 and MV304 == 0 and P602 == 0:
                    U_401[0] = round(U_401[0] + tau, 3)
                if P401 == 1 or P402 == 1:
                    U_401[1] = round(U_401[1] + tau, 3)

            # YS101(k),YS301(k),YS401(k)
            yRes_old = evalPositiveTraceLines[lineNum*intervalNum*n+1].strip().split(",")
            yRes = evalPositiveTraceLines[lineNum*intervalNum*(n+1)+1].strip().split(",")
            for i in range(0, 3):
                YS[i] = float(yRes[i]) - float(yRes_old[i])

            # u(k-1), y(k)
            U = np.array([[U_101[0], 0.0, 0.0],
                          [U_101[1], 0.0, 0.0],
                          [0.0, U_301[0], 0.0],
                          [0.0, U_301[1], 0.0],
                          [0.0, 0.0, U_401[0]],
                          [0.0, 0.0, U_401[1]]])

            Y = np.array([[YS[0], 0.0, 0.0],
                          [0.0, YS[1], 0.0],
                          [0.0, 0.0, YS[2]]])

            alarm = detetcor.deviationDetector(U, Y)

            # alarm index
            for i in range(0, len(alarm)):
                if alarm[i] == 1:
                    alarmIndex = n
                    alarmLocate = i
                    alarmFlag = 1
                    #print("MoD2 alarm index: {} locate at B_{}\n".format(alarmIndex, i))
                    break

            if alarmFlag==1: break

        list_positive_alarm_index.append(alarmIndex)
        list_positive_alarm_location.append(alarmLocate)

    print("\n*** statistical result ***")

    # false positive rate
    FPNum2Negative = 0
    for n in range(0, len(list_negative_alarm_index)):
        if list_negative_alarm_index[n]>0:
            FPNum2Negative = FPNum2Negative + 1

    FPNum2Positive = 0
    for n in range(0, len(list_positive_alarm_index)):
        if list_positive_alarm_index[n]>=0 and list_positive_alarm_index[n]<list_positive_modelDeviationTime[n]:
            FPNum2Positive = FPNum2Positive + 1

    FPRate = (FPNum2Negative + FPNum2Positive)/(evalNegativeTraceNum + evalPositiveTraceNum)
    print("False Positive Rate: {}%".format(round(FPRate*100, 1)))

    # false negative rate
    list_detection_delay = []
    for n in range(0, len(list_positive_alarm_index)):
        if list_positive_alarm_index[n] >= list_positive_modelDeviationTime[n]:
            list_detection_delay.append(list_positive_alarm_index[n]-list_positive_modelDeviationTime[n])

    FNRate = 1.0-len(list_detection_delay)/evalPositiveTraceNum
    print("False Negative Rate: {}%".format(round(FNRate*100, 1)))

    # mean time delay
    if len(list_detection_delay)>0:
        meanTimeDelay = np.mean(list_detection_delay)
    else:
        meanTimeDelay = -1
    print("Mean Time Delay: {}s\n".format(round(meanTimeDelay, 2)))


if __name__ == "__main__":
    print("\n~~~~~ Evaluating effectiveness of MoD2 ~~~~~")
    evaluateEffectiveness4SWaT()