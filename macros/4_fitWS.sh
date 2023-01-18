#!/bin/bash

baseDir=${VLQCOMBDIR}/data/
inDir=${baseDir}/workspaces/asimov_mu0_workspaces/
outDir=${baseDir}/fits/

WORKSPACEFILE=${inDir}/SPT_HTZT_TS_M16K050_MU0_ASIMOV.root
WORKSPACENAME=combined
DATASETNAME=asimovData_mu0
OUTPUTNAME=${outDir}/fits_SPT_HTZT_TS_M16K050_MU0_ASIMOV.root
quickFit -w ${WORKSPACENAME} -f ${WORKSPACEFILE} -d ${DATASETNAME} -p mu_signal=0 \
-o ${OUTPUTNAME} --savefitresult 1 --hesse 1 --minos 1 2>&1 |tee ${outDir}/log_HTZT_minos.txt

WORKSPACEFILE=${inDir}/SPT_OSML_TS_M16K050_MU0_ASIMOV.root
WORKSPACENAME=combWS
DATASETNAME=asimovData_mu0
OUTPUTNAME=${outDir}/fits_SPT_OSML_TS_M16K050_MU0_ASIMOV.root
quickFit -w ${WORKSPACENAME} -f ${WORKSPACEFILE} -d ${DATASETNAME} -p mu_signal=0 \
-o ${OUTPUTNAME} --savefitresult 1 --hesse 1 --minos 1 2>&1 |tee ${outDir}/log_OSML_minos.txt

WORKSPACEFILE=${inDir}/SPT_MONOTOP_TS_M16K050_MU0_ASIMOV.root
WORKSPACENAME=combined
DATASETNAME=asimovData_mu0
OUTPUTNAME=${outDir}/fits_SPT_MONOTOP_TS_M16K050_MU0_ASIMOV.root
quickFit -w ${WORKSPACENAME} -f ${WORKSPACEFILE} -d ${DATASETNAME} -p mu_signal=0 \
-o ${OUTPUTNAME} --savefitresult 1 --hesse 1 --minos 1 2>&1 |tee ${outDir}/log_MONOTOP_minos.txt


WORKSPACEFILE=${inDir}/TS_M16K050_combined_MU0_ASIMOV.root
WORKSPACENAME=combWS
DATASETNAME=asimovData_mu0
OUTPUTNAME=${outDir}/fits_TS_M16K050_combined_MU0_ASIMOV.root
quickFit -w ${WORKSPACENAME} -f ${WORKSPACEFILE} -d ${DATASETNAME} -p mu_signal=0 \
-o ${OUTPUTNAME} --savefitresult 1 --hesse 1 --minos 1 2>&1 |tee ${outDir}/log_combined_minos.txt
