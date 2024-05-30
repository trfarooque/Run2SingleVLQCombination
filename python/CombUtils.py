import sys, os
from termcolor import colored
from VLQCouplingCalculator import VLQCouplingCalculator as vlq
from VLQCrossSectionCalculator import *
import ROOT
#from ROOT import *

ALL_ANACODES = ['SPT_OSML', 'SPT_HTZT', 'SPT_MONOTOP', 'SPT_ALLHAD', 'SPT_TYWB', 'SPT_COMBINED']
#INPUTDIR=os.getcwd()

def getSigTag(mass, kappa, brw):
    return "M{:02d}K{:03d}BRW{:02d}".format(int(mass/100), int(kappa*100), int(brw*100))

def getMKTag(mass, kappa):
    return "M{:02d}K{:03d}".format(int(mass/100), int(kappa*100))

def getmuScale(mass, kappa, brw, all_modes = ['WTZt', 'WTHt', 'ZTZt', 'ZTHt']):
    c = vlq(mass, 'T')
    c.setKappaxi(kappa, brw, (1-brw)/2.0)
    GM = c.getGamma()/mass
    BRs = c.getBRs()
    cw, cz, _, _ = c.getc_Vals()
    XSsum = 0.
    for mode in all_modes:
        this_xs = XS_NWA(mass, cw if mode[0] == 'W' else cz, mode = mode[0:2]) * \
                  (BRs[0] if mode[2] == 'W' else (BRs[1] if mode[2] == 'Z' else BRs[2]) ) * \
                  FtFactor(proc=mode, mass=mass, GM=GM, useAverageXS=True)[0]/PNWA(proc=mode, mass=mass, GM=GM)
        XSsum += this_xs
    return XSsum/0.1

def getWidth(mass, kappa, brw):
    c = vlq(mass, 'T')
    c.setKappaxi(kappa, brw, (1-brw)/2.0)
    GM = c.getGamma()/mass

    return GM


def getSF(mass, kappa, brw, all_modes = ['WTZt', 'WTHt', 'ZTZt', 'ZTHt']):
    c = vlq(mass, 'T')
    c.setKappaxi(kappa, brw, (1-brw)/2.0)
    GM = c.getGamma()/mass
    BRs = c.getBRs()
    cw, cz, _, _ = c.getc_Vals()
    XSvals = []
    XSsum = 0.
    for mode in all_modes:
        this_xs = XS_NWA(mass, cw if mode[0] == 'W' else cz, mode = mode[0:2]) * \
                  (BRs[0] if mode[2] == 'W' else (BRs[1] if mode[2] == 'Z' else BRs[2]) ) * \
                  FtFactor(proc=mode, mass=mass, GM=GM, useAverageXS=True)[0]/PNWA(proc=mode, mass=mass, GM=GM)
        XSsum += this_xs
        XSvals.append(this_xs)
    for ii in range(len(XSvals)):
        XSvals[ii] = XSvals[ii]/XSsum
    return XSvals


class VLQCombinationConfig:
    def __init__(self, AnaCode, DataFolder = 'data', WSName = 'combined', InputDir = os.getcwd(), makePaths = False, checkPaths = False):
        if AnaCode not in ALL_ANACODES:
            raise Exception("Unknown Analysis Code!")
        else:
            self.AnaCode = AnaCode
        self.isCombined = True if self.AnaCode == 'SPT_COMBINED' else False

        self.InputDir = InputDir
        self.DataFolder = DataFolder
        self.WSName = WSName
        
        self.InWSSubDir = 'workspaces/input_workspaces'
        self.ScaledWSSubDir = 'workspaces/scaled_workspaces'
        self.ScalingConfigSubDir = 'xml/scaling'
        self.AsimovWSSubDir = 'workspaces/asimov_workspaces'
        self.AsimovConfigSubDir = 'xml/asimov'
        self.CombinedWSSubDir = 'workspaces/combined_workspaces'
        self.CombinationConfigSubDir = 'xml/combination'
        self.FittedWSSubDir = 'workspaces/fitted_workspaces'
        self.LimitSubDir = 'limits'
        self.LogSubDir = 'logs'
        self.RankingSubDir = 'ranking'
        
        self.setPaths()
        
        if makePaths:
            self.makePaths()

        if checkPaths:
            if not self.checkPaths():
                raise Exception()

    def setPaths(self):
        self.InWSDir = self.InputDir + self.DataFolder + '/' + self.InWSSubDir + '/' +  self.AnaCode + '/'
        self.ScaledWSDir = self.InputDir + self.DataFolder + '/' + self.ScaledWSSubDir + '/' + self.AnaCode + '/'
        self.ScalingConfigDir = self.InputDir + self.DataFolder + '/' + self.ScalingConfigSubDir  + '/' + self.AnaCode + '/'
        self.AsimovWSDir = self.InputDir + self.DataFolder + '/' + self.AsimovWSSubDir + '/' + self.AnaCode + '/'
        self.AsimovConfigDir = self.InputDir + self.DataFolder + '/' + self.AsimovConfigSubDir  + '/' + self.AnaCode + '/'
        self.CombinedWSDir = self.InputDir + self.DataFolder + '/' + self.CombinedWSSubDir + '/' + self.AnaCode + '/'
        self.CombinationConfigDir = self.InputDir + self.DataFolder + '/' + self.CombinationConfigSubDir  + '/' + self.AnaCode + '/'
        self.FittedWSDir = self.InputDir + self.DataFolder + '/' + self.FittedWSSubDir + '/' + self.AnaCode + '/'
        self.LimitDir = self.InputDir + self.DataFolder + '/' + self.LimitSubDir  + '/' + self.AnaCode + '/'
        self.LogDir = self.InputDir + self.DataFolder + '/' + self.LogSubDir  + '/' + self.AnaCode + '/'
        self.RankingDir = self.InputDir + self.DataFolder + '/' + self.RankingSubDir  + '/' + self.AnaCode + '/'
        '''
        print('InWSDir : '+self.InWSDir)
        print('ScaledWSDir : '+self.ScaledWSDir)
        print('ScalingConfigDir : '+self.ScalingConfigDir)

        print('AsimovWSDir : '+self.AsimovWSDir)
        print('AsimovConfigDir : '+self.AsimovConfigDir)
        print('CombinedWSDir : '+self.CombinedWSDir)
        print('CombinationConfigDir : '+self.CombinationConfigDir)

        print('FittedWSDir : '+self.FittedWSDir)
        print('LimitDir : '+self.LimitDir)
        print('LogDir : '+self.LogDir)
        print('RankingDir : '+self.RankingDir)
        '''

    def makePaths(self):
        mkdir = "mkdir -p {}"
        if not self.isCombined:
            os.system(mkdir.format(self.InWSDir))
            os.system(mkdir.format(self.ScaledWSDir))
            os.system(mkdir.format(self.ScalingConfigDir))
        os.system(mkdir.format(self.AsimovWSDir))
        os.system(mkdir.format(self.AsimovConfigDir))
        os.system(mkdir.format(self.CombinedWSDir))
        os.system(mkdir.format(self.CombinationConfigDir))
        os.system(mkdir.format(self.FittedWSDir))
        os.system(mkdir.format(self.LimitDir))
        os.system(mkdir.format(self.LogDir))
        os.system(mkdir.format(self.RankingDir))

    def setSubDir(self, pathdict, makePaths=False):
        for pathname, path in pathdict.items():
            try:
                oldpath = getattr(self, pathname)
            except:
                print(colored("The variable '{}' is  not defined for the VLQCombinationConfig class".format(pathname), color = "black", on_color="on_light_yellow"))
                continue
            setattr(self, pathname, path)
            if path != oldpath:
                print(colored("The  variable '{}' has been changed from '{}' to '{}'".format(pathname, oldpath, path), color = "black", on_color="on_green"))

        self.setPaths()
        if makePaths:
            self.makePaths()


    def checkPaths(self):
        if not (os.path.exists(self.InWSDir) or self.isCombined):
            print(colored("Input WS {} not found!".format(self.InWSDir), color = "black", on_color="on_red"))
            return False
        if not (os.path.exists(self.ScaledWSDir) or self.isCombined):
            print(colored("Scaled WS directory {} not found!".format(self.ScaledWSDir), color = "black", on_color="on_red"))
            return False
        if not (os.path.exists(self.ScalingConfigDir) or self.isCombined):
            print(colored("Directory for scaling config {} not found!".format(self.ScalingConfigDir), color = "black", on_color="on_red"))
            return False
        if not os.path.exists(self.AsimovWSDir):
            print(colored("Asimov WS directory {} not found!".format(self.AsimovWSDir), color = "black", on_color="on_red"))
            return False
        if not os.path.exists(self.AsimovConfigDir):
            print(colored("Directory for Asimov config {} not found!".format(self.AsimovConfigDir), color = "black", on_color="on_red"))
            return False
        if not os.path.exists(self.CombinedWSDir):
            print(colored("Combined WS directory {} not found!".format(self.CombinedWSDir), color = "black", on_color="on_red"))
            return False
        if not os.path.exists(self.CombinationConfigDir):
            print(colored("Directory for Asimov config {} not found!".format(self.CombinationConfigDir), color = "black", on_color="on_red"))
            return False
        if not os.path.exists(self.FittedWSDir):
            print(colored("Fitted WS directory {} not found!".format(self.FittedWSDir), color = "black", on_color="on_red"))
            return False
        if not os.path.exists(self.LimitDir):
            print(colored("Limits directory {} not found!".format(self.LimitDir), color = "black", on_color="on_red"))
            return False
        if not os.path.exists(self.LogDir):
            print(colored("Log directory {} not found!".format(self.LogDir), color = "black", on_color="on_red"))
            return False
        if not os.path.exists(self.RankingDir):
            print(colored("Ranking fit directory {} not found!".format(self.RankingDir), color = "black", on_color="on_red"))
            return False
        
        return True

    def getInputWSPath(self, mass, kappa, brw):
        sigtag = getSigTag(mass, kappa, brw)
        mktag = getMKTag(mass, kappa)
        return "{}/{}_combined_{}.root".format(self.InWSDir, self.AnaCode, mktag)

    def getScaledWSPath(self, mass, kappa, brw, datatag):
        sigtag = getSigTag(mass, kappa, brw)
        mktag = getMKTag(mass, kappa)
        return "{}/{}_scaled_{}_{}.root".format(self.ScaledWSDir, self.AnaCode, sigtag, datatag)
        
    def getScalingConfigPath(self, mass, kappa, brw, datatag):
        sigtag = getSigTag(mass, kappa, brw)
        mktag = getMKTag(mass, kappa)
        return "{}/{}_scaling_{}_{}.xml".format(self.ScalingConfigDir, self.AnaCode, sigtag, datatag)

    def getScalingConfig(self, mass, kappa, brw, datatag):
        InFilePath = self.getInputWSPath(mass, kappa, brw)
        if not os.path.exists(InFilePath):
            print(colored("Input WS {} not found!".format(InFilePath), color = "black", on_color="on_red"))
            return False
        DataName = "obsData" if datatag == "data" else "asimovData"
        OutFilePath = self.getScaledWSPath(mass, kappa, brw, datatag)
        OutConfigPath = self.getScalingConfigPath(mass, kappa, brw, datatag)

        sigtag = getSigTag(mass, kappa, brw)
        AnaChannel = self.AnaCode
        WSName = self.WSName

        sfWTZt, sfWTHt, sfZTZt, sfZTHt = getSF(mass, kappa, brw, all_modes = ['WTZt', 'WTHt', 'ZTZt', 'ZTHt'])

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
        print("Config written to {}".format(colored(OutConfigPath, color = "green")))
        return True

    def scaleWS(self, mass, kappa, brw, datatag, LogFile="log.txt"):
        sigtag = getSigTag(mass, kappa, brw)
        ConfigName = self.getScalingConfigPath(mass, kappa, brw, datatag)
        if not os.path.exists(ConfigName):
            return False
        print(colored("cp {}/dtd/Organization.dtd {}".format(os.getenv('VLQCOMBDIR'),self.ScalingConfigDir), color = "black", on_color="on_yellow"))
        os.system("cp {}/dtd/Organization.dtd {}".format(os.getenv('VLQCOMBDIR'),self.ScalingConfigDir))
        print(colored("manager -w edit -x {} > {} 2>&1".format(ConfigName, LogFile), color = "black", on_color="on_yellow"))
        code = os.system('manager -w edit -x {} > {} 2>&1'.format(ConfigName, LogFile))
        if code == 0:
            print("Workspace scaling done for {}".format(colored(sigtag, color = "green")))
        else:
            print(colored("Workspace scaling failed for {}. Check Log: {}".format(sigtag, LogFile), color = "black", on_color="on_red"))
        return True if code == 0 else False    

    def getCombinationConfigPath(self, mass, kappa, brw, datatag):
        sigtag = getSigTag(mass, kappa, brw)
        mktag = getMKTag(mass, kappa)
        return "{}/{}_combination_{}_{}.xml".format(self.CombinationConfigDir, self.AnaCode, sigtag, datatag)

    def getCombinedWSPath(self, mass, kappa, brw, datatag):
        sigtag = getSigTag(mass, kappa, brw)
        mktag = getMKTag(mass, kappa)
        return "{}/{}_combined_{}_{}.root".format(self.CombinedWSDir, self.AnaCode, sigtag, datatag)

    def getCombinationConfig(self, WSListFile, mass, kappa, brw, mu = 0.0, DataName = 'asimovData'):
        
        if not os.path.exists(WSListFile):
            return False
        sigtag = getSigTag(mass, kappa, brw)
        mktag = getMKTag(mass, kappa)
        datatag = "data" if 'asimov' not in DataName else "asimov_mu{}".format(int(mu*100))
        cmd = '''workspace \
        file_path={0} \
        data_name="{1}" \
        output_xml_folder={2} \
        output_xml_name={3} \
        output_ws_folder={4} \
        output_ws_name={5} \
        do_config_dump=TRUE \
        do_checks=FALSE \
        abort_on_error=FALSE '''.format(WSListFile, 
                                        DataName, 
                                        self.CombinationConfigDir,
                                        self.getCombinationConfigPath(mass, kappa, brw, datatag).split('/')[-1],
                                        self.CombinedWSDir,
                                        self.getCombinedWSPath(mass, kappa, brw, datatag).split('/')[-1])
        
        print(colored(cmd, color = "black", on_color="on_yellow"))
        code = os.system(cmd)
        return True if code == 0 else None


    def combineWS(self, mass, kappa, brw, datatag, LogFile="log_combine.txt"):
        ConfigName = self.getCombinationConfigPath(mass, kappa, brw, datatag)
        if not os.path.exists(ConfigName):
            return False
        print(colored("cp {}/dtd/Combination.dtd {}".format(os.getenv('VLQCOMBDIR'),self.CombinationConfigDir), color = "black", on_color="on_yellow"))
        os.system("cp {}/dtd/Combination.dtd {}".format(os.getenv('VLQCOMBDIR'),self.CombinationConfigDir))
        print(colored("manager -w combine -x {} > {} 2>&1".format(ConfigName, LogFile), color = "black", on_color="on_yellow"))
        code = os.system("manager -w combine -x {} > {} 2>&1".format(ConfigName, LogFile))
        return True if code == 0 else False

    def getAsimovWSPath(self, mass, kappa, brw, mu=0):
        sigtag = getSigTag(mass, kappa, brw)
        mktag = getMKTag(mass, kappa)
        return "{}/{}_asimov_mu{}_{}.root".format(self.AsimovWSDir, self.AnaCode, int(mu*100), sigtag)
        
    def getAsimovConfigPath(self, mass, kappa, brw, mu=0):
        sigtag = getSigTag(mass, kappa, brw)
        mktag = getMKTag(mass, kappa)
        return "{}/{}_asimov_mu{}_{}.xml".format(self.AsimovConfigDir, self.AnaCode, int(mu*100), sigtag)

    def getAsimovConfig(self, mass, kappa, brw, mu=0):
        datatag = 'asimov_mu{}'.format(int(mu*100))
        if self.isCombined:
            InFilePath = self.getCombinedWSPath(mass, kappa, brw, datatag)
        else:
            InFilePath = self.getScaledWSPath(mass, kappa, brw, datatag)
        
        if not os.path.exists(InFilePath):
            return False

        OutFilePath = self.getAsimovWSPath(mass, kappa, brw, mu)
        OutConfigPath = self.getAsimovConfigPath(mass, kappa, brw, mu)
        str_to_print='''<!DOCTYPE Asimov  SYSTEM 'asimovUtil.dtd'>  
    <Asimov 
        InputFile="{}" 
        OutputFile="{}"
        POI="mu_signal" 
        >
      <Action Name="Prepare" Setup="" Action="nominalNuis:nominalGlobs"/>
      <Action Name="asimovData_mu{}" Setup="mu_signal={}" Action="genasimov:nominalGlobs"/>
    </Asimov>'''.format(InFilePath, OutFilePath, int(mu*100), mu)
        f = open(OutConfigPath, 'w')
        f.write(str_to_print)
        f.close()
        return True

    def getAsimovWS(self, mass, kappa, brw, mu=0, LogFile="log.txt"):
        ConfigName = self.getAsimovConfigPath(mass, kappa, brw, mu)
        DataName = 'asimovData' if not self.isCombined else 'combData'
        if not os.path.exists(ConfigName):
            return False
        print(colored("cp {}/dtd/asimovUtil.dtd {}".format(os.getenv('VLQCOMBDIR'),self.AsimovConfigDir), color = "black", on_color="on_yellow"))
        os.system("cp {}/dtd/asimovUtil.dtd {}".format(os.getenv('VLQCOMBDIR'),self.AsimovConfigDir))
        print(colored("quickAsimov -x {} -w {} -m ModelConfig -d {} > {} 2>&1".format(ConfigName, self.WSName, DataName, LogFile), color = "black", on_color="on_yellow"))
        code = os.system('quickAsimov -x {} -w {} -m ModelConfig -d {} > {} 2>&1'.format(ConfigName, self.WSName, DataName, LogFile))
        return True if code == 0 else False


    def getFittedResultPath(self, mass, kappa, brw, mu=0, fittype='BONLY', isAsimov=True):
        sigtag = getSigTag(mass, kappa, brw)
        mktag = getMKTag(mass, kappa)
        datatag = "data" if not isAsimov else "asimov_mu{}".format(int(mu*100))
        return "{}/{}_fitted_{}_{}_{}.root".format(self.FittedWSDir, self.AnaCode, sigtag, datatag, fittype)
        
 
    def fitWS(self, mass, kappa, brw, mu=0,  fittype='BONLY', isAsimov=True, LogFile="log.txt"):
        DSName = "asimovData_mu{}".format(int(mu*100)) if isAsimov else ("obsData" if not self.isCombined else "combData")
        datatag = "data" if not isAsimov else "asimov_mu{}".format(int(mu*100))
        InWSPath = self.getAsimovWSPath(mass, kappa, brw, mu) if isAsimov \
                   else (self.getCombinedWSPath(mass, kappa, brw, datatag) if self.isCombined \
                         else self.getScaledWSPath(mass, kappa, brw, datatag))
        fitarg = ' '
        if isAsimov:
            fitarg = '-p mu_signal={} '.format(mu) if fittype == 'BONLY' else '-p mu_signal '
        else:
            fitarg = '-p mu_signal=0 ' if fittype == 'BONLY' else '-p mu_signal '
        cmd = '''quickFit -w {} -f {} -d {}  -o {} \
--savefitresult 1 --hesse 1 --minos 1 {} > {} 2>&1 '''.format(self.WSName,
                                                                InWSPath,
                                                                DSName,
                                                                self.getFittedResultPath(mass, kappa, brw, mu, fittype, isAsimov), 
                                                                fitarg,
                                                                LogFile)
        print(colored(cmd, color = "black", on_color="on_yellow"))
        code = os.system(cmd)
        return True if code == 0 else False

    def getLimitsPath(self, mass, kappa, brw, mu=0, isAsimov=True):
        sigtag = getSigTag(mass, kappa, brw)
        mktag = getMKTag(mass, kappa)
        datatag = "data" if not isAsimov else "asimov_mu{}".format(int(mu*100))
        return "{}/{}_limits_{}_{}.root".format(self.LimitDir, self.AnaCode, sigtag, datatag)


    def getLimits(self, mass, kappa, brw, mu=0, isAsimov=True, LogFile="log.txt"):
        DSName = "asimovData_mu{}".format(int(mu*100)) if isAsimov else ("obsData" if not self.isCombined else "combData")
        datatag = "data" if not isAsimov else "asimov_mu{}".format(int(mu*100))
        InWSPath = self.getAsimovWSPath(mass, kappa, brw, mu) if isAsimov \
                   else (self.getCombinedWSPath(mass, kappa, brw, datatag) if self.isCombined \
                         else self.getScaledWSPath(mass, kappa, brw, datatag))
        cmd = '''quickLimit -w {} -f {} -d {} -p mu_signal \
-o {} 2>&1 |tee {}'''.format(self.WSName,
                             InWSPath,
                             DSName,
                             self.getLimitsPath(mass, kappa, brw, mu, isAsimov),
                             LogFile)

        print(colored(cmd, color = "black", on_color="on_yellow"))
        code = os.system(cmd)
        return True if code == 0 else False

    def getRankingPath(self, mass, kappa, brw, mu=0, isAsimov=True):

        DSName = "asimovData_mu{}".format(int(mu*100)) if isAsimov else ("obsData" if not self.isCombined else "combData")
        datatag = "data" if not isAsimov else "asimov_mu{}".format(int(mu*100))
        InWSPath = self.getAsimovWSPath(mass, kappa, brw, mu) if isAsimov \
                   else (self.getCombinedWSPath(mass, kappa, brw, datatag) if self.isCombined \
                         else self.getScaledWSPath(mass, kappa, brw, datatag))
    
        sigtag = getSigTag(mass, kappa, brw)
        mktag = getMKTag(mass, kappa)
        datatag = "data" if not isAsimov else "asimov_mu{}".format(int(mu*100))
        return "{}/{}_{}_{}/".format(self.RankingDir, self.AnaCode, sigtag, datatag)


def getTRExFConfigs(ConfDir, WSListFile, sigtag, mu=0, fittype="BONLY", isAsimov= True):
    if not os.path.exists(WSListFile):
        return False
    DSName = "asimovData_mu{}".format(int(mu*100)) if isAsimov else "obsData" 
    datatag = "data" if not isAsimov else "asimov_mu{}".format(int(mu*100))
    cmd = '''workspace \
file_path={} \
output_trexf_folder={} \
output_tag={} \
do_trexf_dump=TRUE do_checks=FALSE abort_on_error=FALSE \
data_name="{}" \
fittype={}
'''.format(WSListFile, ConfDir,
           sigtag + "_" + datatag + "_" + fittype,
           DSName,
           fittype)
    print(colored(cmd, color = "black", on_color="on_yellow"))
    code = os.system(cmd)
    return True if code == 0 else False

def getTRExFFitFile(in_fname, out_fname, fromLog=True):

    print("in:"+in_fname)
    print("out:"+out_fname)
    if not os.path.exists(in_fname):
        return False
    if not os.path.exists('/'.join(out_fname.split('/')[:-1])):
        return False

    return (getTRExFFitFileFromLog(in_fname, out_fname) if fromLog else getTRExFFitFileFromRoot(in_fname, out_fname))

def change_JER_name(param_name, fname):
    if 'SPT_MONOTOP' in fname: channel = 'SPT_MONOTOP'
    elif 'SPT_HTZT' in fname: channel = 'SPT_HTZT'
    elif 'SPT_OSML' in fname: channel = 'SPT_OSML'
    else:
        return param_name

    new_name = param_name
    if channel == 'SPT_MONOTOP':
        new_name = param_name.replace("JET_JER_EffectiveNP","JET_FullJER_EffectiveNP").replace("JET_JER_DataVsMC_MC16","JET_FullJER_DataVsMC_MC16")
    elif channel == 'SPT_HTZT' or channel == 'SPT_OSML':
        new_name = param_name.replace("JET_JER_EffectiveNP","JET_SimpleJER_EffectiveNP").replace("JET_JER_DataVsMC_MC16","JET_SimpleJER_DataVsMC_MC16")
    return new_name


def getTRExFFitFileFromRoot(in_fname, out_fname):

    #extract the list of nuisance parameters and signal strength; also extract correlation matrix
    #safer than parsing log file, because we can reliably get the final values of 
    infile = ROOT.TFile(in_fname)
    fitResult = infile.Get("fitResult")
    if not(fitResult):
        return False

    outfile = open(out_fname, 'w')
    outfile.write('NUISANCE_PARAMETERS\n')
    for par in fitResult.floatParsFinal():
        modified_name = change_JER_name(par.GetName(), out_fname)
        line = "{}  {:g} {:+.6f} {:+.6f}\n"\
            .format(modified_name.replace('alpha_',''),par.getValV(),par.getErrorHi(),par.getErrorLo())
        outfile.write(line)

    outfile.write('\n\nCORRELATION_MATRIX\n')
    corrMatrix = fitResult.correlationHist()
    outfile.write("{:d}   {:d}\n".format(corrMatrix.GetNbinsX(),corrMatrix.GetNbinsY()))
    for i in range(1,corrMatrix.GetNbinsX()+1):
        for j in range(1,corrMatrix.GetNbinsY()+1):
            outfile.write("{:g}   ".format(corrMatrix.GetBinContent(i,j)))
        outfile.write('\n')

    outfile.write('\n\nNLL\n')
    outfile.write("{:.6f}\n".format(fitResult.minNll()))
    outfile.write('\n')

    #code = os.system(cmd)
    return True #if code == 0 else False


def getTRExFFitFileFromLog(in_log, out_fname):

    cmd = "perl {}/utils/make_TRExNPfile.perl {} {}".format(os.getenv("VLQCOMBDIR"), in_log, out_fname)
    
    print(colored(cmd, color = "black", on_color="on_yellow"))
    code = os.system(cmd)
    return True if code == 0 else False

def plotCorrelationMatrix(wsFile, fitResultFile, outputPath, wsName, plotName):

    print(colored("makeCorrMatrix --wsFile={} --fitResultFile={} --outputPath={} --wsName={} --plotName={}".format(wsFile,fitResultFile,outputPath,wsName, plotName), color = "black", on_color="on_yellow"))
    code = os.system("makeCorrMatrix --wsFile={} --fitResultFile={} --outputPath={} --wsName={} --plotName={}"
                     .format(wsFile,fitResultFile,outputPath,wsName, plotName))
    return True if code == 0 else False

def makeTRExFCompDirs(ConfDir, LogDir, sigtag, mu=0, fittype="BONLY", isAsimov=True):
    datatag = "data" if not isAsimov else "asimov_mu{}".format(int(mu*100))
    tag_flag = sigtag + "_" + datatag + "_" + fittype
    files = [ (ConfDir + '/' + f) for f in os.listdir(ConfDir) if (tag_flag in f and '.txt' in f) ]
    trex_dirs = []
    print('\n'.join(files))
    for fname in files:
        if "multifit" in fname:
            continue
        f = open(fname)
        for line in f:
            if "Job: " in line:
                # name of the directory should be the same as the workspace+"_"+fittype
                dirname = line.strip().split(':')[1].strip()
                print(colored("mkdir -p {}/{}/Fits/".format(ConfDir, dirname), color = "black", on_color="on_yellow"))
                os.system("mkdir -p {}/{}/Fits/".format(ConfDir, dirname)) # the directory is in the same place as the config 
                trex_dirs.append(dirname)
                break
        f.close()

    for dirname in trex_dirs:
        if "multifit" in dirname:
            continue
        
        print(colored("cp {0}/{1}.txt {2}/{1}/Fits/".format(LogDir, dirname, ConfDir), color = "black", on_color="on_yellow"))
        code = os.system("cp {0}/{1}.txt {2}/{1}/Fits/".format(LogDir, dirname, ConfDir)) # copy the already created fit file from LogDir to the  TRExF's Fits/ dir
        if code != 0:
            return False

    return True


