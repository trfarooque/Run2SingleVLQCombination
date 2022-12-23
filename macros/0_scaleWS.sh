#!/bin/bash

manager -w edit -x ${VLQCOMBDIR}/data/xml/scaling/TS_HTZT.xml 2>&1 |tee log.txt
manager -w edit -x ${VLQCOMBDIR}/data/xml/scaling/TS_OSML.xml 2>&1 |tee log.txt
manager -w edit -x ${VLQCOMBDIR}/data/xml/scaling/TS_MONOTOP.xml 2>&1 |tee log.txt
