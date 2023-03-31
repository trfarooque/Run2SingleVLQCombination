#!/bin/bash

baseDir=${VLQCOMBDIR}/data/xml/asimov/
quickAsimov -x ${baseDir}/asimov_HTZT.xml -w combined -m ModelConfig -d asimovData
quickAsimov -x ${baseDir}/asimov_OSML.xml -w combWS -m ModelConfig -d asimovData
quickAsimov -x ${baseDir}/asimov_MONOTOP.xml -w combined -m ModelConfig -d asimovData
quickAsimov -x ${baseDir}/asimov_combined.xml -w combWS -m ModelConfig -d combData
