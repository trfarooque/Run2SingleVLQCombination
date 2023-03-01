#!/bin/bash

macroDir=${VLQCOMBDIR}/macros/
fitDir=${VLQCOMBDIR}/data/fits/
trexfDir=${VLQCOMBDIR}/data/trexf/


#make a temporary directory where all work will be done
mkdir -p tmp_plotting
cd tmp_plotting

#soft link all the necessary fit directories
cp -as ${fitDir}/SPT_HTZT_TS_M16K050_MU0_ASIMOV .
cp -as ${fitDir}/SPT_OSML_TS_M16K050_MU0_ASIMOV .
cp -as ${fitDir}/SPT_MONOTOP_TS_M16K050_MU0_ASIMOV . 
cp -as ${fitDir}/SPT_combined_TS_M16K050_MU0_ASIMOV .

#Run TRexFitter
trex-fitter m ${trexfDir}/configFile_multifit_TS_M16K050.txt

#move the results of the plotting to the right directory
mv Compare_TS_M16K050 ${trexfDir}/.
cd ..
rm -r tmp_plotting
