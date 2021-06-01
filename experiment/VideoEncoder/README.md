## Video encoder (VideoEncoder)

Video encoder is a video compression and streaming system that adaptively changes compression parameter to balance video's size and quality.

### Negative and positive test configurations
* The negative test configurations use the original settings of video encoder and the environment input (video stream) is extracted from real-world surveillance video streams, like this:
  * negativeVideo01 https://www.youtube.com/watch?v=wqlO5i3N-FU  
  * negativeVideo02 https://www.youtube.com/watch?v=6rgEyQ9YFh8  
  * negativeVideo03 https://www.youtube.com/watch?v=MNn9qKG2UFI&t=1s  
* The positive test configurations are derived from different kinds of real-world video streams (advertisement or animation clip video) at a random model deviation time point, like this:
  * positveVideo01 https://www.youtube.com/watch?v=98GXzGYwtn4
  * positveVideo02 https://www.youtube.com/watch?v=Pii224aV-jY

### Collected traces
For each test configuration, the execution trace records frame id, optimal controller's ouput, data size of original frame, and data size of compressed frame as follows:
```
7171,35,1265.3505859375,123.0439453125
7172,40,1266.6962890625,137.1484375
7173,45,1266.2294921875,148.2216796875
7174,50,1266.296875,160.912109375
7175,53,1266.1494140625,171.6806640625
7176,55,1265.5419921875,179.30859375
7177,57,1265.501953125,183.0703125
7178,58,1265.4912109375,189.564453125
7179,58,1265.0478515625,193.1025390625
7180,58,1264.59765625,192.9443359375
...
```
* We have collected 200 negaitive traces and 200 positive traces at the length of 900 adaptation loops

### Reproduction of experimental results
We provide two scripts to reproduce experimental reuslts of the effectiveness and usefulness.

#### Effectiveness
 * Unzip VideoEncoderTraces.zip and move subfolders *evalNegativeTrace* and *evalPositiveTrace* to *VideoEncoder/trace*
 * Go to *VideoEncoder/detector* and run *evaluateEffectiveness4VideoEncoder.py* in a terminal. The output looks like this:

```
~~~~~ Evaluating effectiveness of MoD2 ~~~~~

load test configurations...

apply MoD2...

*** statistical result ***
False Positice Rate: 3.0%
False Negative Rate: 2.0%
Mean Time Delay: 0.0s
```
The mean time delay turns out better than our preprint paper due to the addition of activeDetector which is mentioned in our approach. We will revise this in the carmera ready version.

#### Usefulness
 * Unzip VideoEncoderTraces.zip and move subfolders *evalNegativeTrace* and *evalPositiveTrace* to *VideoEncoder/trace*
 * Go to *VideoEncoder/detector* and run *evaluateUsefulness4VideoEncoder.py* in a terminal. The output looks like this:

```
~~~~~~ Evaluating usefulness of MoD2 ~~~~~

processing...

*** original control-SAS ***
deviation time: 18.18s
abnormal time: 2.92s
abnormal rate: 16.2%


processing...

*** MoD2-based adaptation-supervision mechanism ***
deviation time: 18.18s
abnormal time: 0.08s
abnormal rate: 0.4%
```
