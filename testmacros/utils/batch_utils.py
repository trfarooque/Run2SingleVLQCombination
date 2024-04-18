#!/bin/python
import socket
import glob
import os
import sys

sys.path.append( os.getenv("VLQCOMBPATH") + "/utils/" )
from messages import *

class batch_utils:
    ##_________________________________________________________________________
    ##
    def __init__(self):
        self._platform=""
        if socket.gethostname().find("cca")>-1:
            self._platform="lyon"
        elif socket.gethostname().find("pic")>-1:
            self._platform="pic"

    ##__________________________________________________________________________
    ##
    def is_known(self):
        return not len(self._platform)==0

    ##__________________________________________________________________________
    ##
    def submit_scripts(self, output, pattern, queue):
        list_scripts=[]
        if isinstance(pattern, basestring):
            list_scripts=glob.glob(output+"/*"+pattern)
        else:
            list_scripts=pattern
        for script in list_scripts:
            if self._platform=="lyon":
                os.system("qsub -l sps=1 -P P_atlas -o " + output + "/ -e " + output + "/" + script)
            elif self._platform=="pic":
                os.system("qsub -q " + queue + " " + script + " -o " + output + "/ -e " + output+ "/" )

    ##__________________________________________________________________________
    ##
    def check_outputs(self, check_file):
        '''
        Function to dump a list of scripts to resubmit because the outputs are missing
        '''
        output_check = open(check_file,"r")
        list_to_resubmit=[]
        for output in output_check:
            #each line contains the name of the output and the corresponding script
            split_path=output.split(" ")
            if not len(split_path)==2:
                print "Error with file: " + check_file + ". Not the good format."
                continue;

            if not os.path.exists(split_path[0]):
                #the file cannot be found ... add the script to the list for resubmission
                list_to_resubmit += [split_path[1]]
                printWarning("-> Will resubmit job for "+ split_path[1].split("/")[len(split_path[1].split("/"))-1].replace("\n",""))
        if len(list_to_resubmit)==0:
            printGoodNews("=> The checker found all files !")
        return list_to_resubmit