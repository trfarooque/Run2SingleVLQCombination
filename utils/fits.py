#!/bin/python
import os
import glob
import sys

sys.path.append( os.getenv("VLQCOMBPATH") + "/utils/" )
from messages import *

class fits:
    ##__________________________________________________________________________
    ##
    def __init__(self, signal, masses, br, inputs, output, data ):
        self._signal=signal
        self._masses=masses
        self._br=br
        self._input=inputs
        self._output=output
        self._data=data
        self._check_file=output+"/OutputChecks.chk"

    ##__________________________________________________________________________
    ##
    def prepare_scripts(self, prefix, workspace_name):
        output_check=open(self._check_file,"w")
        for mass in self._masses:
            for br in self._br:
                list_files = glob.glob( self._input + "/*"+self._signal+"*"+mass+"*"+br+".root" )
                if not len(list_files)==1:
                    printError("=> ERROR: not find a single file matching: " + self._input + "/*"+self._signal+"*"+mass+"*"+br+".root")
                    continue
                f = list_files[0]
                f_splitted = f.split("/")
                f_name = f_splitted[len(f_splitted)-1]
                script_name=prefix+"_"+f_name+".sh"
                script=open(self._output+"/"+script_name,'w')
                script.write("#!/bin/bash \n")
                script.write("export ATLAS_LOCAL_ROOT_BASE=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase \n")
                script.write("source ${ATLAS_LOCAL_ROOT_BASE}/user/atlasLocalSetup.sh \n")
                script.write("cd $TMPDIR \n")
                script.write("cp "+ os.getenv("VLQCOMBPATH") +"/StatTools.tgz . \n")
                script.write("tar -xf StatTools.tgz \n")

                #Copying the files locally
                script.write("cp "+ f +" . \n")
                script.write("source setup.sh \n")
                script.write("\n\n\n")

                command = "./bin/fit.exe file_path="+f_name+" workspace_name="
                command += workspace_name+" data_name="+self._data
                command += " output_folder=Fit_"+ f_name.replace(".root","") +" \n"
                script.write(command)

                script.write("mv Fit_"+ f_name.replace(".root","") +" " + self._output + "/ \n")
                output_check.write(self._output + "/Fit_"+ f_name.replace(".root","") + "/FitResult.root "+self._output+"/"+script_name+"\n")
                
                script.write("rm -rf $TMPDIR/* \n")
                script.close()
