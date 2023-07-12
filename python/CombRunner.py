#!/bin/python3

import sys, os
sys.path.append(os.getenv("VLQCOMBDIR") + "/VLQ_Interpretation_Tools")

from VLQCouplingCalculator import VLQCouplingCalculator as vlq
from VLQCrossSectionCalculator import *
from termcolor import colored
from CombUtils import *
from RankingPlotter import *
from itertools import *
import time
from optparse import OptionParser


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("--data-loc", 
                      dest="dataloc",
                      help='location of data',
                      default='data')
    parser.add_option("--inws-subdir", 
                      dest="inwssubdir",
                      help='location of input ws sub-directories',
                      default='workspaces/input_workspaces')
    parser.add_option("--scaledws-subdir", 
                      dest="scaledwssubdir",
                      help='location of scaled ws sub-directories',
                      default='workspaces/scaled_workspaces')
    parser.add_option("--scalingconfig-subdir", 
                      dest="scalingconfigsubdir",
                      help='location of scaling config sub-directories',
                      default='xml/scaling')
    parser.add_option("--asimovws-subdir", 
                      dest="asimovwssubdir",
                      help='location of asimov ws sub-directories',
                      default='workspaces/asimov_workspaces')
    parser.add_option("--asimovconfig-subdir", 
                      dest="asimovconfigsubdir",
                      help='location of asimov config sub-directories',
                      default='xml/asimov')
    parser.add_option("--combinedws-subdir", 
                      dest="combinedwssubdir",
                      help='location of combined ws sub-directories',
                      default='workspaces/combined_workspaces')
    parser.add_option("--combconfig-subdir", 
                      dest="combconfigsubdir",
                      help='location of combination config sub-directories',
                      default='xml/combination')
    parser.add_option("--fittedws-subdir", 
                      dest="fittedwssubdir",
                      help='location of fitted ws sub-directories',
                      default='workspaces/fitted_workspaces')
    parser.add_option("--limit-subdir", 
                      dest="limitsubdir",
                      help='location of limit sub-directories',
                      default='limits')
    parser.add_option("--log-subdir", 
                      dest="logsubdir",
                      help='location of log sub-directories',
                      default='logs')
    parser.add_option("--ranking-subdir", 
                      dest="rankingsubdir",
                      help='location of ranking fit output sub-directories',
                      default='ranking')
    parser.add_option("--masses", 
                      dest="masses",
                      help='Provide a comma separated list of masses with GeV units (e.g. 1200,1600)',
                      default='1600')
    parser.add_option("--kappas", dest="kappas",
                      help='Provide a comma separated list of kappas (e.g. 0.3,0.5)',
                      default='0.5')
    parser.add_option("--brws", dest="brws",
                      help='Provide a comma separated list of T > Wb BRs (e.g. 0.0,0.5)',
                      default='0.5')
    parser.add_option("--mu", dest="mu",
                      help='Choice of mu for asimov dataset',
                      default='0.0')
    parser.add_option("--use-defScaling", 
                      dest="usedefscale",
                      help='set if the mu is to set the signal scale factor to correspond to the theory XS. If set, the mu value will be overwritten',
                      action='store_true',
                      default=False)
    parser.add_option("--fit-type", 
                      dest="fittype",
                      help='Provide the fit type: BONLY or SPLUSB',
                      default='BONLY')
    parser.add_option("--ranking-nmerge", 
                      dest="ranking_nmerge",
                      help='Number of jobs to merge together when running ranking fits ',
                      default='10')
    parser.add_option("--batch-system",
                      dest="batchsystem",
                      help='Type of batch system (pbs,condor,...) to which jobs should be sent. The default option will be chosen based on the running platform.',
                      default='')
    parser.add_option("--batch-queue",
                      dest="batchqueue",
                      help='Name of batch queue/flavour (short,long,...) to which jobs should be sent. The default option will be chosen based on the running platform.',
                      default='')
    parser.add_option("--use-data", 
                      dest="usedata",
                      help='set if real data is to be used, otherwise asimov will be used',
                      action='store_true',
                      default=False)
    parser.add_option("--skip-scaling", 
                      dest="doscaling",
                      help='set if scaling input workspaces is to be skipped (i.e. already done)',
                      action='store_false',
                      default=True)
    parser.add_option("--skip-asimov", 
                      dest="doasimov",
                      help='set if real data is to be used instead of asimov',
                      action='store_false',
                      default=True)
    parser.add_option("--skip-combine", 
                      dest="docombine",
                      help='set if combination of workspaces is not required',
                      action='store_false',
                      default=True)
    parser.add_option("--skip-separate-fitting", 
                      dest="dosepfit",
                      help='set if independent fitting of workspaces is not required',
                      action='store_false',
                      default=True)
    parser.add_option("--skip-combined-fitting", 
                      dest="docombfit",
                      help='set if fitting of combined workspaces is not required',
                      action='store_false',
                      default=True)
    parser.add_option("--skip-separate-limits", 
                      dest="doseplims",
                      help='set if independent limits are not required',
                      action='store_false',
                      default=True)
    parser.add_option("--skip-combined-limits", 
                      dest="docomblims",
                      help='set if combined limits not required',
                      action='store_false',
                      default=True)
    parser.add_option("--do-separate-ranking-fits", 
                      dest="doseparaterankingfits",
                      help='set if you want to run ranking plot fits for individual workspaces',
                      action='store_true',
                      default=False)
    parser.add_option("--do-combined-ranking-fits", 
                      dest="docombinedrankingfits",
                      help='set if you want to run ranking plot fits for combined workspaces',
                      action='store_true',
                      default=False)
    parser.add_option("--overwrite-ranking-jobs", 
                      dest="overwriteranking",
                      help='set if you want to overwrite preexisting ranking jobs',
                      action='store_true',
                      default=False)
    parser.add_option("--ranking-includeGammas", 
                      dest="ranking_includeGammas",
                      help='Include gamma parameters in ranking fits',
                      default=False)
    parser.add_option("--skip-trexf-configs", 
                      dest="dotrexfcfgs",
                      help='set if TRExFitter Configs are not required',
                      action='store_false',
                      default=True)
    parser.add_option("--skip-trexf-comp", 
                      dest="dotrexfcomp",
                      help='set if TRExFitter Comps are not required',
                      action='store_false',
                      default=True)
    parser.add_option("--do-separate-ranking-plots", 
                      dest="doseparaterankingplots",
                      help='set if you want to make ranking plots for individual workspaces. NOTE: Ranking fits must have already been run',
                      action='store_true',
                      default=False)
    parser.add_option("--do-combined-ranking-plots", 
                      dest="docombinedrankingplots",
                      help='set if you want to make ranking plots for combined workspaces. NOTE: Ranking fits must have already been run',
                      action='store_true',
                      default=False)
    parser.add_option("--dry-run", 
                      dest="dryrun",
                      help='set if you want to write commands to scripts without executing them',
                      action='store_true',
                      default=False)
    parser.add_option("--debug", 
                      dest="debug",
                      help='set for debug messages',
                      action='store_true',
                      default=False)


    (options, args) = parser.parse_args()

    do_Scaling = bool(options.doscaling)
    do_Asimov = bool(options.doasimov)
    do_Combine = bool(options.docombine)
    do_Separate_Fitting = bool(options.dosepfit)
    do_Combined_Fitting = bool(options.docombfit)
    do_Separate_Limits =  bool(options.doseplims)
    do_Combined_Limits =  bool(options.docomblims)
    do_Separate_Ranking_Fits = bool(options.doseparaterankingfits)
    do_Combined_Ranking_Fits = bool(options.docombinedrankingfits)
    do_Overwrite_ranking = bool(options.overwriteranking)
    do_TRExFComp =  bool(options.dotrexfcomp) 
    do_TRExFConfigs = True if do_TRExFComp else bool(options.dotrexfcfgs) # This flag is overwritten when comparison plots are required
    do_Separate_Ranking_Plots = bool(options.doseparaterankingplots)
    do_Combined_Ranking_Plots = bool(options.docombinedrankingplots)
    use_data = False if do_Asimov else bool(options.usedata) # This flag is overwritten when asimov workspaces are required
    ranking_includeGammas = bool(options.ranking_includeGammas)
    do_dry_run = bool(options.dryrun)
    debug_level = bool(options.debug)
    use_defScaling = bool(options.usedefscale)

    DataLoc = str(options.dataloc)
    fittype = str(options.fittype)
    pathdict = {'InWSSubDir' : str(options.inwssubdir),
                'ScaledWSSubDir' : str(options.scaledwssubdir),
                'ScalingConfigSubDir' : str(options.scalingconfigsubdir),
                'AsimovWSSubDir' : str(options.asimovwssubdir),
                'AsimovConfigSubDir' : str(options.asimovconfigsubdir),
                'CombinedWSSubDir' : str(options.combinedwssubdir),
                'CombinationConfigSubDir' :str(options.combconfigsubdir),
                'FittedWSSubDir' : str(options.fittedwssubdir),
                'LimitSubDir' : str(options.limitsubdir),
                'LogSubDir' : str(options.logsubdir),
                'RankingSubDir' : str(options.rankingsubdir)
                }

    mu = float(options.mu)
    masses = list(map(float, str(options.masses).split(',')))
    kappas = list(map(float, str(options.kappas).split(',')))
    BRWs = list(map(float, str(options.brws).split(',')))
    ranking_nmerge = int(options.ranking_nmerge)
    InDataName = 'asimovData' if not use_data else "obsData"
    datatag = 'data' if use_data else 'asimov_mu{}'.format(int(mu*100))

    if fittype not in ['BONLY', 'SPLUSB']:
        print(colored("Unrecognized Fit Type (--fit-type) option. Reverting to BONLY", color = "black", on_color="on_red"))
        fittype = 'BONLY'

    batchSystem = str(options.batchsystem)
    batchQueue = str(options.batchqueue)


    print('''
Options set for this Job:

use_asimov = {}
do_Scaling = {}
do_Asimov = {}
do_Combine = {}
do_Separate_Fitting = {}
do_Combined_Fitting = {}
do_Separate_Limits = {}
do_Combined_Limits = {}
do_Separate_Ranking_Fits = {}
do_Combined_Ranking_Fits = {}
do_TRExFComp = {}
do_TRExFConfigs = {}
do_Separate_Ranking_Plots = {}
do_Combined_Ranking_Plots = {}
use_data = {}
DataLoc = {}
fittype = {}
mu = {}
masses = {}
kappas = {}
BRWs = {}
'''
.format(
    not use_data,
    do_Scaling,
    do_Asimov,
    do_Combine,
    do_Separate_Fitting,
    do_Combined_Fitting,
    do_Separate_Limits,
    do_Combined_Limits,
    do_Separate_Ranking_Fits,
    do_Combined_Ranking_Fits,
    do_TRExFComp,
    do_TRExFConfigs,
    do_Separate_Ranking_Plots,
    do_Combined_Ranking_Plots,
    use_data,
    DataLoc,
    fittype,
    mu,
    masses,
    kappas,
    BRWs))

    print ('DataLoc = '+DataLoc) 
    if DataLoc.startswith('/'):
        INPUTDIR = ''
        print('Absolute path')
    else:
        INPUTDIR = os.getcwd()+'/'
    print ('INPUTDIR = '+INPUTDIR) 
    TRExFConfDir = INPUTDIR + DataLoc + '/trexf/'
    print( 'TRExFConfDir = '+TRExFConfDir)
    if not os.path.exists(TRExFConfDir):
        os.system("mkdir -p " + TRExFConfDir)
    
    FitLogDir = INPUTDIR + DataLoc + '/fit_logs/'
    print( 'FitLogDir = '+FitLogDir)
    if not os.path.exists(FitLogDir):
        os.system("mkdir -p " + FitLogDir)

    WSListDir = INPUTDIR + DataLoc + '/ws_lists/'
    print( 'WSListDir = '+WSListDir)
    if not os.path.exists(WSListDir):
        os.system("mkdir -p " + WSListDir)

    for key,value in pathdict.items():
        print(key + ' : ' + value)    

    ALL_CFGs = {}

    for ana in ['SPT_OSML', 'SPT_HTZT', 'SPT_MONOTOP']:
        print("Creating CombinationConfig for {}".format(ana))
        ALL_CFGs[ana]  = VLQCombinationConfig(AnaCode = ana, 
                                              DataFolder = DataLoc,
                                              WSName = 'combWS' if ana == 'SPT_OSML' else 'combined',
                                              InputDir = INPUTDIR,
                                              makePaths = False,
                                              checkPaths = False)
        ALL_CFGs[ana].setSubDir(pathdict, makePaths = True)

    print("Creating CombinationConfig for SPT_COMBINED")
    combination_cfg = VLQCombinationConfig(AnaCode = 'SPT_COMBINED',
                                           DataFolder = DataLoc,                                                      
                                           WSName = 'combWS',
                                           InputDir = INPUTDIR,
                                           makePaths = True,
                                           checkPaths = False)
    combination_cfg.setSubDir(pathdict, makePaths = True)

    for (mass, kappa, brw) in product(*[masses, kappas, BRWs]):
        if use_defScaling:
            mu = getmuScale(mass, kappa, brw, all_modes = ['WTZt', 'WTHt', 'ZTZt', 'ZTHt'])
        sigtag = getSigTag(mass, kappa, brw)
        mktag = getMKTag(mass, kappa)
        ws_list = ""
        ws_asimov_list = ""
        ###################### ACTIONS FOR INDIVIDUAL ANALYSES ########################################
        for ana in ALL_CFGs.keys():
            cfg = ALL_CFGs[ana]

            if do_Scaling:
                print("Scaling {} WS for {}".format(ana, colored(sigtag, color = "green")))
                scalingconfig = cfg.getScalingConfig(mass, 
                                                     kappa, 
                                                     brw, 
                                                     datatag)
                if not scalingconfig:
                    print(colored("Scaling config could not be created for {} for {}!".format(ana, sigtag), color = "black", on_color="on_red"))
                    time.sleep(5)
                    continue
                scaling = cfg.scaleWS(mass, 
                                      kappa, 
                                      brw, 
                                      datatag,
                                      LogFile="{}/logScaling_{}_{}_{}.txt".format(cfg.LogDir, ana, sigtag, datatag))
                if not scaling:
                    print(colored("Scaled WS could not be created for {} for {}!".format(ana, sigtag), color = "black", on_color="on_red"))
                    time.sleep(5)
                    continue

            if do_Combine:
                if not os.path.exists(cfg.getScaledWSPath(mass, kappa, brw, datatag)):
                    print(colored("Scaled WS was not found for {} for {}!".format(ana, sigtag), color = "black", on_color="on_red"))
                    time.sleep(5)
                    continue
                else:
                    ws_list += '{}  :  {}  :  {}\n'.format(ana, cfg.getScaledWSPath(mass, kappa, brw, datatag), cfg.WSName)

            if do_Asimov:
                asimovconfig = cfg.getAsimovConfig(mass, 
                                                   kappa, 
                                                   brw, 
                                                   mu)
                if asimovconfig:
                    asimov = cfg.getAsimovWS(mass, 
                                             kappa, 
                                             brw, 
                                             mu, 
                                             LogFile="{}/logAsimov_mu{}_{}_{}.txt".format(cfg.LogDir, int(mu*100), ana, sigtag))
                    if not asimov:
                        print(colored("Getting Asimov WS with mu = {} could not be done for {} for {}!".format(mu, ana, sigtag), color = "black", on_color="on_red"))
                        time.sleep(5)
                    else:
                        print(colored("Getting Asimov WS with mu = {} successful for {} for {}!".format(mu, ana, sigtag), color = "black", on_color="on_green"))
                        ws_asimov_list += '{}  :  {}  :  {}\n'.format(ana, cfg.getAsimovWSPath(mass, kappa, brw, mu), cfg.WSName)
                else:
                    print(colored("Getting Asimov Config with mu = {} could not be done for {} for {}!".format(mu, ana, sigtag), color = "black", on_color="on_red"))
                    time.sleep(5)

            if do_Separate_Fitting:
                print("Fitting {} WS for {}".format(ana, colored(sigtag, color = "green")))
                fit = cfg.fitWS(mass, 
                                kappa, 
                                brw, 
                                mu = mu, 
                                fittype = fittype, 
                                isAsimov = not use_data,
                                LogFile="{}/logFitting_{}_{}_{}_{}.txt".format(cfg.LogDir, ana, sigtag, datatag,fittype)) 
                if not fit:
                    print(colored("Fitting WS could not be done for {} for {}!".format(ana, sigtag), color = "black", on_color="on_red"))
                    time.sleep(5)
                else:
                    print(colored("Fitting WS done for {} for {}!".format(ana, sigtag), color = "black", on_color="on_green"))
                    time.sleep(5)

            if do_TRExFComp:
                outfname = cfg.getAsimovWSPath(mass, kappa, brw, mu).split('/')[-1].replace('.root', '') if not use_data \
                           else cfg.getScaledWSPath(mass, kappa, brw, datatag).split('/')[-1].replace('.root', '')
                outfname += '_' + fittype
                #comp = getTRExFFitFile(in_fname = "{}/logFitting_{}_{}_{}.txt".format(cfg.LogDir, 
                #                                                                    ana, 
                #                                                                    sigtag, 
                #                                                                    datatag), 
                #                       out_fname = FitLogDir + '/' + outfname + ".txt")

                comp = getTRExFFitFile( in_fname = cfg.getFittedResultPath(mass, kappa, brw, mu, fittype, (not use_data)),
                                        out_fname = FitLogDir + '/' + outfname + ".txt", fromLog = False)
                if not comp:
                    print(colored("Getting TRExF comp file could not be done for {} for {}!".format(ana, sigtag), color = "black", on_color="on_red"))
                    time.sleep(5)

                code = plotCorrelationMatrix(wsFile = cfg.getAsimovWSPath(mass, kappa, brw, mu) if not use_data \
                                             else cfg.getScaledWSPath(mass, kappa, brw, datatag), 
                                             fitResultFile =  cfg.getFittedResultPath(mass, kappa, brw, mu, fittype, (not use_data)),
                                             outputPath = FitLogDir, 
                                             wsName = cfg.WSName, 
                                             plotName = "Correlations_"+outfname)

                if not code:
                    print(colored("Correlation matrix could not be plotted for {} for {}!".format(ana, sigtag), color = "black", on_color="on_red"))
                    time.sleep(5)

            if do_Separate_Limits:
                limit = cfg.getLimits(mass, 
                                      kappa, 
                                      brw, 
                                      mu = mu, 
                                      isAsimov = not use_data, 
                                      LogFile="{}/logLimits_{}_{}_{}.txt".format(cfg.LogDir, ana, sigtag, datatag))
                if not limit:
                    print(colored("Limits could not be done for {} for {}!".format(ana, sigtag), color = "black", on_color="on_red"))
                    time.sleep(5)
                else:
                    print(colored("Limit done for {} for {}!".format(ana, sigtag), color = "black", on_color="on_green"))
                    time.sleep(5)



            if( do_Separate_Ranking_Fits or do_Separate_Ranking_Plots ):
                #get the paths from combutils
                ranking_path = cfg.getRankingPath(mass, kappa, brw, mu=mu, isAsimov=not use_data)

                dsName = "obsData" if use_data else "asimovData_mu{}".format(int(mu*100))
                wsPath = cfg.getScaledWSPath(mass, kappa, brw, datatag) if use_data \
                         else cfg.getAsimovWSPath(mass, kappa, brw, mu)
            
                outfname = cfg.getScaledWSPath(mass, kappa, brw, datatag).split('/')[-1].replace('.root', '') if use_data \
                           else cfg.getAsimovWSPath(mass, kappa, brw, mu).split('/')[-1].replace('.root', '')
                outfname += '_' + fittype
                fitFileName = FitLogDir + '/' + outfname + ".txt"
            
                #define the ranking plotter
                ranking_plotter = RankingPlotter(wsPath, cfg.WSName, dsName, fitFileName,
                                                 ranking_path, ranking_nmerge, ranking_includeGammas, 
                                                 batch=batchSystem, batch_queue=batchQueue,
                                                 dry_run=do_dry_run,debug=debug_level)

                ranking_plotter.ReadFitResultTextFile()
                if(do_Separate_Ranking_Fits):
                    ranking_plotter.LaunchRankingFits(True, overwrite=do_Overwrite_ranking)
                if(do_Separate_Ranking_Plots):
                    ranking_plotter.WriteTRexFRankingFile()
                    confName = ranking_plotter.GetTRexFConfigFile()
                    code = os.system("cd {} && trex-fitter r {} Ranking=plot && cd -".format(cfg.RankingDir, confName))
                    if not code == 0:
                        print(colored("TRExFitter ranking plot failed for {} in channel {}!".format(sigtag, ana), 
                                      color = "black", on_color="on_red"))
                        time.sleep(5)

        ###################### ACTIONS FOR COMBINED WORKSPACE ########################################
        if do_Combine:
            print("Starting the Combination for {}".format(colored(sigtag, color = "green")))
            time.sleep(5)

            wslist_fname = WSListDir + '/wsList4CombConfig_{}_{}.txt'.format(sigtag, datatag)
            f = open(wslist_fname, "w")
            f.write(ws_list)
            f.close()
            print("WS List is available at " + colored(wslist_fname, color = "black", on_color="on_green"))


            CombConfig = combination_cfg.getCombinationConfig(WSListFile = wslist_fname, 
                                                              mass= mass,
                                                              kappa = kappa,
                                                              brw = brw,
                                                              mu = mu,
                                                              DataName = InDataName)

            if not CombConfig:
                print(colored("Generating Combination Config failed for {}".format(sigtag), color = "black", on_color="on_red"))
                continue
            combined = combination_cfg.combineWS(mass, 
                                                 kappa, 
                                                 brw, 
                                                 datatag,
                                                 LogFile="{}/logCombine_SPT_COMBINED_{}_{}.txt".format(combination_cfg.LogDir, sigtag, datatag))
            if not combined:
                print(colored("Combination failed for {}".format(sigtag), color = "black", on_color="on_red"))
                time.sleep(5)
                continue
            else:
                ws_list += 'SPT_COMBINED  :  {}  :  {}\n'.format(combination_cfg.getCombinedWSPath(mass, kappa, brw, datatag), combination_cfg.WSName)
                wslist4config_fname = WSListDir + '/wsList4TrexConfig_{}_{}.txt'.format (sigtag, datatag)
                f = open(wslist4config_fname, "w")
                f.write(ws_list)
                f.close()

        if do_Asimov:
            asimovconfig = combination_cfg.getAsimovConfig(mass, 
                                                           kappa, 
                                                           brw, 
                                                           mu)
            if asimovconfig:
                asimov = combination_cfg.getAsimovWS(mass, 
                                                     kappa, 
                                                     brw, 
                                                     mu, 
                                                     LogFile="{}/logAsimov_mu{}_SPT_COMBINED_{}.txt".format(combination_cfg.LogDir, 
                                                                                                            int(mu*100), sigtag))
                if not asimov:
                    print(colored("Getting Asimov WS with mu = {} could not be done for SPT_COMBINED for {}!".format(mu, sigtag), color = "black", on_color="on_red"))
                    time.sleep(5)
                else:
                    ws_asimov_list += 'SPT_COMBINED  :  {}  :  {}\n'.format(combination_cfg.getAsimovWSPath(mass, kappa, brw, mu), combination_cfg.WSName)
                    wslist4config_fname = WSListDir + '/wsAsimovList4TrexConfig_{}_{}.txt'.format (sigtag, datatag)
                    f = open(wslist4config_fname, "w")
                    f.write(ws_asimov_list)
                    f.close()


            else:
                print(colored("Getting Asimov Config with mu = {} could not be done for SPT_COMBINED for {}!".format(mu, sigtag), color = "black", on_color="on_red"))
                time.sleep(5)

        if do_Combined_Fitting:
            print("Fitting SPT_COMBINED WS for {}".format(colored(sigtag, color = "green")))
            fit = combination_cfg.fitWS(mass, 
                                        kappa, 
                                        brw, 
                                        mu, 
                                        fittype = fittype, 
                                        isAsimov = not use_data, 
                                        LogFile="{}/logFitting_SPT_COMBINED_{}_{}_{}.txt".format(combination_cfg.LogDir, 
                                                                                                 sigtag, 
                                                                                                 datatag,fittype))
            if not fit:
                print(colored("Fitting WS could not be done for SPT_COMBINED for {}!".format(sigtag), color = "black", on_color="on_red"))
                time.sleep(5)
            else:
                print(colored("Fitting WS done for SPT_COMBINED for {}!".format(sigtag), color = "black", on_color="on_green"))
                time.sleep(5)


        if do_Combined_Limits:
            limit = combination_cfg.getLimits(mass, 
                                              kappa, 
                                              brw, 
                                              mu = mu, 
                                              isAsimov = not use_data, 
                                              LogFile="{}/logLimits_SPT_COMBINED_{}_{}.txt".format(combination_cfg.LogDir, sigtag, datatag))
            if not limit:
                print(colored("Limits could not be done for SPT_COMBINED for {}!".format(sigtag), color = "black", on_color="on_red"))
                time.sleep(5)
                sys.exit(1)
            else:
                print(colored("Limit done for SPT_COMBINED for {}!".format(sigtag), color = "black", on_color="on_green"))
                time.sleep(5)

        if do_TRExFConfigs:
            fname = ''
            if not use_data:
                if not os.path.exists(combination_cfg.getAsimovWSPath(mass, kappa, brw, mu)):
                    print(colored("Asimov WS could not be found for SPT_COMBINED for {}!".format(sigtag), color = "black", on_color="on_red"))
                    time.sleep(5)
                    sys.exit(1)
                else:
                    fname = WSListDir + '/wsAsimovList4TrexConfig_{}_{}.txt'.format (sigtag, datatag)
            else:
                if not os.path.exists(combination_cfg.getCombinedWSPath(mass, kappa, brw, datatag)):
                    print(colored("Combined WS could not be found for SPT_COMBINED for {}!".format(sigtag), color = "black", on_color="on_red"))
                    time.sleep(5)
                    sys.exit(1)
                else:
                    fname = WSListDir + '/wsList4TrexConfig_{}_{}.txt'.format (sigtag, datatag)
            if fname:
                status = getTRExFConfigs(ConfDir = TRExFConfDir, 
                                         WSListFile = fname, 
                                         sigtag = sigtag,
                                         mu = mu, 
                                         fittype = fittype,
                                         isAsimov= not use_data)
                if not status:
                    print(colored("TRExF Configs could not be generated for SPT_COMBINED for {}!".format(sigtag), color = "black", on_color="on_red"))
                    time.sleep(5)

        if do_TRExFComp:
            outfname = combination_cfg.getAsimovWSPath(mass, kappa, brw, mu).split('/')[-1].replace('.root', '') \
                       if not use_data \
                       else combination_cfg.getCombinedWSPath(mass, kappa, brw, datatag).split('/')[-1].replace('.root', '')
            outfname += '_' + fittype
            comp = getTRExFFitFile(in_fname = combination_cfg.getFittedResultPath(mass, kappa, brw, mu, fittype, (not use_data)),
                                   out_fname = FitLogDir + '/' + outfname + ".txt", fromLog = False)

            #comp = getTRExFFitFile(in_fname = "{}/logFitting_SPT_COMBINED_{}_{}.txt".format(combination_cfg.LogDir, 
            #                                                                              sigtag, 
            #                                                                              datatag), 
            #                       out_fname = FitLogDir + '/' + outfname + ".txt")
            if not comp:
                print(colored("Getting TRExF comp file could not be done for SPT_COMBINED for {}!".format(sigtag), color = "black", on_color="on_red"))
                time.sleep(5)

            code = plotCorrelationMatrix(wsFile = combination_cfg.getAsimovWSPath(mass, kappa, brw, mu) \
                                         if not use_data \
                                         else combination_cfg.getCombinedWSPath(mass, kappa, brw, datatag),
                                         fitResultFile = 
                                         combination_cfg.getFittedResultPath(mass, kappa, brw, mu, fittype, (not use_data)),
                                         outputPath = FitLogDir, 
                                         wsName = combination_cfg.WSName, 
                                         plotName = "Correlations_"+outfname)
            if not code:
                print(colored("Correlation matrix could not be plotted for SPT_COMBINED for {}!".format(sigtag), color = "black", on_color="on_red"))
                time.sleep(5)

            tag_flag = sigtag + "_"+ datatag + "_"+ fittype
            compdir = makeTRExFCompDirs(ConfDir = TRExFConfDir, 
                                        LogDir = FitLogDir, 
                                        sigtag = sigtag, 
                                        mu = mu,
                                        fittype = fittype,
                                        isAsimov = not use_data)
            if not compdir:
                print(colored("TRExF Directories could not be setup for {}!".format(sigtag), color = "black", on_color="on_red"))
                time.sleep(5)
            else:
                code = os.system("cd {} && trex-fitter m configFile_multifit_{}.txt && cd -".format(TRExFConfDir, tag_flag))
                if not code == 0:
                    print(colored("TRExFitter multi-fit failed for {}!".format(sigtag), color = "black", on_color="on_red"))
                    time.sleep(5)

        if( do_Combined_Ranking_Fits or do_Combined_Ranking_Plots ):
            #get the paths from combutils
            ranking_path_comb = combination_cfg.getRankingPath(mass, kappa, brw, mu=mu, isAsimov=not use_data)

            #dsName_comb = "obsData" if use_data else "combData"
            dsName_comb = "combData" if use_data else "asimovData_mu{}".format(int(mu*100))
            wsPath_comb = combination_cfg.getCombinedWSPath(mass, kappa, brw, datatag) if use_data \
                     else combination_cfg.getAsimovWSPath(mass, kappa, brw, mu)
            
            outfname_comb = combination_cfg.getCombinedWSPath(mass, kappa, brw, datatag).split('/')[-1].replace('.root', '') \
                       if use_data \
                       else combination_cfg.getAsimovWSPath(mass, kappa, brw, mu).split('/')[-1].replace('.root', '')
            outfname_comb += '_' + fittype
            fitFileName_comb = FitLogDir + '/' + outfname_comb + ".txt"
            
            #define the ranking plotter
            ranking_plotter_comb = RankingPlotter(wsPath_comb, combination_cfg.WSName, dsName_comb, fitFileName_comb,
                                                  ranking_path_comb, ranking_nmerge, ranking_includeGammas,
                                                  batch=batchSystem, batch_queue=batchQueue,
                                                  dry_run=do_dry_run,debug=debug_level)
            print("Reading from:", fitFileName_comb)
            ranking_plotter_comb.ReadFitResultTextFile()
            if(do_Combined_Ranking_Fits):
                ranking_plotter_comb.LaunchRankingFits(True, overwrite=do_Overwrite_ranking)
            if(do_Combined_Ranking_Plots):
                ranking_plotter_comb.WriteTRexFRankingFile()
                confName = ranking_plotter_comb.GetTRexFConfigFile()
                code = os.system("cd {} && trex-fitter r {} Ranking=plot && cd -".format(combination_cfg.RankingDir, confName))
                if not code == 0:
                    print(colored("TRExFitter combined ranking plot failed for {}!".format(sigtag), 
                                  color = "black", on_color="on_red"))
                    time.sleep(5)
