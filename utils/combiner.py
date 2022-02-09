#!/bin/python
import os
import sys
import glob
import os.path

sys.path.append( os.getenv("VLQCOMBPATH") + "/utils/" )
from messages import *

class combiner:
    ##__________________________________________________________________________
    ##
    def __init__(self, signal, channels, masses, br, inputs, output, data ):
        self._signal=signal
        self._channels=channels
        self._masses=masses
        self._br=br
        self._input=inputs
        self._output=output
        self._data=data
        self._config_name=""
        self._check_file=output+"/OutputChecks.chk"


    ##__________________________________________________________________________
    ##
    def prepare_scripts(self, prefix):
        output_check=open(self._check_file,"w")
        for mass in self._masses:
            for br in self._br:
                script_name=prefix+"_"+mass+"_"+br+".sh"
                script=open(self._output+"/"+script_name,'w')
                script.write("#!/bin/bash \n")
                script.write("export ATLAS_LOCAL_ROOT_BASE=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase \n")
                script.write("source ${ATLAS_LOCAL_ROOT_BASE}/user/atlasLocalSetup.sh \n")
                script.write("cd $TMPDIR \n")
                #Copying the necessary tarballs
                script.write("cp "+ os.getenv("VLQCOMBPATH") +"/workspaceCombiner.tgz . \n")
                script.write("cp "+ os.getenv("VLQCOMBPATH") +"/WorkspaceChecks.tgz . \n")
                #Extracting the tarballs now ... 
                script.write("mkdir workspaceCombiner && tar -xf workspaceCombiner.tgz -C workspaceCombiner \n")
                script.write("mkdir WorkspaceChecks && tar -xf WorkspaceChecks.tgz -C WorkspaceChecks \n")


                #Copying the files locally and creating a list of files so the combined config file can be dumped
                #script.write("cp "+ self._output + "/" + self._config_name + " combination.xml \n")
                script.write("rm -f WorkspaceChecks/listFiles \n")
                for c in self._channels:
                    workspace_file=glob.glob(self._input+"/"+c+"/"+c+"_"+self._signal+"_"+mass+"*"+br+"*.root")
                    #if not len(workspace_file)==1:
                    #    printError("=> ERROR when trying to find the input workspace for "+self._input+"/"+c+"/"+c+"_"+self._signal+"_"+mass+"*"+br+"*.root. Aborting !")
                        #sys.exit()
                    #else:
                    if True:
                        #script.write("cp "+ workspace_file[0] + " " + c +  ".root \n")
                        map_file=""
                        if c in ["ZTMET", "WBX", "WTX" ]:
                            map_file = " : maps/oldCDI.txt"
                        script.write("echo \"" + c + " : ../" + c + ".root " + map_file + " \" >> WorkspaceChecks/listFiles \n")

                #First, sets up ROOT
                script.write("cd workspaceCombiner \n\n")
                script.write("source setup.sh \n")

                #Then dumps the config files for each channel
                script.write("cd ../WorkspaceChecks \n\n")
                script.write("make \n\n\n")
                script.write("cat listFiles \n\n\n")
                script.write("./bin/workspace.exe file_path=listFiles workspace_name=combined data_name=" + self._data +" do_config_dump=true \n")
                script.write("cat output/combination.xml \n\n\n")
                script.write("cp output/combination.xml ../workspaceCombiner/ \n\n\n")

                #Now, let's actually combine ! 
                script.write("cd ../workspaceCombiner \n\n")
                script.write("manager -w combine -x combination.xml -f combined.root -s false -t 5\n")
                name_output_workspace = "Combined"
                for c in self._channels:
                    name_output_workspace += "_"+c
                name_output_workspace += "_"+self._signal
                name_output_workspace += "_"+mass
                name_output_workspace += "_"+br
                name_output_workspace += ".root"
                script.write("mv combined.root " + self._output + "/" + name_output_workspace + " \n")
                output_check.write( self._output + "/" + name_output_workspace + " " + self._output+"/"+script_name + "\n")
                script.write("$PWD \n")
                script.close()
        output_check.close()
