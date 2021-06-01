import os
from MoD2VideoEncoder import *

def evaluateOriginalAbnormalRate():

    print("\nprocessing...")

    # load positive test configurations
    evalPositiveTraceDir = "../trace/evalPositiveTrace"
    evalPositiveTraceFiles = os.listdir(evalPositiveTraceDir)
    evalPositiveTraceFiles.sort()

    list_deviationTime = []
    list_abnormalTime = []

    for file in evalPositiveTraceFiles:

        # extract model deviation time from file name
        fileStr = str.split(file, "-")
        index = fileStr.index("t")
        modelDeviationTime = int(fileStr[index+1])

        evalPositiveTraceFilePath = evalPositiveTraceDir + "/" + file
        fr = open(evalPositiveTraceFilePath, "r")
        positiveTraceLines = fr.readlines()
        fr.close()

        traceLength = len(positiveTraceLines)
        abnormalTime = 0
        for n in range(modelDeviationTime, traceLength):
            res = positiveTraceLines[n].strip().split(",")
            compressedSize = float(res[3])

            if compressedSize>220:
                abnormalTime = abnormalTime + (1/30)

        list_deviationTime.append((traceLength-modelDeviationTime)/30)
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
    settlingTime = 12

    print("\nprocessing...")

    # load positive test configurations
    evalPositiveTraceDir = "../trace/evalPositiveTrace"
    evalPositiveTraceFiles = os.listdir(evalPositiveTraceDir)
    evalPositiveTraceFiles.sort()

    list_modelDeviationTime = []
    list_alarm_index = []

    for file in evalPositiveTraceFiles:

        # extract model deviation time from file name
        fileStr = str.split(file, "-")
        index = fileStr.index("t")
        modelDeviationTime = int(fileStr[index+1])
        # print("modelDeviationTime: {}".format(modelDeviationTime))))

        list_modelDeviationTime.append(modelDeviationTime)

        evalPositiveTraceFilePath = evalPositiveTraceDir + "/" + file
        fr = open(evalPositiveTraceFilePath, "r")
        positiveTraceTraceLines = fr.readlines()
        fr.close()

        # apply detector
        detector = MoD2VideoEncoder()

        alarmIndex = -1
        for n in range(settlingTime, len(positiveTraceTraceLines)):
            res_old = positiveTraceTraceLines[n-1].strip().split(",")
            res = positiveTraceTraceLines[n].strip().split(",")

            quality = int(res_old[1])
            originalSize = float(res[2])
            compressedSize = float(res[3])

            # u(k-1), a(k), y(k)
            alarm = detector.deviationDetector(quality,
                                               originalSize,
                                               compressedSize)

            if alarm == 1:
                alarmIndex = n
                break

        list_alarm_index.append(alarmIndex)

    # abnormal rate after model deviation with MoD2-based adaptation-supervision mechanism
    list_deviationTime = []
    list_abnormalTime = []

    num = 0
    for file in evalPositiveTraceFiles:

        evalPositiveTraceFilePath = evalPositiveTraceDir + "/" + file
        fr = open(evalPositiveTraceFilePath, "r")
        positiveTraceTraceLines = fr.readlines()
        fr.close()

        abnormalTime = 0
        traceLength = len(positiveTraceTraceLines)
        if list_alarm_index[num]<list_modelDeviationTime[num]:
            for n in range(list_modelDeviationTime[num], traceLength):

                res = positiveTraceTraceLines[n].strip().split(",")
                compressedSize = float(res[3])

                if compressedSize>220:
                    abnormalTime = abnormalTime + 1/30

        else:
            for n in range(list_modelDeviationTime[num], list_alarm_index[num]+1):

                    res = positiveTraceTraceLines[n].strip().split(",")
                    compressedSize = float(res[3])

                    if compressedSize>220:
                        abnormalTime = abnormalTime + 1/30

        list_deviationTime.append((traceLength-list_modelDeviationTime[num])/30)
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


if __name__ == "__main__":
    print("\n~~~~~~ Evaluating usefulness of MoD2 ~~~~~")
    evaluateOriginalAbnormalRate()
    evaluateMoD2AbnormalRate()