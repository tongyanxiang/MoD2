## Video encoder (VideoEncoder)

Video encoder is a video compression and streaming system that adaptively changes compression parameter to balance video's size and quality.

### The implementation of VideoEncoder is as follows:
* The code/encoder.py implements the process of video compression with our proposed adaptation-supervison mechanism.
* The code/adaptation/ directory only contains control-based **optimal controller**
* The code/supervision/ directory contains **MoD2**, **mandatory controller**, and **switcher**.
* The code/result/VideoEncoderRes.txt records the measurements (i.e, `quality_{k-1}`, `originalSize_k` and `compressedSize_k`), model parameter value estimate (i.e, `B_k` and `BVar`), and the alarm signal (i.e, `alarm`) for each adaptation loop.
* The original/negative directory contains negative frames
* The original/positive directory contains positive frames

### Main control loop and model deviaton detection

The main control loop is implemented in **code/encoder.py** as follows:

```Python
def encoder():
    ...
    ...
    
    # load negative and positive frames
    list_frameFilePath = []
    ...
      
    # initialize controllers
    optCtrl = OptimalController()
    mandCtrl = MandatoryController()

    # initialize supervision
    detector = MoD2()
    switcher = Switcher()

    # main loop
    ...
    
    for n in range(0, len(list_frameFilePath)):
	...
	
        # supervision
   	...
        if switcher.getSwithMode()==0:
		...
                # u(k-1),a(k),y(k)
                alarm = detector.deviationDetector(quality,
                                                   originalSize,
                                                   compressedSize)
		...
		
                if alarm==1:
                    switcher.setSwitchMode(alarm)
        else:
	 	...
		
        # compute new control parameter
        if switcher.getSwithMode()==0:
            quality = optCtrl.PIControl(quality, compressedSize) # u(k)
        else:
            quality = mandCtrl.control(quality, compressedSize)  # u(k)   
    ...
```
* For each frame, the applied compression parameter (i.e, `quality`), the original and compressed size of current video frame (i.e, `originalSize` and `compressedSize`) are measured and the new compression parameter is computed by the optimal controller.
* The adaptation-supervision mechanism is implemented by inserting model deviation detection before computing the new control parameter.
* The *MoD2* (supervision/MoD2.py) performs model deviation detection and updates the switching parameter `switchMode` (in supervision/switcher.py).
* The *mandatory controller* (supervision/mandatoryController.py) is activated based on the value of `switchMode`.

### Running video encoder
  
The main function is implemented in *encoder.py*, you can run it in a terminal.

	python3 encoder.py
	
and the terminal output looks like this：
```
~~~~~ Running video encoder with MoD2-based adaptation-supervision mechanism ~~~~~
startFrame: 4603, quality: 30, settlingTime: 12

frame, quality_{k-1}, originalSize_k, compressedSize_k, B_k, BVar, alarm
4615, 58, 1236.3447265625, 194.99609375, 3.0959, 0.5, 0
4616, 58, 1236.8095703125, 195.033203125, 3.0959, 0.5, 0
4617, 58, 1236.6806640625, 194.998046875, 3.0959, 0.5, 0
4618, 58, 1237.3583984375, 195.115234375, 3.0959, 0.5, 0
4619, 58, 1238.4951171875, 195.138671875, 3.0959, 0.5, 0
4620, 58, 1238.837890625, 195.173828125, 3.0959, 0.5, 0
4621, 58, 1238.8515625, 195.138671875, 3.0959, 0.5, 0
4622, 58, 1238.849609375, 195.1025390625, 3.0959, 0.5, 0
4623, 58, 1238.728515625, 195.134765625, 3.0959, 0.5, 0
4624, 58, 1238.7353515625, 195.16015625, 3.0959, 0.5, 0
4625, 58, 1234.0341796875, 194.95703125, 3.0959, 0.5, 0
4626, 58, 1234.51953125, 195.0224609375, 3.0959, 0.5, 0
4627, 58, 1235.1025390625, 194.9443359375, 3.0959, 0.5, 0
4628, 58, 1234.8056640625, 194.8427734375, 3.0959, 0.5, 0
4629, 58, 1234.7392578125, 194.7763671875, 3.0959, 0.5, 0
...
```
