import os
from MoD2SWaT import *

def evaluateOriginalAbnormalRate():

    # settings
    tau = 0.05
    d = 1.0
    intervalNum = int(d/tau)

    print("\nprocessing...")

    evalAttackTraceFileDir = "../trace/evalAttackTrace_tau_" + str(tau)
    evalAttackTracefiles = os.listdir(evalAttackTraceFileDir)

    list_deviationTime = []
    list_abnormalTime = []

    for file in evalAttackTracefiles:

        fileStr = str.split(file, "_")
        index = fileStr.index("modelDeviationTime")
        modelDeviationTime = int(np.ceil(int(fileStr[index+1].split(".")[0])/intervalNum))

        evalAttackTraceFilePath = evalAttackTraceFileDir + "/" + file
        fr = open(evalAttackTraceFilePath, "r")
        evalAttackTraceLines = fr.readlines()
        fr.close()

        lineNum = 5
        intervalNum = int(d/tau)
        maxstep = int(len(evalAttackTraceLines)/lineNum/intervalNum)

        abnormalTime = 0
        for n in range(modelDeviationTime, maxstep):
            yRes = evalAttackTraceLines[lineNum*intervalNum*n].strip().split(",")

            YTRUE = np.zeros(5)
            for i in range(0, 5):
                YTRUE[i] = float(yRes[i])

            if YTRUE[0] < 250 or YTRUE[0] > 1100 or YTRUE[1] < 250 or YTRUE[1] > 1200 or YTRUE[2] < 250 or YTRUE[2] > 1200:
                abnormalTime = abnormalTime + d

        list_deviationTime.append(maxstep-modelDeviationTime)
        list_abnormalTime.append(abnormalTime)

    # abnormal rate
    list_abnormalRate = []
    for n in range(0, len(list_deviationTime)):
        abnormalRate = list_abnormalTime[n]/list_deviationTime[n]
        list_abnormalRate.append(abnormalRate)

    deviationMeanTime = np.mean(list_deviationTime)
    abnormalMeanTime = np.mean(list_abnormalTime)
    meanAbnormalRate = np.mean(list_abnormalRate)

    print("\n*** original control-SAS ***")
    print("deviation time: {}s".format(round(deviationMeanTime, 2)))
    print("abnormal time: {}s".format(round(abnormalMeanTime, 2)))
    print("abnormal rate: {}%\n".format(round(meanAbnormalRate*100, 1)))

def evaluateMoD2AbnormalRate():

    # settings
    tau = 0.05
    d = 1.0
    intervalNum = int(d/tau)

    print("\nprocessing...")

    evalAttackTraceFileDir = "../trace/evalAttackTrace_tau_" + str(tau)
    evalAttackTracefiles = os.listdir(evalAttackTraceFileDir)

    list_attack_modelDeviationTime = []
    list_attack_alarm_index = []

    for file in evalAttackTracefiles:
        #print(file)

        fileStr = str.split(file, "_")
        index = fileStr.index("modelDeviationTime")
        modelDeviationTime = int(np.ceil(int(fileStr[index+1].split(".")[0])/intervalNum))
        list_attack_modelDeviationTime.append(modelDeviationTime)

        evalAttackTraceFilePath = evalAttackTraceFileDir + "/" + file
        fr = open(evalAttackTraceFilePath, "r")
        evalAttackTraceLines = fr.readlines()
        fr.close()

        # apply detector
        detector = MoD2SWaT()

        lineNum = 5
        intervalNum = int(d/tau)
        maxstep = int(len(evalAttackTraceLines)/lineNum/intervalNum)
        alarmIndex = -1
        alarmFlag = 0

        for n in range(1, maxstep):

            U_101 = np.zeros(2)
            U_301 = np.zeros(2)
            U_401 = np.zeros(2)
            YS = np.zeros(3)

            # calculate U(k-1) loop
            for i in range(0, intervalNum):
                # MV101,MV201,MV301,MV302,MV303,MV304,MV501,MV502,MV503,MV504
                mvRes = evalAttackTraceLines[lineNum*intervalNum*(n-1)+lineNum*i+2].strip().split(",")
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
                pumpRes = evalAttackTraceLines[lineNum*intervalNum*(n-1)+lineNum*i+4].strip().split(",")
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
            yRes_old = evalAttackTraceLines[lineNum*intervalNum*(n-1)+1].strip().split(",")
            yRes = evalAttackTraceLines[lineNum*intervalNum*n+1].strip().split(",")
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

            alarm = detector.deviationDetector(U, Y)

            for i in range(0, len(alarm)):
                if alarm[i] == 1:
                    alarmIndex = n
                    alarmFlag = 1
                    break

            if alarmFlag == 1: break

        list_attack_alarm_index.append(alarmIndex)

    # abnormal rate after model deviation with MoD2-based adaptation-supervision mechanism
    list_deviationTime = []
    list_abnormalTime = []

    num = 0
    for file in evalAttackTracefiles:
        #print(file)

        evalAttackTraceFilePath = evalAttackTraceFileDir + "/" + file
        fr = open(evalAttackTraceFilePath, "r")
        evalAttackTraceLines = fr.readlines()
        fr.close()

        lineNum = 5
        intervalNum = int(d/tau)
        maxstep = int(len(evalAttackTraceLines)/lineNum/intervalNum)

        abnormalTime = 0
        if list_attack_alarm_index[num] < list_attack_modelDeviationTime[num]:

            for n in range(list_attack_modelDeviationTime[num], maxstep):

                yTrue = evalAttackTraceLines[lineNum*intervalNum*n].strip().split(",")

                YTRUE = np.zeros(3)
                for i in range(0, 3):
                    YTRUE[i] = float(yTrue[i])

                if YTRUE[0] < 250 or YTRUE[0] > 1100 or YTRUE[1] < 250 or YTRUE[1] > 1200 or YTRUE[2] < 250 or YTRUE[2] > 1200:
                    abnormalTime = abnormalTime + d

        else:
            for n in range(list_attack_modelDeviationTime[num], list_attack_alarm_index[num]+1):

                yTrue = evalAttackTraceLines[lineNum*intervalNum*n].strip().split(",")
                YTRUE = np.zeros(3)
                for i in range(0, 3):
                    YTRUE[i] = float(yTrue[i])

                if YTRUE[0] < 250 or YTRUE[0] > 1100 or YTRUE[1] < 250 or YTRUE[1] > 1200 or YTRUE[2] < 250 or YTRUE[2] > 1200:
                    abnormalTime = abnormalTime + d

        list_deviationTime.append(maxstep-list_attack_modelDeviationTime[num])
        list_abnormalTime.append(abnormalTime)

        num = num + 1

    # abnormal rate
    list_abnormalRate = []
    for n in range(0, len(list_deviationTime)):
        abnormalRate = list_abnormalTime[n]/list_deviationTime[n]
        list_abnormalRate.append(abnormalRate)

    deviationMeanTime = np.mean(list_deviationTime)
    abnormalMeanTime = np.mean(list_abnormalTime)
    meanAbnormalRate = np.mean(list_abnormalRate)

    print("\n*** MoD2-based adaptation-supervision mechanism ***")
    print("deviation time: {}s".format(round(deviationMeanTime,2)))
    print("abnormal time: {}s".format(round(abnormalMeanTime, 2)))
    print("abnormal rate: {}%\n".format(round(meanAbnormalRate*100,1)))


if __name__=='__main__':
    print("\n~~~~~~ Evaluating usefulness of MoD2 ~~~~~")
    evaluateOriginalAbnormalRate()
    evaluateMoD2AbnormalRate()
