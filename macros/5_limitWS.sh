#!/bin/bash

baseDir=${VLQCOMBDIR}/data/
inDir=${baseDir}/workspaces/asimov_mu0_workspaces/
outDir=${baseDir}/limits/

#WORKSPACEFILE=${inDir}/SPT_HTZT_TS_M16K050_MU0_ASIMOV.root
#WORKSPACENAME=combined
#DATASETNAME=asimovData_mu0
#OUTPUTNAME=${outDir}/limits_SPT_HTZT_TS_M16K050_MU0_ASIMOV.root
#quickLimit -w ${WORKSPACENAME} -f ${WORKSPACEFILE} -d ${DATASETNAME} -p mu_signal \
#-o ${OUTPUTNAME} 2>&1 |tee ${outDir}/log_HTZT_limit.txt

#WORKSPACEFILE=${inDir}/SPT_OSML_TS_M16K050_MU0_ASIMOV.root
#WORKSPACENAME=combWS
#DATASETNAME=asimovData_mu0
#OUTPUTNAME=${outDir}/limits_SPT_OSML_TS_M16K050_MU0_ASIMOV.root
#quickLimit -w ${WORKSPACENAME} -f ${WORKSPACEFILE} -d ${DATASETNAME} -p mu_signal \
#-o ${OUTPUTNAME} 2>&1 |tee ${outDir}/log_OSML_limit.txt

#WORKSPACEFILE=${inDir}/SPT_MONOTOP_TS_M16K050_MU0_ASIMOV.root
#WORKSPACENAME=combined
#DATASETNAME=asimovData_mu0
#OUTPUTNAME=${outDir}/limits_SPT_MONOTOP_TS_M16K050_MU0_ASIMOV.root
#quickLimit -w ${WORKSPACENAME} -f ${WORKSPACEFILE} -d ${DATASETNAME} -p mu_signal \
#-o ${OUTPUTNAME} 2>&1 |tee ${outDir}/log_MONOTOP_limit.txt

WORKSPACEFILE=${inDir}/SPT_combined_TS_M16K050_MU0_ASIMOV.root
WORKSPACENAME=combWS
DATASETNAME=asimovData_mu0
OUTPUTNAME=${outDir}/limits_SPT_combined_TS_M16K050_MU0_ASIMOV.root
quickLimit -w ${WORKSPACENAME} -f ${WORKSPACEFILE} -d ${DATASETNAME} -p mu_signal \
-o ${OUTPUTNAME} 2>&1 |tee ${outDir}/log_combined_limit.txt
