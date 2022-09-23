#!/bin/bash

#WORKSPACEFILE=/data/at3/scratch2/farooque/VLQCombination/SingleVLQCombination_2022/newCO/Run2SingleVLQCombination/data/workspaces/SPT_HTZT_TS_WT16K050.root                                                                                                
#DATASETNAME=asimovData

WORKSPACEFILE=/data/at3/scratch2/farooque/VLQCombination/SingleVLQCombination_2022/newCO/Run2SingleVLQCombination/data/workspaces/SPT_HTZT_TS_WT16K050_MU0_ASIMOV.root
WORKSPACENAME=combined
DATASETNAME=asimovData_mu0
OUTPUTNAME=output_TS_HTZT_mu0.root
quickFit -w ${WORKSPACENAME} -f ${WORKSPACEFILE} -d ${DATASETNAME} -p mu_signal=0 \
-o ${OUTPUTNAME} --savefitresult 1 --hesse 1 --minos 1 2>&1 |tee log_HTZT_minos.txt
              
WORKSPACEFILE=/data/at3/scratch2/farooque/VLQCombination/SingleVLQCombination_2022/newCO/Run2SingleVLQCombination/data/workspaces/SPT_OSML_TS_ZT16K050_MU0_ASIMOV.root     
WORKSPACENAME=combined
DATASETNAME=asimovData_mu0
OUTPUTNAME=output_TS_OSML_mu0.root
quickFit -w ${WORKSPACENAME} -f ${WORKSPACEFILE} -d ${DATASETNAME} -p mu_signal=0 \
-o ${OUTPUTNAME} --savefitresult 1 --hesse 1 --minos 1 2>&1 |tee log_OSML_minos.txt

WORKSPACEFILE=/data/at3/scratch2/farooque/VLQCombination/SingleVLQCombination_2022/newCO/Run2SingleVLQCombination/data/workspaces/TS_WT16K050_combined_MU0_ASIMOV.root
WORKSPACENAME=combWS
DATASETNAME=asimovData_mu0
OUTPUTNAME=output_TS_mu0.root
quickFit -w ${WORKSPACENAME} -f ${WORKSPACEFILE} -d ${DATASETNAME} -p mu_signal=0 \
-o ${OUTPUTNAME} --savefitresult 1 --hesse 1 --minos 1 2>&1 |tee log_TS_minos.txt

