#!/bin/python
import os
import glob

class asimov:
    ##__________________________________________________________________________
    ##
    def __init__(self, inputs, output, data_name, np_values ):
        self._input=inputs
        self._output=output
        self._data_name=data_name
        self._np_values=np_values
        self._check_file=output+"/OutputChecks.chk"

    ##__________________________________________________________________________
    ##
    def prepare_scripts(self, prefix, workspace_name):
        output_check=open(self._check_file,"w")
        list_files = glob.glob( self._input + "/*.root" )
        for f in list_files:
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
            script.write("$PWD \n\n\n")
            script.write("ls \n\n\n")
            command = "./bin/create_asimov.exe file_path="+ f_name +" workspace_name="+ workspace_name +" asimov_name="+self._data_name
            if( self._np_values ):
                command += " np_values="+ self._np_values
            command += " poi_value=0 debug=false \n"
            script.write(command)

            script.write("mv "+ f_name.replace(".root","_ASIMOV.root") +" " + self._output + "/"+ f_name +" \n")
            output_check.write( self._output + "/"+ f_name + " " + self._output+"/"+script_name + "\n")
            script.write("rm -rf $TMPDIR \n")
            script.close()
        output_check.close()
