#!/bin/bash

macroDir=${VLQCOMBDIR}/macros/
fitDir=${VLQCOMBDIR}/data/fits/

mkdir -p ${fitDir}/SPT_HTZT_TS_M16K050_MU0_ASIMOV/Fits/
mkdir -p ${fitDir}/SPT_OSML_TS_M16K050_MU0_ASIMOV/Fits/
mkdir -p ${fitDir}/SPT_MONOTOP_TS_M16K050_MU0_ASIMOV/Fits/
mkdir -p ${fitDir}/SPT_combined_TS_M16K050_MU0_ASIMOV/Fits/

perl ${macroDir}/make_TRExNPfile.perl ${fitDir}/log_HTZT_minos.txt ${fitDir}/SPT_HTZT_TS_M16K050_MU0_ASIMOV/Fits/SPT_HTZT_TS_M16K050_MU0_ASIMOV.txt
perl ${macroDir}/make_TRExNPfile.perl ${fitDir}/log_OSML_minos.txt ${fitDir}/SPT_OSML_TS_M16K050_MU0_ASIMOV/Fits/SPT_OSML_TS_M16K050_MU0_ASIMOV.txt
perl ${macroDir}/make_TRExNPfile.perl ${fitDir}/log_MONOTOP_minos.txt ${fitDir}/SPT_MONOTOP_TS_M16K050_MU0_ASIMOV/Fits/SPT_MONOTOP_TS_M16K050_MU0_ASIMOV.txt
perl ${macroDir}/make_TRExNPfile.perl ${fitDir}/log_combined_minos.txt ${fitDir}/SPT_combined_TS_M16K050_MU0_ASIMOV/Fits/SPT_combined_TS_M16K050_MU0_ASIMOV.txt
