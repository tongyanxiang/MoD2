import os
from MoD2VideoEncoder import *

def evaluateEffectiveness4VideoEncoder():

    # settings
    settlingTime = 12

    print("\nload test configurations...")

    # load negative test configurations
    evalNegativeTraceDir = "../trace/evalNegativeTrace"
    evalNegativeTraceFiles = os.listdir(evalNegativeTraceDir)
    evalNegativeTraceFiles.sort()

    list_negative_quality = []
    list_negative_originalSize = []
    list_negative_compressedSize = []

    negativeNum = 0
    for file in evalNegativeTraceFiles:

        evalNegativeTraceFilePath = evalNegativeTraceDir + "/" + file
        fr = open(evalNegativeTraceFilePath, "r")
        evalNegativeTraceLines = fr.readlines()
        fr.close()

        list_negative_quality.append([])
        list_negative_originalSize.append([])
        list_negative_compressedSize.append([])

        for k in range(0, len(evalNegativeTraceLines)):
            res = evalNegativeTraceLines[k].strip().split(",")
            list_negative_quality[negativeNum].append(int(res[1]))
            list_negative_originalSize[negativeNum].append(float(res[2]))
            list_negative_compressedSize[negativeNum].append(float(res[3]))

        negativeNum = negativeNum + 1

    # load positive test configurations
    evalPositiveTraceDir = "../trace/evalPositiveTrace"
    evalPositiveTraceFiles = os.listdir(evalPositiveTraceDir)
    evalPositiveTraceFiles.sort()

    list_positive_modelDeviationTime = []
    list_positive_quality = []
    list_positive_originalSize = []
    list_positive_compressedSize = []

    positiveNum = 0
    for file in evalPositiveTraceFiles:

        # extract model deviation time from file name
        fileStr = str.split(file, "-")
        index = fileStr.index("t")
        modelDeviationTime = int(fileStr[index+1])
        list_positive_modelDeviationTime.append(modelDeviationTime)

        evalPositiveTraceFilePath = evalPositiveTraceDir + "/" + file
        fr = open(evalPositiveTraceFilePath, "r")
        evalPositiveTraceLines = fr.readlines()
        fr.close()

        list_positive_quality.append([])
        list_positive_originalSize.append([])
        list_positive_compressedSize.append([])

        for n in range(0, len(evalPositiveTraceLines)):
            res = evalPositiveTraceLines[n].strip().split(",")
            list_positive_quality[positiveNum].append(int(res[1]))
            list_positive_originalSize[positiveNum].append(float(res[2]))
            list_positive_compressedSize[positiveNum].append(float(res[3]))

        positiveNum = positiveNum + 1

    print("\napply MoD2...")

    # apply detector to negative test configurations
    list_negative_alarm_index = []
    for n in range(0, negativeNum):

        detector = MoD2VideoEncoder()

        alarmIndex = -1
        for k in range(settlingTime, len(list_negative_quality[n])):

            # u(k-1), a(k), y(k)
            alarm = detector.deviationDetector(list_negative_quality[n][k-1],
                                               list_negative_originalSize[n][k],
                                               list_negative_compressedSize[n][k])

            if alarm == 1:
                alarmIndex = k
                break

        list_negative_alarm_index.append(alarmIndex)

    # apply detector to positive test configurations
    list_positive_alarm_index = []
    for n in range(0, positiveNum):

        detector = MoD2VideoEncoder()

        alarmIndex = -1
        for k in range(settlingTime, len(list_positive_quality[n])):

            # u(k-1), a(k), y(k)
            alarm = detector.deviationDetector(list_positive_quality[n][k-1],
                                               list_positive_originalSize[n][k],
                                               list_positive_compressedSize[n][k])

            if alarm == 1:
                alarmIndex = k
                break

        list_positive_alarm_index.append(alarmIndex)

    print("\n*** statistical result ***")

    # false positive rate
    FPNum2Negative = 0
    for n in range(0, len(list_negative_alarm_index)):
        if list_negative_alarm_index[n] > 0:
            FPNum2Negative = FPNum2Negative + 1

    FPNum2Positive = 0
    for n in range(0, len(list_positive_alarm_index)):
        if list_positive_alarm_index[n] >= 0 and list_positive_alarm_index[n] < list_positive_modelDeviationTime[n]:
            FPNum2Positive = FPNum2Positive + 1

    FPRate = (FPNum2Negative + FPNum2Positive)/(negativeNum + positiveNum)
    print("False Positice Rate: {}%".format(round(FPRate*100, 1)))

    # false negative rate
    list_detection_delay = []
    for n in range(0, len(list_positive_alarm_index)):

        if list_positive_alarm_index[n] >= list_positive_modelDeviationTime[n]:
            list_detection_delay.append(list_positive_alarm_index[n] - list_positive_modelDeviationTime[n])

    FNRate = 1.0 - len(list_detection_delay)/positiveNum
    print("False Negative Rate: {}%".format(round(FNRate*100, 1)))

    # mean time delay
    if len(list_detection_delay) > 0:
        meanTimeDelay = np.mean(list_detection_delay)
    else:
        meanTimeDelay = -1
    print("Mean Time Delay: {}s\n".format(round(meanTimeDelay/30, 2)))


if __name__ == "__main__":
    print("\n~~~~~ Evaluating effectiveness of MoD2 ~~~~~")
    evaluateEffectiveness4VideoEncoder()