import sys, os
sys.path.append("VLQ_Interpretation_Tools")

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
    parser.add_option("--no-scaling", 
                      dest="doscaling",
                      help='set if scaling input workspaces is not required',
                      action='store_false',
                      default=True)
    parser.add_option("--no-asimov", 
                      dest="doasimov",
                      help='set if real data is to be used instead of asimov',
                      action='store_false',
                      default=True)
    parser.add_option("--mu", dest="mu",
                      help='Choice of mu for asimov dataset',
                      default='0.0')
    parser.add_option("--no-combine", 
                      dest="docombine",
                      help='set if combination of workspaces is not required',
                      action='store_false',
                      default=True)
    parser.add_option("--fit-type", 
                      dest="fittype",
                      help='Provide the fit type: BONLY or SPLUSB',
                      default='BONLY')
    parser.add_option("--no-separate-fitting", 
                      dest="dosepfit",
                      help='set if independent fitting of workspaces is not required',
                      action='store_false',
                      default=True)
    parser.add_option("--no-combined-fitting", 
                      dest="docombfit",
                      help='set if fitting of combined workspaces is not required',
                      action='store_false',
                      default=True)
    parser.add_option("--no-separate-limits", 
                      dest="doseplims",
                      help='set if independent limits are not required',
                      action='store_false',
                      default=True)
    parser.add_option("--no-combined-limits", 
                      dest="docomblims",
                      help='set if combined limits not required',
                      action='store_false',
                      default=True)
    parser.add_option("--no-trexf-configs", 
                      dest="dotrexfcfgs",
                      help='set if TRExFitter Configs are not required',
                      action='store_false',
                      default=True)
    parser.add_option("--no-trexf-comp", 
                      dest="dotrexfcomp",
                      help='set if TRExFitter Comps are not required',
                      action='store_false',
                      default=True)


    (options, args) = parser.parse_args()

    ## The following will be taken from CL Input
    do_Scaling = bool(options.doscaling)
    do_Asimov = bool(options.doasimov)
    do_Combine = bool(options.docombine)
    do_Separate_Fitting = bool(options.dosepfit)
    do_Combined_Fitting = bool(options.docombfit)
    do_Separate_Limits =  bool(options.doseplims)
    do_Combined_Limits =  bool(options.docomblims)
    do_TRExFConfigs = bool(options.dotrexfcfgs) # This flag will only work if either do_Combine or do_Asimov is True
    do_TRExFComp =  bool(options.dotrexfcomp) 
    DataLoc = str(options.dataloc)
    fittype = str(options.fittype)
    mu = float(options.mu)
    masses = list(map(float, str(options.masses).split(',')))
    kappas = list(map(float, str(options.kappas).split(',')))
    BRWs = list(map(float, str(options.brws).split(',')))

    InDataName = 'asimovData' if do_Asimov else "obsData"
    if do_TRExFComp:
        do_TRExFConfigs = True
    if fittype not in ['BONLY', 'SPLUSB']:
        print(colored("Unrecognized Fit Type (--fit-type) option. Reverting to BONLY", color = "black", on_color="on_red"))
        fittype = 'BONLY'

    print('''
Options set for this Job:

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

    TRExFConfDir = VLQCOMBDIR + '/' + DataLoc + '/trexf/'
    if not os.path.exists(TRExFConfDir):
        os.system("mkdir -p " + TRExFConfDir)

    FitLogDir = VLQCOMBDIR + '/' + DataLoc + '/fit_logs/'
    if not os.path.exists(FitLogDir):
        os.system("mkdir -p " + FitLogDir)
    

    ALL_CFGs = {}

    for ana in ['SPT_OSML', 'SPT_HTZT', 'SPT_MONOTOP']:
        print("Creating CombinationConfig for {}".format(ana))
        ALL_CFGs[ana]  = VLQCombinationConfig(AnaCode = ana, 
                                              DataFolder = DataLoc, ## CHECK: Location of data needs to be a CL Input
                                              WSName = 'combWS' if ana == 'SPT_OSML' else 'combined',
                                              makePaths = True)

    print("Creating CombinationConfig for SPT_COMBINED")
    combination_cfg = VLQCombinationConfig(AnaCode = 'SPT_COMBINED',
                                              DataFolder = DataLoc, ## CHECK: Location of data needs to be a CL Input                                                     
                                              WSName = 'combWS',
                                              makePaths = True)

    for (mass, kappa, brw) in product(*[masses, kappas, BRWs]):
        sigtag = getSigTag(mass, kappa, brw)
        mktag = getMKTag(mass, kappa)
        ws_list = ""
        ws_asimov_list = ""
        for ana in ALL_CFGs.keys():
            cfg = ALL_CFGs[ana]

            if do_Scaling:
                scalingconfig = cfg.getScalingConfig(mass, kappa, brw, DataName=InDataName) ## CHECK: DataName needs to be a CL Input
                if not scalingconfig:
                    print(colored("Scaling config could not be created for {} for {}!".format(ana, sigtag), color = "black", on_color="on_red"))
                    time.sleep(5)
                    continue
                scaling = cfg.scaleWS(mass, kappa, brw, LogFile="logScaling_{}_{}.txt".format(ana, sigtag))
                if not scaling:
                    print(colored("Scaled WS could not be created for {} for {}!".format(ana, sigtag), color = "black", on_color="on_red"))
                    time.sleep(5)
                    continue

            if do_Combine:
                if not os.path.exists(cfg.getScaledWSPath(mass, kappa, brw)):
                    print(colored("Scaled WS was not found for {} for {}!".format(ana, sigtag), color = "black", on_color="on_red"))
                    time.sleep(5)
                    continue
                ws_list += '{}  :  {}  :  {}\n'.format(ana, cfg.getScaledWSPath(mass, kappa, brw), cfg.WSName)

            if do_Asimov:
                asimovconfig = cfg.getAsimovConfig(mass, kappa, brw, mu)
                if asimovconfig:
                    asimov = cfg.getAsimovWS(mass, kappa, brw, mu, LogFile="logAsimov_mu{}_{}_{}.txt".format(int(mu*100),ana,sigtag))
                    if not asimov:
                        print(colored("Getting Asimov WS with mu = {} could not be done for {} for {}!".format(mu, ana, sigtag), color = "black", on_color="on_red"))
                        time.sleep(5)
                    ws_asimov_list += '{}  :  {}  :  {}\n'.format(ana, cfg.getAsimovWSPath(mass, kappa, brw, mu), cfg.WSName)
                else:
                    print(colored("Getting Asimov Config with mu = {} could not be done for {} for {}!".format(mu, ana, sigtag), color = "black", on_color="on_red"))
                    time.sleep(5)

            if do_Separate_Fitting:
                # Will do Asimov Fitting if Asimov creation is asked
                fit = cfg.fitWS(mass, kappa, brw, mu=mu, fittype=fittype, isAsimov=do_Asimov, LogFile="logFitting_{}_{}.txt".format(ana, sigtag)) 
                if not fit:
                    print(colored("Fitting WS could not be done for {} for {}!".format(ana, sigtag), color = "black", on_color="on_red"))
                    time.sleep(5)
                else:
                    print(colored("Fitting WS done for {} for {}!".format(ana, sigtag), color = "black", on_color="on_green"))
                    time.sleep(5)

            if do_TRExFComp:
                outfname = cfg.getAsimovWSPath(mass, kappa, brw, mu).split('/')[-1].replace('.root', '') if do_Asimov \
                           else cfg.getScaledWSPath(mass, kappa, brw).split('/')[-1].replace('.root', '')
                outfname += '_' + fittype
                comp = getTRExFFitFile(in_log = "logFitting_{}_{}.txt".format(ana, sigtag), 
                                       out_fname = FitLogDir + '/' + outfname + ".txt")
                if not comp:
                    print(colored("Getting TRExF comp file could not be done for {} for {}!".format(ana, sigtag), color = "black", on_color="on_red"))
                    time.sleep(5)
                

            if do_Separate_Limits:
                limit = cfg.getLimits(mass, kappa, brw, mu=mu, isAsimov=do_Asimov, LogFile="logLimits_{}_{}.txt".format(ana, sigtag))
                if not limit:
                    print(colored("Limits could not be done for {} for {}!".format(ana, sigtag), color = "black", on_color="on_red"))
                    time.sleep(5)
                else:
                    print(colored("Limit done for {} for {}!".format(ana, sigtag), color = "black", on_color="on_green"))
                    time.sleep(5)
                

        if do_Combine:
            print(colored("Starting the Combination for {}".format(sigtag), color = "black", on_color = "on_green"))
            time.sleep(5)
            f = open("wsList.txt", "w") ## CHECK: this filename should be a CL Input
            f.write(ws_list)
            f.close()
            print("WS List is available at " + colored('wsList.txt', color = "black", on_color="on_green"))


            CombConfig = combination_cfg.getCombinationConfig(WSListFile = "wsList.txt", 
                                                              mass= mass,
                                                              kappa = kappa,
                                                              brw = brw,
                                                              DataName = InDataName)

            if not CombConfig:
                print(colored("Generating Combination Config failed for {}".format(sigtag), color = "black", on_color="on_red"))
                continue
            combined = combination_cfg.combineWS(mass, kappa, brw, LogFile="log_combine_{}.txt".format(sigtag))
            if not combined:
                print(colored("Combination failed for {}".format(sigtag), color = "black", on_color="on_red"))
                time.sleep(5)
                continue

        if do_Asimov:
            asimovconfig = combination_cfg.getAsimovConfig(mass, kappa, brw, mu)
            if asimovconfig:
                asimov = combination_cfg.getAsimovWS(mass, kappa, brw, mu, LogFile="logAsimov_mu{}_{}.txt".format(ana,sigtag))
                if not asimov:
                    print(colored("Getting Asimov WS with mu = {} could not be done for SPT_COMBINED for {}!".format(mu, sigtag), color = "black", on_color="on_red"))
                    time.sleep(5)
            else:
                print(colored("Getting Asimov Config with mu = {} could not be done for SPT_COMBINED for {}!".format(mu, sigtag), color = "black", on_color="on_red"))
                time.sleep(5)

        if do_Combined_Fitting:
             # Will do Asimov Fitting if Asimov creation is asked
            fit = combination_cfg.fitWS(mass, kappa, brw, mu, fittype=fittype, isAsimov=do_Asimov, LogFile="logFitting_SPT_COMBINED_{}.txt".format(sigtag))
            if not fit:
                print(colored("Fitting WS could not be done for SPT_COMBINED for {}!".format(sigtag), color = "black", on_color="on_red"))
                time.sleep(5)
            else:
                print(colored("Fitting WS done for SPT_COMBINED for {}!".format(sigtag), color = "black", on_color="on_green"))
                time.sleep(5)

        if do_TRExFComp:
            outfname = combination_cfg.getAsimovWSPath(mass, kappa, brw, mu).split('/')[-1].replace('.root', '') if do_Asimov \
                       else combination_cfg.getCombinedWSPath(mass, kappa, brw).split('/')[-1].replace('.root', '')
            outfname += '_' + fittype
            comp = getTRExFFitFile(in_log = "logFitting_SPT_COMBINED_{}.txt".format(sigtag), 
                                   out_fname = FitLogDir + '/' + outfname + ".txt")
            if not comp:
                print(colored("Getting TRExF comp file could not be done for SPT_COMBINED for {}!".format(sigtag), color = "black", on_color="on_red"))
                time.sleep(5)

        if do_Combined_Limits:
            limit = combination_cfg.getLimits(mass, kappa, brw, mu=mu, isAsimov=do_Asimov, LogFile="logLimits_SPT_COMBINED_{}.txt".format(sigtag))
            if not limit:
                print(colored("Limits could not be done for SPT_COMBINED for {}!".format(sigtag), color = "black", on_color="on_red"))
                time.sleep(5)
                sys.exit(1)
            else:
                print(colored("Limit done for SPT_COMBINED for {}!".format(sigtag), color = "black", on_color="on_green"))
                time.sleep(5)

        if do_TRExFConfigs:
            list2write = None
            if do_Asimov:
                if not os.path.exists(combination_cfg.getAsimovWSPath(mass, kappa, brw, mu)):
                    print(colored("Asimov WS could not be found for SPT_COMBINED for {}!".format(sigtag), color = "black", on_color="on_red"))
                    time.sleep(5)
                else:
                    ws_asimov_list += 'SPT_COMBINED  :  {}  :  {}\n'.format(combination_cfg.getAsimovWSPath(mass, kappa, brw, mu), combination_cfg.WSName)
                    list2write = ws_asimov_list
            else:
                if not os.path.exists(combination_cfg.getCombinedWSPath(mass, kappa, brw)):
                    print(colored("Combined WS could not be found for SPT_COMBINED for {}!".format(sigtag), color = "black", on_color="on_red"))
                    time.sleep(5)
                else:
                    ws_list += 'SPT_COMBINED  :  {}  :  {}\n'.format(combination_cfg.getCombinedWSPath(mass, kappa, brw), combination_cfg.WSName)
                    list2write = ws_list
            if list2write:
                f = open("wsList4Configs.txt", "w")
                f.write(list2write)
                f.close()
                status = getTRExFConfigs(ConfDir = TRExFConfDir, 
                                         WSListFile = "wsList4Configs.txt", 
                                         sigtag = sigtag,
                                         mu=mu, 
                                         fittype=fittype,
                                         isAsimov= do_Asimov) ## to be continued
                if not status:
                    print(colored("TRExF Configs could not be generated for SPT_COMBINED for {}!".format(sigtag), color = "black", on_color="on_red"))
                    time.sleep(5)

        if do_TRExFComp:
            tag_flag = ("asimov_mu{}_".format(int(mu*100)) if do_Asimov else "data_") + sigtag + "_" + fittype
            compdir = makeTRExFCompDirs(ConfDir = TRExFConfDir, 
                                        LogDir = FitLogDir, 
                                        sigtag = sigtag, 
                                        mu = mu,
                                        fittype=fittype,
                                        isAsimov = do_Asimov)
            if not compdir:
                print(colored("TRExF Directories could not be setup for {}!".format(sigtag), color = "black", on_color="on_red"))
                time.sleep(5)
            else:
                code = os.system("cd {} && trex-fitter m configFile_multifit_{}.txt && cd -".format(TRExFConfDir, tag_flag))
                if not code:
                    print(colored("TRExFitter multi-fit failed for {}!".format(sigtag), color = "black", on_color="on_red"))
                    time.sleep(5)


                











# perl ${macroDir}/make_TRExNPfile.perl ${fitDir}/log_HTZT_minos.txt ${fitDir}/SPT_HTZT_TS_M16K050_MU0_ASIMOV/Fits/SPT_HTZT_TS_M16K050_MU0_ASIMOV.txt


    # for (mass, kappa, BRW) in product(*[masses, kappas, BRWs]):
    #     sigtag = getSigTag(mass, kappa, BRW)
    #     mktag = getMKTag(mass, kappa)
    #     ws_list = ""
    #     asimov_ws_list = ""
    #     do_asimov = True
    #     for anacode in ALL_ANACODES.keys():
    #         wsinfo = getScalingConfingXML(InFilePath =  "{}/{}_combined_{}.root".format(ALL_ANACODES[anacode]['InWSDir'], anacode, mktag),
    #                                       OutFilePath = "{}/{}_scaled_{}.root".format(ALL_ANACODES[anacode]['ScaledWSDir'], anacode, sigtag), 
    #                                       OutConfigPath = "{}/{}_scaling_{}.xml".format(ALL_ANACODES[anacode]['ScaledConfigDir'], anacode, sigtag), 
    #                                       AnaChannel = anacode,
    #                                       mass = mass, 
    #                                       kappa = kappa, 
    #                                       BRW = BRW, 
    #                                       WSName = ALL_ANACODES[anacode]['WSName'], 
    #                                       DataName="asimovData")
    #         if not wsinfo:
    #             print(colored("Scaling Config File Could not be Generated for " + anacode + " at M = {} and K = {}".format(mass, kappa), color = "black", on_color="on_red"))
    #             continue
    #         ws_list += wsinfo + '\n'
    #         if not scaleWS(ConfigName = "{}/{}_scaling_{}.xml".format(ALL_ANACODES[anacode]['ScaledConfigDir'], anacode, sigtag), LogFile="log_{}.txt".format(anacode)):
    #             print(colored("Scaling WS failed for " + anacode + " at M = {}, K= {}, and BRW = {}".format(mass, kappa, BRW), color = "black", on_color="on_red"))
    #             continue
    #         asimovwsinfo = getAsimovConfigXML(InFilePath = "{}/{}_scaled_{}.root".format(ALL_ANACODES[anacode]['ScaledWSDir'], anacode, sigtag), 
    #                                           OutFilePath = "{}/{}_MU0ASIMOV_{}.root".format(ALL_ANACODES[anacode]['ScaledWSDir'], anacode, sigtag),
    #                                           OutConfigPath = "{}/{}_MU0ASIMOV_{}.xml".format(ALL_ANACODES[anacode]['AsimovConfigDir'], anacode, sigtag),
    #                                           AnaChannel = anacode, 
    #                                           WSName = ALL_ANACODES[anacode]['WSName'])
    #         if not asimovwsinfo:
    #             print(colored("ASIMOV config failed for " + anacode + " at M = {}, K= {}, and BRW = {}".format(mass, kappa, BRW), color = "black", on_color="on_red"))
    #             continue
    #         else:
    #             _anachan, _configpath, _wsname, _dataname = asimovwsinfo
    #         if not getAsimovWS(_configpath, _wsname, _dataname, LogFile="log.txt"):
    #             print(colored("ASIMOV WS failed for " + anacode + " at M = {}, K= {}, and BRW = {}".format(mass, kappa, BRW), color = "black", on_color="on_red"))
    #             continue

    #     f = open("wsList.txt", "w")
    #     f.write(ws_list)
    #     f.close()
    #     print("WS List is available at " + colored('wsList.txt', color = "black", on_color="on_green"))
    #     CombConfig = getCombWS(WSListFile = "wsList.txt", sigtag=sigtag)
    #     if not CombConfig:
    #         print(colored("Generating Combination Config failed for M = {}, K= {}, and BRW = {}".format(mass, kappa, BRW), color = "black", on_color="on_red"))
    #         sys.exit(1)
    #     if not combineWS(CombConfig, LogFile="log_combine.txt"):
    #         print(colored("Combination failed for M = {}, K= {}, and BRW = {}".format(mass, kappa, BRW), color = "black", on_color="on_red"))
    #         sys.exit(1)

    #     asimovwsinfo = getAsimovConfigXML(InFilePath = "{}/data_devloc/workspaces/combined_workspaces/{}_combined.root".format(VLQCOMBDIR, sigtag),
    #                                       OutFilePath = "{}/data_devloc/workspaces/asimov_workspaces/SPT_COMBINED/{}_MU0ASIMOV_combined.root".format(VLQCOMBDIR, sigtag),
    #                                       OutConfigPath = "{}/data_devloc/xml/asimov/SPT_COMBINED/{}_MU0ASIMOV_COMBINED.xml".format(VLQCOMBDIR, sigtag),
    #                                       AnaChannel = 'SPT_COMBINED',
    #                                       WSName = 'combWS')
