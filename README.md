# Geo1015-04-PointClouds
This is the repository for geo1015 assignment 4.
## Code 
include all codes used in the assignment
### Proprocessing
include all the code used to thinning,filtering,buffering 
just click "run" then you can test them
### Main.py
Main.py is used to run the steps integrately.
You can run any of the step3 (interpolation) to 5 in it with the parameters you set.
All the file and parameters of the functions in Main.py have been set defaultly according to the requirements of the assignment.(eg. the default output resolution is 0.5m).
This could make the operation very slow, so we strongly recommend to change the resolution parameters to a smaller number.

-Input data: ../data/process

-Output data:../data/output
## data
  include the processed data and result data 
### Process
    1.tile_500_filtered.laz -> used in step4
    2.600_GP_output_threshold.laz -> used in interpolation/step4
### Result (All the results and output is stored in ../data/output)
    1.dtm.tiff <- output of interpolation
    2.step4.tiff <- output of step4
    3.chm.tiff <- output of step5
