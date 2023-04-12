#!/bin/python3

import sys, os
sys.path.append(os.getenv("VLQCOMBDIR") + "/VLQ_Interpretation_Tools")

from VLQCouplingCalculator import VLQCouplingCalculator as vlq
from VLQCrossSectionCalculator import *
from termcolor import colored
from CombUtils import *
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
    parser.add_option("--fit-type", 
                      dest="fittype",
                      help='Provide the fit type: BONLY or SPLUSB',
                      default='BONLY')
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


    (options, args) = parser.parse_args()

    do_Scaling = bool(options.doscaling)
    do_Asimov = bool(options.doasimov)
    do_Combine = bool(options.docombine)
    do_Separate_Fitting = bool(options.dosepfit)
    do_Combined_Fitting = bool(options.docombfit)
    do_Separate_Limits =  bool(options.doseplims)
    do_Combined_Limits =  bool(options.docomblims)
    do_TRExFComp =  bool(options.dotrexfcomp) 
    do_TRExFConfigs = True if do_TRExFComp else bool(options.dotrexfcfgs) # This flag is overwritten when comparison plots are required
    use_data = False if do_Asimov else bool(options.usedata) # This flag is ovrwritten when asimov workspaces are required

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
                'LogSubDir' : str(options.logsubdir)
                }

    mu = float(options.mu)
    masses = list(map(float, str(options.masses).split(',')))
    kappas = list(map(float, str(options.kappas).split(',')))
    BRWs = list(map(float, str(options.brws).split(',')))

    InDataName = 'asimovData' if not use_data else "obsData"
    datatag = 'data' if use_data else 'asimov_mu{}'.format(int(mu*100))

    if fittype not in ['BONLY', 'SPLUSB']:
        print(colored("Unrecognized Fit Type (--fit-type) option. Reverting to BONLY", color = "black", on_color="on_red"))
        fittype = 'BONLY'

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
do_TRExFConfigs = {}
do_TRExFComp = {}
DataLoc = {}
mu = {}
masses = {}
kappas = {}
BRWs = {}
fittype = {}
'''.format(
    not use_data,
    do_Scaling,
    do_Asimov,
    do_Combine,
    do_Separate_Fitting,
    do_Combined_Fitting,
    do_Separate_Limits,
    do_Combined_Limits,
    do_TRExFConfigs,
    do_TRExFComp,
    DataLoc,
    mu,
    masses,
    kappas,
    BRWs,
    fittype
))

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
        sigtag = getSigTag(mass, kappa, brw)
        mktag = getMKTag(mass, kappa)
        ws_list = ""
        ws_asimov_list = ""
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
                                LogFile="{}/logFitting_{}_{}_{}.txt".format(cfg.LogDir, ana, sigtag, datatag)) 
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
                comp = getTRExFFitFile(in_log = "{}/logFitting_{}_{}_{}.txt".format(cfg.LogDir, 
                                                                                    ana, 
                                                                                    sigtag, 
                                                                                    datatag), 
                                       out_fname = FitLogDir + '/' + outfname + ".txt")
                if not comp:
                    print(colored("Getting TRExF comp file could not be done for {} for {}!".format(ana, sigtag), color = "black", on_color="on_red"))
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
                                        LogFile="{}/logFitting_SPT_COMBINED_{}_{}.txt".format(combination_cfg.LogDir, 
                                                                                              sigtag, 
                                                                                              datatag))
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
            outfname = combination_cfg.getAsimovWSPath(mass, kappa, brw, mu).split('/')[-1].replace('.root', '') if not use_data \
                       else combination_cfg.getCombinedWSPath(mass, kappa, brw, datatag).split('/')[-1].replace('.root', '')
            outfname += '_' + fittype
            comp = getTRExFFitFile(in_log = "{}/logFitting_SPT_COMBINED_{}_{}.txt".format(combination_cfg.LogDir, 
                                                                                          sigtag, 
                                                                                          datatag), 
                                   out_fname = FitLogDir + '/' + outfname + ".txt")
            if not comp:
                print(colored("Getting TRExF comp file could not be done for SPT_COMBINED for {}!".format(sigtag), color = "black", on_color="on_red"))
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

