import sys, os
sys.path.append("VLQ_Interpretation_Tools")

from VLQCouplingCalculator import VLQCouplingCalculator as vlq
from VLQCrossSectionCalculator import *
from termcolor import colored
from CombUtils import *
from itertools import *
masses = [1600.]
kappas = [0.5]
BRWs = [0.5]
do_Asimov = True
ALL_CFGs = {}

for ana in ['SPT_OSML', 'SPT_HTZT']:
    print("Creating CombinationConfig for {}".format(ana))
    ALL_CFGs[ana]  = VLQCombinationConfig(AnaCode = ana, 
                                          DataFolder = 'data_devloc', ## CHECK: Location of data needs to be a CL Input
                                          WSName = 'combWS' if ana == 'SPT_OSML' else 'combined',
                                          makePaths = True)

print("Creating CombinationConfig for SPT_COMBINED")
combination_cfg = VLQCombinationConfig(AnaCode = 'SPT_COMBINED',
                                          DataFolder = 'data_devloc', ## CHECK: Location of data needs to be a CL Input                                                     
                                          WSName = 'combWS',
                                          makePaths = True)

for (mass, kappa, brw) in product(*[masses, kappas, BRWs]):
    sigtag = getSigTag(mass, kappa, brw)
    mktag = getMKTag(mass, kappa)
    ws_list = ""
    for ana in ALL_CFGs.keys():
        cfg = ALL_CFGs[ana]
        scalingconfig = cfg.getScalingConfing(mass, kappa, brw, DataName="asimovData") ## CHECK: DataName needs to be a CL Input
        if not scalingconfig:
            print(colored("Scaling config could not be created for {} for {}!".format(ana, sigtag), color = "black", on_color="on_red"))
            continue
        scaling = cfg.scaleWS(mass, kappa, brw, LogFile="logScaling_{}_{}.txt".format(ana, sigtag))
        if not scaling:
            print(colored("Scaled WS could not be created for {} for {}!".format(ana, sigtag), color = "black", on_color="on_red"))
            continue
        ws_list += '{}  :  {}  :  {}\n'.format(ana, cfg.getScaledWSPath(mass, kappa, brw), cfg.WSName)
        if do_Asimov:
            asimovconfig = cfg.getAsimovConfig(mass, kappa, brw)
            if asimovconfig:
                asimov = cfg.getAsimovWS(mass, kappa, brw, DataName='asimovData', LogFile="logAsimov_{}_{}.txt".format(ana,sigtag))

    f = open("wsList.txt", "w") ## CHECK: this filename should be a CL Input
    f.write(ws_list)
    f.close()
    print("WS List is available at " + colored('wsList.txt', color = "black", on_color="on_green"))
    
    
    CombConfig = combination_cfg.getCombinationConfig(WSListFile = "wsList.txt", 
                                                      mass= mass,
                                                      kappa = kappa,
                                                      brw = brw,
                                                      DataName = 'asimovData')

    if not CombConfig:
        print(colored("Generating Combination Config failed for M = {}, K= {}, and BRW = {}".format(mass, kappa, BRW), color = "black", on_color="on_red"))
        continue
    combined = combination_cfg.combineWS(mass, kappa, brw, LogFile="log_combine_{}.txt".format(sigtag))
    if not combined:
        print(colored("Combination failed for M = {}, K= {}, and BRW = {}".format(mass, kappa, BRW), color = "black", on_color="on_red"))
        continue

    if do_Asimov:
        asimovconfig = combination_cfg.getAsimovConfig(mass, kappa, brw)
        if asimovconfig:
            asimov = combination_cfg.getAsimovWS(mass, kappa, brw, DataName='obsData', LogFile="logAsimov_{}_{}.txt".format(ana,sigtag))



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
