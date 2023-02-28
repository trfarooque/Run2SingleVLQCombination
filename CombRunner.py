import sys, os
sys.path.append("VLQ_Interpretation_Tools")

from VLQCouplingCalculator import VLQCouplingCalculator as vlq
from VLQCrossSectionCalculator import *
from termcolor import colored
from CombUtils import *
from itertools import *
import time


if __name__ == "__main__":

    ## The following will be taken from CL Input
    do_Scaling = True
    do_Asimov = True
    do_Combine = True
    do_Separate_Fitting = True
    do_Combined_Fitting = True
    do_Separate_Limits = True
    do_Combined_Limits = True
    InDataName = 'asimovData'
    DataLoc = 'data_devloc'
    mu = 0.0


    masses = [1600.]
    kappas = [0.5]
    BRWs = [0.5]

    ALL_CFGs = {}

    for ana in ['SPT_OSML', 'SPT_HTZT']:
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
        for ana in ALL_CFGs.keys():
            cfg = ALL_CFGs[ana]
            if do_Scaling:
                scalingconfig = cfg.getScalingConfing(mass, kappa, brw, DataName=InDataName) ## CHECK: DataName needs to be a CL Input
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
                else:
                    print(colored("Getting Asimov Config with mu = {} could not be done for {} for {}!".format(mu, ana, sigtag), color = "black", on_color="on_red"))
                    time.sleep(5)
            if do_Separate_Fitting:
                # Will do Asimov Fitting if Asimov creation is asked
                fit = cfg.fitWS(mass, kappa, brw, mu=0, isAsimov=do_Asimov, LogFile="logFitting_{}_{}.txt".format(ana, sigtag)) 
                if not fit:
                    print(colored("Fitting WS could not be done for {} for {}!".format(ana, sigtag), color = "black", on_color="on_red"))
                    time.sleep(5)
                else:
                    print(colored("Fitting WS done for {} for {}!".format(ana, sigtag), color = "black", on_color="on_green"))
                    time.sleep(5)
            if do_Separate_Limits:
                limit = cfg.getLimits(mass, kappa, brw, mu=0, isAsimov=do_Asimov, LogFile="logLimits_{}_{}.txt".format(ana, sigtag))
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
            fit = combination_cfg.fitWS(mass, kappa, brw, mu, isAsimov=do_Asimov, LogFile="logFitting_{}_{}.txt".format(ana, sigtag))
            if not fit:
                print(colored("Fitting WS could not be done for SPT_COMBINED for {}!".format(sigtag), color = "black", on_color="on_red"))
                time.sleep(5)
            else:
                print(colored("Fitting WS done for SPT_COMBINED for {}!".format(sigtag), color = "black", on_color="on_green"))
                time.sleep(5)

        if do_Combined_Limits:
            limit = combination_cfg.getLimits(mass, kappa, brw, mu=0, isAsimov=do_Asimov, LogFile="logLimits_{}_{}.txt".format(ana, sigtag))
            if not limit:
                print(colored("Limits could not be done for SPT_COMBINED for {}!".format(sigtag), color = "black", on_color="on_red"))
                time.sleep(5)
                sys.exit(1)
            else:
                print(colored("Limit done for SPT_COMBINED for {}!".format(sigtag), color = "black", on_color="on_green"))
                time.sleep(5)














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
