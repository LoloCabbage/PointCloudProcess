# Geo1015-04-PointClouds
This is the repository for geo1015 assignment 4.
## Code 
include all codes used in the assignment
### Proprocessing
include all the code used to thinning,filtering,buffering 
just click "run" then you can test them
### Main.py
Main.py is used to run the steps integrately.
You can run any of the step3 to 5 in it with the parameters you set.
All the file and parameters of the functions in Main.py have been set defaultly according to the requirements of the assignment.(eg. the default output resolution is 0.5m).
This could make the operation very slow, so we strongly recommend to change the resolution parameters to a smaller number.

-Input data: ../data/process

-Output data:../data/result
## data
  include the processed data and result data 
### Process
    1.thinning data -> used to test
    2.buffering data -> used in step3
    3.filter.laz -> used in step4
### Result 
    1.dtm.tiff <- output of step3
    2.step4.tiff <- output of step4
    3.chm.tiff <- output of step5
