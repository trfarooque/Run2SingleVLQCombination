#!/bin/bash

manager -w combine -x ${VLQCOMBDIR}/data/xml/combination/combination.xml 2>&1 |tee log_combine
