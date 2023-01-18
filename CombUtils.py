import sys, os
sys.path.append("VLQ_Interpretation_Tools")

from VLQCouplingCalculator import VLQCouplingCalculator as vlq
from VLQCrossSectionCalculator import *
from termcolor import colored

############## GLOBAL VARIABLES ##################
ALL_ANACODES = {'SPT_OSML':   {'WSName':          'combWS',
                               'InWSDir':         '/afs/cern.ch/work/a/avroy/Run2SingleVLQCombination/data_devloc/workspaces/input_workspaces/SPT_OSML/',
                               'ScaledWSDir':     '/afs/cern.ch/work/a/avroy/Run2SingleVLQCombination/data_devloc/workspaces/scaled_workspaces/SPT_OSML/',
                               'ScaledConfigDir': '/afs/cern.ch/work/a/avroy/Run2SingleVLQCombination/data_devloc/xml/scaling/SPT_OSML/'  },
                'SPT_HTZT':   {'WSName':          'combined',
                               'InWSDir':         '/afs/cern.ch/work/a/avroy/Run2SingleVLQCombination/data_devloc/workspaces/input_workspaces/SPT_HTZT/',
                               'ScaledWSDir':     '/afs/cern.ch/work/a/avroy/Run2SingleVLQCombination/data_devloc/workspaces/scaled_workspaces/SPT_HTZT/',
                               'ScaledConfigDir': '/afs/cern.ch/work/a/avroy/Run2SingleVLQCombination/data_devloc/xml/scaling/SPT_HTZT/'  },
                # 'SPT_MONOTOP':{'WSName':          'combined',
                #                'InWSDir':         '/afs/cern.ch/work/a/avroy/Run2SingleVLQCombination/data_devloc/workspaces/input_workspaces/SPT_MONOTOP/',
                #                'ScaledWSDir':     '/afs/cern.ch/work/a/avroy/Run2SingleVLQCombination/data_devloc/workspaces/scaled_workspaces/SPT_MONOTOP/',
                #                'ScaledConfigDir': '/afs/cern.ch/work/a/avroy/Run2SingleVLQCombination/data_devloc/xml/scaling/SPT_MONOTOP/'  }
            }

VLQCOMBDIR = os.getcwd()
##################################################


def getSigTag(mass, kappa, BRW):
    return "M{:02d}K{:03d}BRW{:02d}".format(int(mass/100), int(kappa*100), int(BRW*100))

def getMKTag(mass, kappa):
    return "M{:02d}K{:03d}".format(int(mass/100), int(kappa*100))


def getSF(mass, kappa, BRW, all_modes = ['WTZt', 'WTHt', 'ZTZt', 'ZTHt']):
    c = vlq(mass, 'T')
    c.setKappaxi(kappa, BRW, (1-BRW)/2.0)
    GM = c.getGamma()/mass
    cw, cz, _, _ = c.getc_Vals()
    XSvals = []
    XSsum = 0.
    for mode in all_modes:
        this_xs = XS_NWA(mass, cw if mode[0] == 'W' else cz, mode = mode[0:2]) * (BRW if mode[2] == 'W' else (1-BRW)/2.) * \
                  FtFactor(proc=mode, mass=mass, GM=GM)/PNWA(proc=mode, mass=mass, GM=GM)
        XSsum += this_xs
        XSvals.append(this_xs)
    for ii in range(len(XSvals)):
        XSvals[ii] = XSvals[ii]/XSsum
    return XSvals


def getScalingConfingXML(InFilePath, OutFilePath, OutConfigPath, AnaChannel, 
                         mass, kappa, BRW, WSName= "combined", DataName="asimovData"):
    if AnaChannel not in ['SPT_ALLHAD', 'SPT_HTZT', 'SPT_OSML', 'SPT_TYWB', 'SPT_MONOTOP']:
        print(colored("Invalid Analysis Channel!", color = "black", on_color="on_red"))
        return False
    if not os.path.exists(InFilePath):
        print(colored("Input WS {} not found!".format(InFilePath), color = "black", on_color="on_red"))
        return False
    if not os.path.exists('/'.join(OutFilePath.split('/')[:-1])):
        print(colored("Output WS directory {} not found!".format('/'.join(OutFilePath.split('/')[:-1])), color = "black", on_color="on_red"))
        return False
    if not os.path.exists('/'.join(OutConfigPath.split('/')[:-1])):
        print(colored("Output directory for config {} not found!".format('/'.join(OutConfigPath.split('/')[:-1])), color = "black", on_color="on_red"))
        return False
    sigtag = getSigTag(mass, kappa, BRW)
    sfWTZt, sfWTHt, sfZTZt, sfZTHt = getSF(mass, kappa, BRW, all_modes = ['WTZt', 'WTHt', 'ZTZt', 'ZTHt'])
    str_to_print = '''
<!DOCTYPE Organization  SYSTEM 'Organization.dtd'>
<Organization
    InFile="{}"'''.format(InFilePath) + '''
    OutFile="{}"'''.format(OutFilePath) + '''
        ModelName="{}_{}"'''.format(AnaChannel, sigtag) + '''
        POINames="mu_signal"
        WorkspaceName="{}"'''.format(WSName) + '''
        ModelConfigName="ModelConfig"
        DataName="{}"'''.format(DataName) + '''
        >
  <Item Name="sc_TS_WTZt[{}]"/>
  <Item Name="sc_TS_WTHt[{}]"/>
  <Item Name="sc_TS_ZTZt[{}]"/>
  <Item Name="sc_TS_ZTHt[{}]"/>'''.format(sfWTZt, sfWTHt, sfZTZt, sfZTHt) + '''
  <Item Name="mu_signal[1,-100,100]"/>

  <Item Name="expr::mu_sc_TS_WTZt('@0*@1', sc_TS_WTZt, mu_signal)" />
  <Item Name="expr::mu_sc_TS_WTHt('@0*@1', sc_TS_WTHt, mu_signal)" />
  <Item Name="expr::mu_sc_TS_ZTZt('@0*@1', sc_TS_ZTZt, mu_signal)" />
  <Item Name="expr::mu_sc_TS_ZTHt('@0*@1', sc_TS_ZTHt, mu_signal)" />
  <Map Name="EDIT::NEWPDF(OLDPDF,                                                                                                                                           
             mu_WTZt=mu_sc_TS_WTZt,                                                                                                                                         
             mu_WTHt=mu_sc_TS_WTHt,                                                                                                                                         
             mu_ZTZt=mu_sc_TS_ZTZt,                                                                                                                                         
             mu_ZTHt=mu_sc_TS_ZTHt)" />
</Organization>
'''

    f = open(OutConfigPath, 'w')
    f.write(str_to_print)
    f.close()
    print("Config written to {}".format(colored(OutConfigPath, color = "black", on_color="on_green")))
    return "{}  :  {}  :  {}".format(AnaChannel, OutFilePath, WSName)
    

def ScaleWS(ConfigName, LogFile="log.txt"):
    os.system("cp templates/Organization.dtd {}".format('/'.join(ConfigName.split('/')[:-1])))
    code = os.system('manager -w edit -x {} 2>&1 |tee {}'.format(ConfigName, LogFile))
    return True if code == 0 else False
    

def GetCombWS(WSListFile, sigtag):
    cmd = '''{0}/WorkspaceChecks/bin/workspace.exe \
file_path={1} \
data_name="asimovData" \
output_xml_folder={0}/data_devloc/xml/combination/ \
output_ws_folder={0}/data_devloc/workspaces/combined_workspaces/ \
output_ws_name={2}_combined.root \
do_config_dump=TRUE \
do_checks=FALSE \
abort_on_error=FALSE '''.format(VLQCOMBDIR, WSListFile, sigtag)
    # print(cmd)
    code = os.system(cmd)
    return True if code == 0 else False


if __name__ == "__main__":
    mass = 1600.
    kappa = 0.5
    BRW = 0.5 # singlet
    # print(getSF(mass=mass, kappa=kappa, BRW=BRW))
    sigtag = getSigTag(mass, kappa, BRW)
    mktag = getMKTag(mass, kappa)
    ws_list = ""
    for anacode in ALL_ANACODES.keys():
        wsinfo = getScalingConfingXML(InFilePath =  "{}/{}_combined_{}.root".format(ALL_ANACODES[anacode]['InWSDir'], anacode, mktag),
                                      OutFilePath = "{}/{}_combined_{}.root".format(ALL_ANACODES[anacode]['ScaledWSDir'], anacode, sigtag), 
                                      OutConfigPath = "{}/{}_scaling_{}.xml".format(ALL_ANACODES[anacode]['ScaledConfigDir'], anacode, sigtag), 
                                      AnaChannel = anacode,
                                      mass = mass, 
                                      kappa = kappa, 
                                      BRW = BRW, 
                                      WSName = ALL_ANACODES[anacode]['WSName'], 
                                      DataName="asimovData")
        if not wsinfo:
            print(colored("Scaling Config File Could not be Generated for " + anacode + " at M = {} and K = {}".format(mass, kappa), color = "black", on_color="on_red"))
            continue
        ws_list += wsinfo + '\n'
        if not ScaleWS(ConfigName = "{}/{}_scaling_{}.xml".format(ALL_ANACODES[anacode]['ScaledConfigDir'], anacode, sigtag), LogFile="log_{}.txt".format(anacode)):
            print(colored("Scaling WS failed for " + anacode + " at M = {}, K= {}, and BRW = {}".format(mass, kappa, BRW), color = "black", on_color="on_red"))
    f = open("wsList.txt", "w")
    f.write(ws_list)
    f.close()
    print("WS List is available at " + colored('wsList.txt', color = "black", on_color="on_green"))
    GetCombWS(WSListFile = "wsList.txt", sigtag=sigtag)
