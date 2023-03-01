#!/bin/python
'''
Python script performing the tasks for the VLQ combination: workspace
combination, asimov building, fits, limit setting, ...
It allows the interactive and the batch use for some clusters. Currently
implemented:
-> PIC (Spain)
-> CCIN2P3 (France)
This implementation is performed in the utils/batch.py class
'''

import argparse
import sys
import os

if(os.getenv("VLQCOMBPATH")==""):
    print "=> Please do `setup.sh` to load the needed environment variables"
    sys.exit()

sys.path.append( os.getenv("VLQCOMBPATH") + "/utils/" )
from batch_utils import *
from checker import *
from messages import *
from combiner import *
from asimov import *
from limits import *
from fits import *

parser = argparse.ArgumentParser(description='Utilities for the VLQ combination effort',
formatter_class=argparse.ArgumentDefaultsHelpFormatter)
#
required = parser.add_argument_group('required arguments')
required.add_argument('-i', '--input_files', action="store", required=True,
help="absolute path to the folder containing the input files")
#
required.add_argument('-a', '--action', action="store", required=True,
help="which action to perform [check_naming,combine_ws,make_asimov,limits,fits]")
#
required.add_argument('-c', '--channels', action="store", required=True,
help="coma-separated list of channels to consider")
#
required.add_argument('-o', '--output_folder', action="store", required=True,
help="sbsolute path to store the outputs of the jobs")
#
# optional arguments
#
parser.add_argument('-m', '--masses', action="store",
help="coma-separated list of masses to consider",
default="700,750,800,850,900,950,1000,1050,1100,1200,1300,1400"
)
parser.add_argument('-B', '--br', action="store",
help="coma-separated list of branching ratios to consider [Singlet, Doublet, all]",
default="Singlet"
)
parser.add_argument('-d', '--data', action="store",
help="list of the RooDataset to consider in the workspace",
default="asimovData"
)
parser.add_argument('-q', '--queue', action="store",
help="name of the batch queue",
default="at3_short"
)
parser.add_argument('-A', '--asimov', action="store",
help="name of the Asimov dataset to be created (only used if action=make_asimov)",
default="combo_Asimov"
)
parser.add_argument('-n', '--np_values', action="store",
help="values of the nuisance parameters in the fomat np1_name:np1_value,np2_name:np2_value (only used if action=make_asimov)",
default=""
)
parser.add_argument('-w', '--ws_name', action="store",
help="name of the workspace to consider",
default="combWS"
)
parser.add_argument('-C', '--check_outputs', action="store_true",
help="check if outputs have been produced and relaunch jobs if not",
default=False
)
parser.add_argument('-S', '--sumBR', action="store",
help="sum of the branching ratio",
default=1.0
)
parser.add_argument('-s', '--signal', action="store",
help="type of signal to consider TT/BB",
default="TT"
)

#
# Checking if the current system is known
#
_checker = checker()
_batch = batch_utils()

#
# parsing options
#
args = parser.parse_args()
#
# required arguments
#
input_files=args.input_files
if not _checker.exists( input_files ):
    printError("=> ERROR: the path \""+input_files+"\" does not exist")
    #sys.exit(-1)
action=args.action.upper()
if not action in ["CHECK_NAMING","COMBINE_WS","MAKE_ASIMOV","LIMITS","FITS"]:
    printError("=> ERROR: the action is not recognized: " + action)
    sys.exit(-1)
channels=args.channels.split(",")
if not sum( (c in ["WBX","HTX","ZTMET","ZTML","SSL","ALLH","WTX"]) for c in channels)==len(channels):
    printError("=> ERROR: some channels are not recognized.")
    sys.exit(-1)
output_folder=args.output_folder
if not _checker.exists( output_folder ):
    printWarning("=> WARNING: the output folder does not exist yet. Creating it.")
    os.system("mkdir -p "+output_folder)
    if not _checker.exists( output_folder ):
        printError("=> ERROR: the output folder could not be created. Aborting.")
        sys.exit(-1)
    else:
        printGoodNews("=> Created !")

#
# optional arguments
#
masses=args.masses.split(",")
br=args.br.split(",")
data=args.data
queue=args.queue
asimov_data_name=args.asimov
np_values=args.np_values
workspace_name=args.ws_name
check_outputs=args.check_outputs
sum_br=float(args.sumBR)
signal=args.signal

#
# Checking the naming convention of the files
#
if action=="CHECK_NAMING":
    if not _checker.naming_ok( input_files, channels, sum_br ):
        printError("=> Problem ! The naming convention is not respected")
        sys.exit()
    else:
        printGoodNews("=> Naming convention looks OK")

#
# Launching the workspace combination on the batch
#
if action=="COMBINE_WS":
    '''
    Actions needed for the workspace combination:
    1)-> Create the combined configuration file containing the workspace description
       and replace the template entries #channel_name# and #DATA# to adapt to the
       situation
    2)-> Find the individual workspaces
    3)-> Prepare the script to submit on the batch
    4)-> Submit the job
    '''
    if not _batch.is_known():
        print "=> Problem ! Your system is not supported to send batch jobs. Exiting !"
        sys.exit()
    _combiner = combiner( signal, channels, masses, br, input_files, output_folder, data )
    if not check_outputs:
        #_combiner.prepare_config() #prepare the combination.xml file needed by workspaceCombiner
        _combiner.prepare_scripts("script_Comb") #prepare the scripts to launch on the batch
        #_batch.submit_scripts( output_folder, "script_Comb*.sh", queue)
    #else:
        #_batch.submit_scripts(output_folder, _batch.check_outputs(_combiner._check_file), queue)

#
# Launching the workspace combination on the batch
#
if action=="MAKE_ASIMOV":
    '''
    Actions needed for the Asimov creation
    1)-> Point to the workspace files to modify in order to add the Asimov
    2)-> Write the script that will be executed on batch
    3)-> Submit the scripts
    '''
    if not _batch.is_known():
        print "=> Problem ! Your system is not supported to send batch jobs. Exiting !"
        #sys.exit()
    _asimov = asimov( input_files, output_folder, asimov_data_name, np_values)
    if not check_outputs:
        _asimov.prepare_scripts("script_Asimov"+asimov_data_name, workspace_name)#prepare the scripts to launch on the batch
        #_batch.submit_scripts( output_folder, "script_Asimov*.sh", queue)
    #else:
        #_batch.submit_scripts(output_folder, _batch.check_outputs(_asimov._check_file), queue)

#
# Launch the limit computation on batch
#
if action=="LIMITS":
    '''
    Actions needed for the limits
    1)-> Point to the workspace files to use in the inputs
    2)-> Write the script that will be executed on batch
    3)-> Submit the scripts
    '''
    if not _batch.is_known():
        print "=> Problem ! Your system is not supported to send batch jobs. Exiting !"
        sys.exit()
    _limit = limits( signal, masses, br, input_files, output_folder, data )
    if not check_outputs:
        _limit.prepare_scripts("script_Limits", workspace_name)#prepare the scripts to launch on the batch
        _batch.submit_scripts( output_folder, "script_Limits*.sh", queue)
    else:
        _batch.submit_scripts(output_folder, _batch.check_outputs(_limit._check_file), queue)


#
# Launch the fit computation on batch
#
if action=="FITS":
    '''
    Actions needed for the limits
    1)-> Point to the workspace files to use in the inputs
    2)-> Write the script that will be executed on batch
    3)-> Submit the scripts
    '''
    if not _batch.is_known():
        print "=> Problem ! Your system is not supported to send batch jobs. Exiting !"
        sys.exit()
    _fits = fits( signal, masses, br, input_files, output_folder, data )
    if not check_outputs:
        _fits.prepare_scripts("script_Fits", workspace_name)#prepare the scripts to launch on the batch
        _batch.submit_scripts( output_folder, "script_Fits*.sh", queue)
    else:
        _batch.submit_scripts(output_folder, _batch.check_outputs(_fits._check_file), queue)








