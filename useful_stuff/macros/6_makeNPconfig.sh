#!/bin/bash


${VLQCOMBDIR}/WorkspaceChecks/bin/workspace.exe \
file_path=${VLQCOMBDIR}/data/fits/wsList.txt data_name="asimovData_mu0" \
input_ws_folder=${VLQCOMBDIR}/data/workspaces/asimov_mu0_workspaces/ \
output_trexf_folder=${VLQCOMBDIR}/data/trexf/ \
output_tag="TS_M16K050" \
do_trexf_dump=TRUE do_checks=FALSE abort_on_error=FALSE
