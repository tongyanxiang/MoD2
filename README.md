## MoD2 (Model-guided Deviation Detection）

Homage: [https://tongyanxiang.github.io/MoD2/](https://tongyanxiang.github.io/MoD2/)

**MoD2** is a tool for timely and accurate detection of model deviation. Given runtime measurements of a control-based self-adaptive system, MoD2 gives an alarm when model deviation is detected.

* Research Paper: “Timely and Accurate Detection of Model Deviation in Self-Adaptive Software-Intensive Systems” (FSE'21)
    * [Paper preprint (PDF)](https://tongyanxiang.github.io/MoD2/artifact/MoD2-fse2021.pdf)
* Research Artifact
    * [Subjects](https://github.com/tongyanxiang/MoD2/tree/main/subject): control-SASs with MoD2-based adaptation-supervision mechanism
    * [Experiments](https://github.com/tongyanxiang/MoD2/tree/main/experiment): offline MoD2 with the input of collected execution traces and reproduction of experimental results
    * [Dataset](https://drive.google.com/drive/folders/1FO80jwV4m8lejJU3kHSdE7ESZkuRf2T1?usp=sharing): please first download the collected execution traces! 
    * [VirtualBox image](https://drive.google.com/drive/folders/1FO80jwV4m8lejJU3kHSdE7ESZkuRf2T1?usp=sharing): a MoD2 image *MoD2-artifacts-20210604.ova* (about 5G and may take significant time to download) with research artifacts and all requirements is also provided. 

* Installation and execution

   * Required environment
      * Unbutu 18.04
      * Python 3.7 (with numpy, scipy)
      * OMNeT++ 5.5.1 and Boost 1.65.1 (for RUBiS)
      * imagemagick (for video encoder)
      
   * Download the repository and its required [dataset](https://drive.google.com/drive/folders/1FO80jwV4m8lejJU3kHSdE7ESZkuRf2T1?usp=sharing)
   
   * Go to the subfloder to execute each implementation, the instructions of each implementation are shown in subfloder's README file. The **artifact** is organized as follows:
   ```
   .
   ├── experiment: offline MoD2
       ├── README.md: artifact structure of experiments
       └── SWaT
            ├── README.md: execution instructions
            └── ...
       └── RUBiS
            ├── README.md: execution instructions
            └── ...
       └── VideoEncoder
            ├── README.md: execution instructions
            └── ...
   └── subject: MoD2-based adaptation-supervision mechanism
       ├── README.md: artifact structure of subjects' mechanisms
       └── SWaT
            ├── README.md: execution instructions
            └── ...
       └── RUBiS
            ├── README.md: execution instructions
            └── ...
       └── VideoEncoder
            ├── README.md: execution instructions
            └── ...
     ```
