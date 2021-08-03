import os
import shutil

from adaptation.optimalController import *
from supervision.MoD2 import *
from supervision.switcher import *
from supervision.mandatoryController import *

def encoder():

    # save detection result
    if not os.path.exists("result"):
        os.makedirs("result")

    resultFilePath = "result/VideoEncoderRes.txt"
    resultFile = open(resultFilePath, 'w+')

    # define input and output directory
    inputDir = "../original"
    outputDir = "../compressed"

    # delete old output directory and make new one
    if os.path.exists(outputDir):
        try:
            shutil.rmtree(outputDir)
        except OSError as e:
            print(e)
        else:
            print("folder compressed is deleted successfully\n")
    os.makedirs("../compressed/negative")
    os.makedirs("../compressed/positive")

    # load negative and positive frames
    list_frameFilePath = []

    negativeFrameFiles = os.listdir(inputDir + "/negative")
    negativeFrameFiles.sort()
    for n in range(0, len(negativeFrameFiles)):
        framePath = inputDir + "/negative/" + negativeFrameFiles[n]
        list_frameFilePath.append(framePath)

    positiveFrameFiles = os.listdir(inputDir + "/positive")
    positiveFrameFiles.sort()
    for n in range(0, len(positiveFrameFiles)):
        framePath = inputDir + "/positive/" + positiveFrameFiles[n]
        list_frameFilePath.append(framePath)

    # initialize controllers
    optCtrl = OptimalController()
    mandCtrl = MandatoryController()

    # initialize supervision
    detector = MoD2()
    switcher = Switcher()

    # main loop
    quality = 30
    settlingTime = 12
    print("quality: {}, settlingTime: {}\n".format(quality, settlingTime))

    # logging
    outline = "frame, quality_{k-1}, originalSize_k, compressedSize_k, B_k, BVar, alarm"
    resultFile.write(outline + "\n")
    resultFile.flush()
    print(outline)

    st = 0
    for n in range(0, len(list_frameFilePath)):

        img_in = list_frameFilePath[n]

        if "negative" in img_in:
            file = negativeFrameFiles[n]
            img_out = outputDir + "/negative/" + file
        elif "positive" in img_in:
            file = positiveFrameFiles[n-len(negativeFrameFiles)]
            img_out = outputDir + "/positive/" + file

        # frame size measurements
        convert(img_in, img_out, quality)
        originalSize = os.path.getsize(img_in)/1024  # y(k)
        compressedSize = os.path.getsize(img_out)/1024  # y(k)

        # supervision
        frame = int(os.path.basename(file).split(".")[0])

        if switcher.getSwithMode()==0:

            if st>settlingTime:

                # u(k-1),a(k),y(k)
                alarm = detector.deviationDetector(quality,
                                                   originalSize,
                                                   compressedSize)

                B_k = detector.getBEstimate()
                BVar = detector.getBEstimateVariance()

                # save trace
                outline = str(frame) + ", " + str(quality) + ", " + str(originalSize) + ", " + str(compressedSize)
                outline = outline + ", " + str(B_k) + ", " + str(BVar) + ", " + str(alarm) + "\n"
                resultFile.write(outline)
                resultFile.flush()

                # logging
                print("{}, {}, {}, {}, {}, {}, {}".format(frame, quality, originalSize, compressedSize, B_k, BVar, alarm))

                if alarm==1:
                    switcher.setSwitchMode(alarm)

        else:
            # save trace
            outline = str(frame) + ", " + str(quality) + ", " + str(originalSize) + ", " + str(compressedSize) +", NULL, NULL, 1\n"
            resultFile.write(outline)
            resultFile.flush()

            # logging
            print("{}, {}, {}, {}".format(frame, quality, originalSize, compressedSize))

        # compute new control parameter
        if switcher.getSwithMode()==0:
            quality = optCtrl.PIControl(quality, compressedSize) # u(k)
        else:
            quality = mandCtrl.control(quality, compressedSize)  # u(k)

        st = st + 1

    resultFile.close()

def convert(path_in, path_out, quality):
    # command = "magick convert -quality " + str(quality) + " "
    command = "convert -quality " + str(quality) + " "
    command += path_in + ' ' + path_out
    os.system(command)


if __name__ == "__main__":
    print("\n~~~~~ Running video encoder with MoD2-based adaptation-supervision mechanism ~~~~~")
    encoder()