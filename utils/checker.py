#!/bin/python
import os
import glob
import sys

sys.path.append( os.getenv("VLQCOMBPATH") + "/utils/" )
from messages import *

class checker:
    ##_________________________________________________________________________
    ##
    def __init__(self):
        self._verbose=1

    ##__________________________________________________________________________
    ##
    def exists(self, path):
        return os.path.exists(path)

    ##__________________________________________________________________________
    ##
    def check_naming(self, files, channel, sum_br):
        for f in files:
            status = True
            splitted=f.split("/")
            f_name=splitted[len(splitted)-1]
            f_name_split=f_name.split("_")
            if(len(f_name_split)==4 or len(f_name_split)==7):
                OK=True
                #this is the format of files for the simplified scenarios (singlet, doublet)
                if not f_name_split[0]==channel:
                    OK=False
                if not f_name_split[1] in ["TT","BB"]:
                    OK=False
                if not int(f_name_split[2]) in [500,600,700,750,800,850,900,950,1000,1050,1100,1150,1200,1300,1400,1500]:
                    OK=False

                if len(f_name_split)==4:
                    #This is for singlet and doublet
                    if not f_name_split[3].replace(".root","") in ["Singlet","Doublet"]:
                        OK=False
                else:
                    #This is for variable BRs 
                    if not f_name_split[3]=="BR":
                        OK=False
                    if not abs(float(f_name_split[4])+float(f_name_split[5])+float(f_name_split[6].replace(".root",""))-sum_br)<0.00001:
                        OK=False
                if not OK:
                    print "=> \""+f+"\" is not following the convention !"
                    status=False
            else:
                status = False

            if not status:
                #If there is a problem, print the file name for people to know where the problem is
                print "=> Problem with file: " + f 
                break
        return status

    ##__________________________________________________________________________
    ##
    def naming_ok(self, path, channels, sumBR):
        results=True
        if self.exists(path):
            files=glob.glob(path+"/*.root")
            if(len(files)==0):
                for c in channels:
                    files=glob.glob(path+"/"+c+"/*.root")
                    if(len(files)==0):
                        print "=> No rootfile either in \""+path+"/"+c+"/\" ! Returning false !"
                        return False;
                    else:
                        ok=self.check_naming(files, c, sumBR)
                        if not ok:
                            results=False
            else:
                if( len(channels)==1 ):
                    ok=self.check_naming(files, channels[0], sumBR)
                    if not ok:
                        results=False
                else:
                    results = False
        return results
