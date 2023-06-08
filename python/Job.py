###
#
# Utility classes to submit jobs on PBS or Condor batch systems
# Original authors: Loic Valery, Mirko Casolino
#
# trisha.farooque@cern.ch
###


#!/bin/python
import time
import os
from utils import *

def prepareTarBall(pathToPackage,pathToTarball):
    current_folder = os.getcwd()
    os.chdir(pathToPackage)
    
    printGoodNews("=> Creating tarball !")
    print( "   -> ", pathToTarball)
    com = "tar czf " + pathToTarball + " * "
    os.system(com)
    printGoodNews("=> Tarball done :-)")
    
    os.chdir(current_folder)
    

##
##
## CLASS JOBSET
##
##
class JobSet:
    ##_________________________________________________________________________
    ##
    def __init__(self,platform):        
        if(platform.find("lxplus")>-1):
            self.platform = "lxplus"
        elif(platform.find("pic")>-1):
            self.platform = "pic"
        elif(platform.find("aglt2")>-1):
            self.platform = "aglt2"
        else:
            printError("<!> In JobSet class constructor ... Unknown platform: " + platform)
            self.platform = "lxplus"
        self.jobs=[]
        self.outDir=""
        self.logDir=""
        self.scriptDir=""
        self.scriptName=""
        self.tarballPath=""
        self.batch="condor"
        self.queue=""
        self.jobRecoveryFileName="JobCheck.chk"
        self.writeSubmissionCommandsToFileOnly=False
        
    ##_________________________________________________________________________
    ##
    def addJob(self,job):
        self.jobs += [job]

    ##_________________________________________________________________________
    ##
    def size(self):
        return len(self.jobs)
        
    ##_________________________________________________________________________
    ##
    def clear(self):
        self.jobs=[]
        self.scriptName=""

    ##_________________________________________________________________________
    ##
    def setBatch(self,batch):
        self.batch=batch

    ##_________________________________________________________________________
    ##
    def setQueue(self,queue):
        self.queue=queue
        
    ##_________________________________________________________________________
    ##
    def setSubmissionCommandsFile(self,submissioncommandsfile):
        self.writeSubmissionCommandsToFileOnly=True
        self.submissioncommandsfile=submissioncommandsfile

    ##_________________________________________________________________________
    ##
    def setOutDir(self,outDir):
        self.outDir=outDir
    
    ##_________________________________________________________________________
    ##
    def setLogDir(self,logDir):
        self.logDir=logDir
    
    ##_________________________________________________________________________
    ##
    def setScriptDir(self,scriptDir):
        self.scriptDir=scriptDir

    ##_________________________________________________________________________
    ##
    def setScriptName(self,name):
        self.scriptName=name

    ##_________________________________________________________________________
    ##
    def setTarBall(self,tarBall):
        self.tarballPath=tarBall
    
    ##_________________________________________________________________________
    ##
    def setJobRecoveryFile(self,name):
        self.jobRecoveryFileName = name

    ##_________________________________________________________________________
    ##
    def Initialize(self,f):
        f.write("#!/bin/bash \n")
        f.write("export ATLAS_LOCAL_ROOT_BASE=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase \n")
        f.write("source ${ATLAS_LOCAL_ROOT_BASE}/user/atlasLocalSetup.sh \n")
        f.write("echo 'Changing to directory' $TMPDIR \n")
        f.write("cd $TMPDIR \n")
        f.write("echo 'In directory' $PWD \n")
        f.write("\n")
        f.write("echo '==> Before copying tarball'\n")
        f.write("ls -lrth\n")
        f.write("\n")
        f.write("cp -r "+self.tarballPath+" CombCode.tgz \n")
        f.write("\n")
        f.write("echo '==> After copying the tarball'\n")
        f.write("ls -lrth\n")
        f.write("\n")
        f.write("tar xf CombCode.tgz \n")
        f.write("echo '==> After extracting the tarball'\n")
        f.write("ls -lrth\n")
        f.write("\n")

        f.write("source setup.sh && make \n")
        f.write("\n")
        f.write("echo '==> After the setup' \n")
        f.write("ls -lrth \n")
        f.write("\n")
        f.write("\n")
        f.write("\n")

        f.write("export OUTDIR='"+self.outDir+"' \n")
        f.write("export LOGDIR='"+self.logDir+"' \n")
        f.write("\n")

    ##_________________________________________________________________________
    ##
    def Running(self,f,job):

        #f.write("export OUTDIR='"+job.outDir+"' \n")
        #f.write("export LOGDIR='"+job.logDir+"' \n")
        #f.write("\n")
        f.write(job.execName + " ")
        f.write(">& "+job.jobName+".log \n")
        f.write("\n")
        f.write("echo '==> After running the code'\n")
        f.write("\n")
        #f.write("mv *.root $OUTDIR \n")
        #f.write("mv *.txt *.log $LOGDIR \n")
        #f.write("\n")
        #f.write("\n")
        f.write("\n")

    ##_________________________________________________________________________
    ##
    def Terminate(self,f):

        f.write("mv *.root $OUTDIR \n")
        f.write("mv *.txt *.log $LOGDIR \n")
        f.write("\n")
        f.write("\n")

        if self.batch == "pbs":
            f.write("rm -rf $TMPDIR/*")
        f.write("\n")

    ##_________________________________________________________________________
    ##
    def writeCondorSubmitScript(self):
        f = open(self.scriptDir+"/"+self.scriptName+".sub","w")
        f.write("#Basic configuration \n")
        f.write("executable              = "+self.scriptDir+"/"+self.scriptName+" \n")
        f.write("output                  = "+self.logDir+self.scriptName+".$(ClusterId).$(ProcId).out \n")
        f.write("error                   = "+self.logDir+self.scriptName+".$(ClusterId).$(ProcId).err \n")
        f.write("log                     = "+self.logDir+self.scriptName+".$(ClusterId).log \n")
        f.write("\n")
        f.write("\n")
        if(self.platform == "aglt2"):
            f.write("#Duration of job \n")
            if(self.queue.upper() == "MEDIUM"):
                f.write("+IsMediumJob = true \n")
            elif(self.queue.upper() == "LONG"):
                f.write("+IsLongJob = true \n")
            else:
                f.write("+IsShortJob = true \n")
            f.write("\n")
            f.write("\n")
        f.write("#Script options \n")
        if(self.platform != "aglt2"):
            f.write("request_memory           = 8 GB \n")
        f.write("nJobs                   = 1 \n")
        f.write("\n")
        f.write("\n")
        #f.write("include command : mkdir "+self.logDir+"/output \n")
        #f.write("include command : mkdir "+self.logDir+"/error \n")
        #f.write("include command : mkdir "+self.logDir+"/log \n")
        f.write("#Queue subjobs \n")
        f.write("queue $(nJobs) \n")
        f.close()


    ##_________________________________________________________________________
    ##
    def writeScript(self):
        if(self.scriptName==""):
            self.scriptName = self.jobs[len(self.jobs)-1].jobName
    
        #Declaration of the output recovery tool
        f_reco_file = 0
        if not self.jobRecoveryFileName == "":
            f_reco_file = open(self.jobRecoveryFileName,"a")

        #Writing the scripts
        current_merged_script_name = self.scriptDir+"/"+self.scriptName
        #f = open(current_merged_script_name,"w+")
        with open(current_merged_script_name,"w+") as f:
            self.Initialize(f)
            for iJob in range(len(self.jobs)):
                temp_job = self.jobs[iJob]
                self.Running(f,temp_job)
            
                #Also write a sub-script to make easier the resubmission of the jobs
                current_sub_script_name = self.scriptDir+"/sub_"+self.scriptName+"_"+temp_job.jobName
                f_sub = open(current_sub_script_name,"w+")
                self.Initialize(f_sub)
                self.Running(f_sub,temp_job)
                self.Terminate(f_sub)
                f_sub.close()
        
                #Write the file to possibly relaunch the missing jobs
                if not self.jobRecoveryFileName == "":
                    for iOption in range(len(temp_job.jobOptions)):
                        if temp_job.jobOptions[iOption][0].upper()=="OUTPUTFILE":
                            if self.batch == "pbs":
                                f_reco_file.write(temp_job.outDir+"/"+temp_job.jobOptions[iOption][1]
                                                  +" "+current_sub_script_name+"\n")
                            else:
                                f_reco_file.write(temp_job.outDir+"/"+temp_job.jobOptions[iOption][1]
                                                  +" "+self.scriptDir+"/"+self.scriptName+".sub \n")
                            break

            self.Terminate(f)
            #f.close()
        f_reco_file.close()
        if self.batch != "pbs":
            self.writeCondorSubmitScript()
        os.chmod(current_merged_script_name, 0o755)

    ##_________________________________________________________________________
    ##
    def submitSet(self):
        if self.batch != "pbs":
            com="condor_submit " + self.scriptDir + "/" + self.scriptName + ".sub"
            time.sleep(2)
            os.system(com)
        else:
            com=""
            if(self.platform == "lxplus"):
                com += "bsub -q "
            elif(self.platform == "pic"):
                com += "qsub -q "
            else:
                printError("The system you are running on is not supported yet ... Please move to lxplus or PIC")
            if(self.queue==""):
                self.queue="at3_short"
            com += self.queue
            com += " " + self.scriptDir+"/"+self.scriptName+" "
            if not(self.logDir==""):
                if(self.platform == "lxplus"):
                    com += " -o "+self.logDir+"/"+self.scriptName+"_batch.log -e "+self.logDir+"/"+self.scriptName+"_batch.log"
                else:
                    com += " -o "+self.logDir+" -e "+self.logDir
            if self.writeSubmissionCommandsToFileOnly:
                self.submissioncommandsfile.write("echo "+self.scriptName+"\n")
                self.submissioncommandsfile.write(com+"\n")
            else:
                os.system(com)


##
##
## CLASS JOB
##
##
class Job:
    """
    Class allowing to deal transparently with all batch systems. The interface
    is done in the class (by the means of the platform variable), and not in 
    the script itself
    """
    ##_________________________________________________________________________
    ##
    def __init__(self,platform):
        if(platform.find("pic")>-1):
            self.platform = "pic"
        elif(platform.find("lxplus")>-1):
            self.platform = "lxplus"
        elif(platform.find("aglt2")>-1):
            self.platform = "aglt2"
        else:
            printError("<!> In Job class constructor ... Unknown platform: " + platform)
            self.platform = "pic"
        self.debug = False
        self.jobOptions=[]
        self.jobName=""
        self.execName=""
        self.outDir=""

    ##_________________________________________________________________________
    ##
    def setDebug(self,debug):
        self.debug = debug

    ##_________________________________________________________________________
    ##
    def addOption(self,option,value):
        self.jobOptions += [[option,value]]

    ##_________________________________________________________________________
    ##
    def setName(self,name):
        self.jobName=name
    
    ##_________________________________________________________________________
    ##
    def setExecutable(self,exe):
        self.execName = exe
    
    ##_________________________________________________________________________
    ##
    def setOutDir(self,outDir):
        self.outDir = outDir
