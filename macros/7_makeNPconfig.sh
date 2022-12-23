#!/bin/bash

perl ${VLQCOMBDIR}/macros/make_TRExNPfile.perl log_HTZT_minos.txt SPT_HTZT_TS_M16K050_MU0_ASIMOV.txt
perl ${VLQCOMBDIR}/macros/make_TRExNPfile.perl log_OSML_minos.txt SPT_OSML_TS_M16K050_MU0_ASIMOV.txt
perl ${VLQCOMBDIR}/macros/make_TRExNPfile.perl log_MONOTOP_minos.txt SPT_MONOTOP_TS_M16K050_MU0_ASIMOV.txt
perl ${VLQCOMBDIR}/macros/make_TRExNPfile.perl log_combined_minos.txt TS_WT16K050_combined_MU0_ASIMOV.txt
