#!/bin/bash


${VLQCOMBDIR}/WorkspaceChecks/bin/workspace.exe \
file_path=${VLQCOMBDIR}/data/xml/combination/wsList.txt data_name="asimovData" \
output_xml_folder=${VLQCOMBDIR}/data/xml/combination/ \
output_ws_folder=${VLQCOMBDIR}/data/workspaces/combined_workspaces/ \
output_ws_name=TS_M16K050_combined.root \
do_config_dump=TRUE do_checks=FALSE abort_on_error=FALSE
