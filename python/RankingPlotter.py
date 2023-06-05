import sys, os
import ROOT
from termcolor import colored

#from CombUtils import VLQCombinationConfig
from optparse import OptionParser

class RankingPlotter:

    def __init__(self, wsPath, wsName, dsName, fitFileName, outputPath, nMerge, includeGamma):
        self.wsPath = wsPath
        self.wsName = wsName
        self.dsName = dsName
        self.fitFileName = fitFileName
        self.outputPath = outputPath
        self.nMerge = nMerge
        self.includeGamma = includeGamma
        self.mu_nominal = {}
        self.NPlist = {}


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

    ##### Write scripts to run fits to calculate impact of each NP ####
    def WriteNPFit(self, nuisParam, prefit, shift_up, scriptName):

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

        resultPath = self.outputPath+'/Results/fit_'+outBaseName+'.root'
        logPath = self.outputPath+'/Logs/log_'+outBaseName+'.txt'

        cmd = '''quickFit -w {} -f {} -d {} -o {} --savefitresult 1 --hesse 1 --minos 1 {} >> {} 2>&1 \n\n'''\
            .format(self.wsName,
                    self.wsPath,
                    self.dsName,
                    resultPath,
                    fitarg,
                    logPath)
        #Make job scripts
        os.makedirs(os.path.dirname(self.outputPath+'/Scripts/'), exist_ok=True)
        os.makedirs(os.path.dirname(self.outputPath+'/Logs/'), exist_ok=True)
        os.makedirs(os.path.dirname(self.outputPath+'/Results/'), exist_ok=True)
        jobScript = open(self.outputPath+'/Scripts/'+scriptName, 'a')
        print(self.outputPath+'/Scripts/'+scriptName) 
        jobScript.write(cmd)

    #### Submit ranking fit scripts to condor ####
    def submit_condor_job(self, scriptName):
        print('Launching job : '+scriptName)

    #### Main code that loops over NP list and makes/launches ranking fit scripts ####
    def LaunchRankingFits(self, do_run=False):

        merge_index = 0
        script_count = 0
        for np_index,np in self.NPlist.items():
            if(merge_index < self.nMerge):
                merge_index += 1
            else:
                merge_index = 0
                script_count += 1

            np_jobScriptName = ('script_ranking_{}.sh').format(script_count)
            self.WriteNPFit(np, prefit=True, shift_up=True, scriptName=np_jobScriptName)
            self.WriteNPFit(np, prefit=True, shift_up=False, scriptName=np_jobScriptName)
            self.WriteNPFit(np, prefit=False, shift_up=True, scriptName=np_jobScriptName)
            self.WriteNPFit(np, prefit=False, shift_up=False, scriptName=np_jobScriptName)

            if(do_run and (merge_index==self.nMerge)):
                self.submit_condor_job(np_jobScriptName)



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
        #os.system("mkdir -p " + self.outputPath+'/Fits/')
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

            



            
