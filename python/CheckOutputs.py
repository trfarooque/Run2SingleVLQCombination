import os
import os.path
import string
import random
import re
import time, getpass
import socket
import sys
import datetime
from ROOT import *
from utils import *

##______________________________________________________
##
def submitFailedJobs( expectedRootFile, scriptFile ):
    if scriptFile in submitted_joblist:
        print("Script has been submitted already! Moving on!")
        return False

    else:
        submitted_joblist.append(scriptFile)
    if batchSystem == "condor":
        com = "condor_submit " + scriptFile
        os.system(com)
        time.sleep(2)
        return True
    else:
        platform = socket.gethostname()
        com = ""
        if platform.find("pic")>-1:#we work at PIC
            com += "qsub "
        elif platform.find("lxplus")>-1:#we work at lxbatch
            com += "bsub "
        com += "-q " + batchQueue + " " + scriptFile

        place_to_store_the_logfiles = ""
        for splitted in expectedRootFile.split("/"):
            if splitted.find(".root")==-1:
                place_to_store_the_logfiles += splitted + "/"


        if not(os.path.isfile(scriptFile)):
            printWarning("WARNING: Cannot resubmit job since the script is missing ! ")
            print( "    -> ", scriptFile)
            return False
        else:
            os.system(com)
            time.sleep(2)
            return True

##------------------------------------------------------
## Check there is enough arguments
##------------------------------------------------------
if(len(sys.argv)<2):
    printWarning("Output checker ==> Wrong input arguments")
    print("    python "+sys.argv[0]+" input=<name of .chk file> [opt]")
    print("with as options:")
    print("    relaunch=TRUE/FALSE")
    print("        -> if some outputs are missing/corrupted, relaunch the corresponding jobs")
    print("    batch=<name of the batch system>")
    print("        -> name of the batch system on which to submit the resubmitted jobs (condor/pbs)")
    print("    queue=<name of the batch queue>")
    print("        -> name of the batch queue on which to submit the resubmitted jobs")
    print("")
    sys.exit()

##------------------------------------------------------
## Selects the arguments
##------------------------------------------------------
inputFile=""
relaunchJobs=False
batchSystem="condor"
batchQueue="at3_short"
for iArg in range(1,len(sys.argv)):
    splitted=sys.argv[iArg].split("=")
    if(splitted[0]=="input"): inputFile = splitted[1]
    elif(splitted[0]=="relaunch"):
        if(splitted[1].upper()=="TRUE"): relaunchJobs= True
    elif(splitted[0]=="batch"): batchSystem = splitted[1]
    elif(splitted[0]=="queue"): batchQueue = splitted[1]
if(inputFile==""):
    printError("<!> Please provide an input file to check !")
    sys.exit()

##------------------------------------------------------
## Opens the input file
##------------------------------------------------------
f = open(inputFile,'r')
fNew = open(inputFile+".new",'w')

nMissing = 0
nZombie = 0
nIncomplete = 0
nGood = 0
nRelaunchedJobs = 0
nFilesChecked = 0
submitted_joblist = []
for line in f:
    nFilesChecked += 1
    
    if(nFilesChecked%100==1):
        print("==> {:d} files checked".format(nFilesChecked))
    
    line_splitted = line.replace("\n","").split(" ")
    fileToCheck = line_splitted[0]
    scriptFile = line_splitted[1]

    hasProblems = False
    if not(os.path.isfile(fileToCheck)):
        printError("ABSENT: "+fileToCheck)
        nMissing += 1
        hasProblems = True
    else:
        rootFile = TFile(fileToCheck,'r')
        if rootFile.IsZombie():
            printError("ZOMBIE: "+fileToCheck)
            nZombie += 1
            hasProblems = True
        else:
            _LL = [x.GetName() for x in rootFile.GetListOfKeys()]
            if "nllscan" not in _LL or "fitResult" not in _LL:
                printError("INCOMPLETE: "+fileToCheck)
                nIncomplete += 1
                hasProblems = True
            else:
                t = rootFile.Get('nllscan')
                t.GetEntry(0)
                if t.status != 0:
                    printWarning("CONVERGENCE FAILED: "+fileToCheck)
                    # nIncomplete += 1
                    # hasProblems = True
                del t
        rootFile.Close()

    if hasProblems:
        fNew.write(fileToCheck+" "+scriptFile+"\n")
        if relaunchJobs:
            if submitFailedJobs(fileToCheck, scriptFile):
                nRelaunchedJobs += 1
    else:
        nGood += 1

f.close()
fNew.close()

##------------------------------------------------------
## Writting a summary for the user
##------------------------------------------------------
print("=============================")
print("SUMMARY")
print("=============================")
print("Analysed files: {:d}".format(nFilesChecked))
print("Good files: {:d}".format(nGood))
print("Absent files: {:d}".format(nMissing))
print("Corrupted files: {:d}".format(nZombie))
print("Incomplete files: {:d}".format(nIncomplete))
if relaunchJobs:
    print("Relaunched jobs: {:d}".format(nRelaunchedJobs))
print("=============================")
