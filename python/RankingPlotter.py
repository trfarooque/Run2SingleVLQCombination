import utils
import sys, os
import socket
import datetime
from optparse import OptionParser

import ROOT
import Job
from termcolor import colored

## Defines some useful variables
platform = socket.gethostname()
now = datetime.datetime.now().strftime("%Y_%m_%d_%H%M")
sleep = 1

class RankingPlotter:

    def __init__(self, wsPath, wsName, dsName, fitFileName, outputPath, nMerge, includeGamma, 
                 batch='condor', batch_queue='at3_short', dry_run=False, debug=False):
        self.wsPath = wsPath
        self.wsName = wsName
        self.dsName = dsName
        self.fitFileName = fitFileName
        self.outputPath = outputPath
        self.nMerge = nMerge
        self.includeGamma = includeGamma
        self.mu_nominal = {}
        self.NPlist = {}
        self.batch = batch
        self.batch_queue = batch_queue
        self.dry_run = dry_run
        self.debug = debug


    #************************ Making fit jobs for ranking plot ***********************    

    ##### Main code that extracts list of NPs and their pulls/constraints from SPLUSB fit file ####
    def ReadFitResultTextFile(self):
        fitFile = open(self.fitFileName, 'r')

        np_index = 0
        for line in fitFile:
            if( "NUISANCE_PARAMETERS" in line ):
                continue
            elif( ("CORRELATION_MATRIX" in line) or ("NLL" in line) ):
                break
            elif( not(self.includeGamma) and ("gamma_" in line) ):
                continue
            elif("mu_signal" in line):
                self.mu_nominal = {'name': linedata[0], 'central': float(linedata[1]), \
                                   'up': float(linedata[2]), 'down': float(linedata[3])}
                print("Read mu_nominal, central:{:g}".format(self.mu_nominal['central']))
            else:
                linedata = line.split()
                if(len(linedata) != 4):
                    print("WARNING: Unexpected format of line: "+line+"\n")
                    print("Skipping")
                else:
                    np_name = linedata[0]
                    np_cntrl = float(linedata[1])
                    np_neg = float(linedata[2])
                    np_pos = float(linedata[3])

                    nuispar = { 'name': np_name, 'central': np_cntrl, 'up': np_pos, 'down': np_neg }
                    self.NPlist[np_index] = nuispar 
                    np_index += 1

    ##### Return command to run fits to calculate impact of each NP ####
    def WriteNPFit(self, nuisParam, prefit, shift_up): #, scriptName):

        npval = 0
        config = 'pre' if(prefit) else 'post'
        config += 'UP' if(shift_up) else 'DOWN'

        if(prefit):
            if(shift_up):
                npval = 1
            else:
                npval = -1
        else:
            if(shift_up):
                npval = nuisParam['central'] + nuisParam['up']
            else:
                npval = nuisParam['central'] + nuisParam['down']

        fitarg = "-p mu_signal,{}={:.6f}".format(nuisParam['name'],npval)

        outBaseName = 'NPRanking_'+nuisParam['name']+'_'+config

        resultFile = 'fit_'+outBaseName+'.root'
        #logPath = self.outputPath+'/Logs/log_'+outBaseName+'.txt'

        ## SKIPPING ALREADY PROCESSED FILES
        #if(os.path.exists(resultPath)):
        #    printWarning("=> Already processed: skipping")
        #    return ""

        #cmd = '''quickFit -w {} -f {} -d {} -o {} --savefitresult 1 --hesse 1 --minos 1 {} >> {} 2>&1 \n\n'''\
        cmd = '''quickFit -w {} -f {} -d {} -o {} --savefitresult 1 --hesse 1 --minos 1 {}'''\
            .format(self.wsName,
                    self.wsPath,
                    self.dsName,
                    resultFile,
                    fitarg)
                    #logPath)

        return cmd

    #### Main code that loops over NP list and makes/launches ranking fit scripts ####
    def LaunchRankingFits(self, do_run=False):

        #Tar the code directory to send to batch
        codePath = os.getenv('VLQCOMBDIR')
        tarballPath = self.outputPath+'/CombCode.tgz'
        Job.prepareTarBall(codePath, tarballPath)


        os.makedirs(os.path.dirname(self.outputPath+'/Scripts/'), exist_ok=True)
        os.makedirs(os.path.dirname(self.outputPath+'/Logs/'), exist_ok=True)
        os.makedirs(os.path.dirname(self.outputPath+'/Results/'), exist_ok=True)

        JOSet = Job.JobSet(platform)
        JOSet.setBatch(self.batch)
        JOSet.setQueue(self.batch_queue)
        JOSet.setScriptDir(self.outputPath+'/Scripts/')
        JOSet.setLogDir(self.outputPath+'/Logs/')
        JOSet.setOutDir(self.outputPath+'/Results/')
        JOSet.setTarBall(tarballPath)#tarball sent to batch (contains all executables)
        JOSet.setJobRecoveryFile(self.outputPath+'/Scripts/'+"/JobCheck.chk")

        script_count = 0
        for np_index,np in self.NPlist.items():
            if script_count > 5:
                break
            for _up in [True, False]:
                for _pre in [True, False]:

                    jOName = np['name']
                    jOName += 'pre' if(_pre) else 'post'
                    jOName += 'UP' if(_up) else 'DOWN'

                    ## Declare the Job object (one job = one code running once)
                    jO = Job.Job(platform)
                    ## Name of the executable to run
                    str_exec = self.WriteNPFit(np, prefit=_pre, shift_up=_up)
                    if(not str_exec):
                        continue
                    jO.setExecutable(str_exec)
                    jO.setDebug(self.debug)
                    jO.setName(jOName)

                    JOSet.addJob(jO)        
                    #Write a script and submit it if there are nMerge jobs in the set, or there are residual jobs remaining
                    if ( (JOSet.size()==self.nMerge) or ((np_index == len(self.NPlist)) and (JOSet.size()>0) ) ):
                        JOSet.setScriptName( 'script_ranking_{}.sh'.format(script_count) )
                        JOSet.writeScript()
                        if not self.dry_run:
                            JOSet.submitSet()
                        JOSet.clear()
                        script_count += 1

        os.system("sleep {:d}".format(sleep))

        

    #************************ Reading results of ranking fits ***********************    

    #### Read signal strength from a given fit log file ####
    def ReadMuFromResultRootFile(self, resultFileBase, prefit, shift_up):

        mu_fit = {}

        config = 'pre' if(prefit) else 'post'
        config += 'UP' if(shift_up) else 'DOWN'

        fname = resultFileBase+'_'+config+'.root'
        if( os.path.isfile(fname) ):

            fitFile = ROOT.TFile(fname)
            fitResult = fitFile.Get("fitResult")
            if not fitResult:
                sys.exit("ERROR: No fitResult found in ROOT file : "+fname)

            valV = fitResult.floatParsFinal().find("mu_signal").getValV()
            err_high = fitResult.floatParsFinal().find("mu_signal").getErrorHi()
            err_low = fitResult.floatParsFinal().find("mu_signal").getErrorLo()
            mu_fit = {'name': 'mu_signal_'+config, 'central':valV, 'up':err_high, 'down':err_low }
            print("Read mu_signal from {} :\n {:g}".format(fname, mu_fit['central']))

        return mu_fit

    #### Read signal strength from a given fit log file ####
    def ReadMuFromLogFile(self, logFileBase, prefit, shift_up):

        config = 'pre' if(prefit) else 'post'
        config += 'UP' if(shift_up) else 'DOWN'

        fname = logFileBase+'_'+config+'.txt'
        fitFile = open(fname, 'r')
        mu_fit = {}
        for line in fitFile:
            if("mu_signal" in line): #this will not work
                central = line[line.index('=')+1:line.index('+/-')].strip(' ')
                err = line[line.index('+/-')+1:].strip(' ')
                mu_fit = {'name': 'mu_signal_'+config, 'central': float(central), \
                                   'up': float(err), 'down': -1.*float(err)}
                break
        if not(mu_fit):
            print('ERROR: No mu_signal found inside file'+fileName)
            abort()

        return mu_fit

    ### Read individual signal strengths and create TRexFitter-style ranking file that can be used for plotting ###
    def WriteTRexFRankingFile(self):

        #open ranking file:
        os.makedirs(os.path.dirname(self.outputPath+'/Fits/'), exist_ok=True)
        outputPath = self.outputPath+'/Fits/NPRanking.txt'

        #open the fit files for each fixed NP configuration
        with open(outputPath,'w') as outFile:
            for np_index,np in self.NPlist.items():

                #basePath = self.outputPath+'/Logs/log_NPRanking_'+nuisParam['name']
                #mu_preUP = ReadMuFromLogFile(basePath,True,True)
                #mu_preDOWN = ReadMuFromLogFile(basePath,True,False)
                #mu_postUP = ReadMuFromLogFile(basePath,False,True)
                #mu_postDOWN = ReadMuFromLogFile(basePath,False,False)

                basePath = self.outputPath+'/Results/fit_NPRanking_'+np['name']
                mu_preUP = self.ReadMuFromResultRootFile(basePath,True,True)
                mu_preDOWN = self.ReadMuFromResultRootFile(basePath,True,False)
                mu_postUP = self.ReadMuFromResultRootFile(basePath,False,True)
                mu_postDOWN = self.ReadMuFromResultRootFile(basePath,False,False)

                if(not (mu_preUP or mu_preDOWN or mu_postUP or mu_postDOWN) ):
                    continue
                dmu_preUP = mu_preUP['central'] - self.mu_nominal['central']
                dmu_preDOWN = mu_preDOWN['central'] - self.mu_nominal['central']
                dmu_postUP = mu_postUP['central'] - self.mu_nominal['central']
                dmu_postDOWN = mu_postDOWN['central'] - self.mu_nominal['central']

                outLine = "{}   {:.6f} {:.6f} {:.6f}  {:.6f}   {:.6f}  {:.6f}   {:.6f} \n"\
                    .format(np['name'],np['central'],np['up'],np['down'],
                            dmu_preUP,dmu_preDOWN,dmu_postUP,dmu_postDOWN)
                outFile.write(outLine)
        outFile.close()

            



            
