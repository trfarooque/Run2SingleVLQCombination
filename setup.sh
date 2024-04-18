#!/bin/bash

setupATLAS -q
#asetup StatAnalysis,0.2.5
asetup StatAnalysis,0.0.4
export VLQCOMBDIR=$PWD
export PATH=$VLQCOMBDIR/bin/:$VLQCOMBDIR/python/:$PATH
export PYTHONPATH=$VLQCOMBDIR/python/:$VLQCOMBDIR/VLQ_Interpretation_Tools/:$PYTHONPATH
pip3 install termcolor
