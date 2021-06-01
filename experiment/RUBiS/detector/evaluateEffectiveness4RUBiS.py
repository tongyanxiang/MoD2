import os
from MoD2RUBiS import *

def evaluateEffectiveness4RUBiS():

	# settings
	warmTime = 15
	traceLength = 105 - warmTime
	settlingTime = 12

	print("\nload test configurations...")

	# load negative test configurations
	evalNegativeDir = "../trace/evalNegativeTrace"
	evalNegativeFiles = os.listdir(evalNegativeDir)
	evalNegativeFiles.sort()

	list_negative_servers = []
	list_negative_measuredArrivalRate = []
	list_negative_measuredAvgRespTime = []

	negativeTraceNum = 0
	for file in evalNegativeFiles:

		evalNegativeFilePath = evalNegativeDir + "/" + file
		fr = open(evalNegativeFilePath, "r")
		negativeTraceLines = fr.readlines()
		fr.close()

		list_negative_servers.append([])
		list_negative_measuredArrivalRate.append([])
		list_negative_measuredAvgRespTime.append([])

		for k in range(0, traceLength):
			res = negativeTraceLines[k].strip().split(",")
			list_negative_servers[negativeTraceNum].append(float(res[1]))
			list_negative_measuredArrivalRate[negativeTraceNum].append(float(res[2]))
			list_negative_measuredAvgRespTime[negativeTraceNum].append(float(res[3]))

		negativeTraceNum = negativeTraceNum + 1

	# load positive test configurations
	evalPositiveDir = "../trace/evalPositiveTrace"
	evalPositiveFiles = os.listdir(evalPositiveDir)
	evalPositiveFiles.sort()

	list_positive_modelDeviationTime= []
	list_positive_servers = []
	list_positive_measuredArrivalRate = []
	list_positive_measuredAvgRespTime = []

	positiveTraceNum = 0
	for file in evalPositiveFiles:

		# extract model deviation time from file name
		fileStr = str.split(file, "-")
		index = fileStr.index("index")
		modelDeviationTime = int(fileStr[index+1].split(".")[0]) - warmTime
		list_positive_modelDeviationTime.append(modelDeviationTime)

		evalPositiveFilePath = evalPositiveDir + "/" + file
		fr = open(evalPositiveFilePath, "r")
		positiveTraceLines = fr.readlines()
		fr.close()

		list_positive_servers.append([])
		list_positive_measuredArrivalRate.append([])
		list_positive_measuredAvgRespTime.append([])

		for k in range(0, traceLength):
			res = positiveTraceLines[k].strip().split(",")
			list_positive_servers[positiveTraceNum].append(float(res[1]))
			list_positive_measuredArrivalRate[positiveTraceNum].append(float(res[2]))
			list_positive_measuredAvgRespTime[positiveTraceNum].append(float(res[3]))

		positiveTraceNum = positiveTraceNum + 1

	print("\napply MoD2...")

	# apply detector to negative test configurations
	list_negative_alarm_index = []
	for n in range(0, negativeTraceNum):

		detector = MoD2RUBiS()

		alarmIndex = -1
		for k in range(settlingTime, len(list_negative_servers[n])):

			# u(k-1), a(k), y(k)
			alarm = detector.deviationDetector(list_negative_servers[n][k-1],
									           list_negative_measuredArrivalRate[n][k],
									           list_negative_measuredAvgRespTime[n][k])

			if alarm==1:
				alarmIndex = k
				break

		list_negative_alarm_index.append(alarmIndex)

	# apply detector to positive test configurations
	list_positive_alarm_index = []
	for n in range(0, positiveTraceNum):

		detector = MoD2RUBiS()

		alarmIndex = -1
		for k in range(settlingTime, len(list_positive_servers[n])):

			# u(k-1), a(k), y(k)
			alarm = detector.deviationDetector(list_positive_servers[n][k-1],
								         	   list_positive_measuredArrivalRate[n][k],
									           list_positive_measuredAvgRespTime[n][k])

			if alarm==1:
				alarmIndex = k
				break

		list_positive_alarm_index.append(alarmIndex)

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

	FPRate = (FPNum2Negative + FPNum2Positive)/(negativeTraceNum + positiveTraceNum)
	print("False Positive Rate: {}%".format(round(FPRate*100, 2)))

	# false negative rate
	list_detection_delay = []
	for n in range(0, len(list_positive_alarm_index)):

		if list_positive_alarm_index[n] >= list_positive_modelDeviationTime[n]:
			list_detection_delay.append(list_positive_alarm_index[n] - list_positive_modelDeviationTime[n])

	FNRate = 1.0 - len(list_detection_delay)/positiveTraceNum
	print("False Negative Rate: {}%".format(round(FNRate*100,1)))

	# mean time delay
	if len(list_detection_delay)>0:
		meanTimeDelay = np.mean(list_detection_delay)
	else:
		meanTimeDelay = -1
	print("Mean Time Delay: {}s\n".format(round(meanTimeDelay*60.0, 2)))


if __name__ == "__main__":
	print("\n~~~~~ Evaluating effectiveness of MoD2 ~~~~~")
	evaluateEffectiveness4RUBiS()