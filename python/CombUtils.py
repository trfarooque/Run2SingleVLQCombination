import sys, os
from termcolor import colored
from VLQCouplingCalculator import VLQCouplingCalculator as vlq
from VLQCrossSectionCalculator import *


ALL_ANACODES = ['SPT_OSML', 'SPT_HTZT', 'SPT_MONOTOP', 'SPT_ALLHAD', 'SPT_TYWB', 'SPT_COMBINED']
#VLQCOMBDIR = os.getenv("VLQCOMBDIR") 
INPUTDIR=os.getcwd()

def getSigTag(mass, kappa, brw):
    return "M{:02d}K{:03d}BRW{:02d}".format(int(mass/100), int(kappa*100), int(brw*100))

def getMKTag(mass, kappa):
    return "M{:02d}K{:03d}".format(int(mass/100), int(kappa*100))

def getSF(mass, kappa, brw, all_modes = ['WTZt', 'WTHt', 'ZTZt', 'ZTHt']):
    c = vlq(mass, 'T')
    c.setKappaxi(kappa, brw, (1-brw)/2.0)
    GM = c.getGamma()/mass
    cw, cz, _, _ = c.getc_Vals()
    XSvals = []
    XSsum = 0.
    for mode in all_modes:
        this_xs = XS_NWA(mass, cw if mode[0] == 'W' else cz, mode = mode[0:2]) * (brw if mode[2] == 'W' else (1-brw)/2.) * \
                  FtFactor(proc=mode, mass=mass, GM=GM)/PNWA(proc=mode, mass=mass, GM=GM)
        XSsum += this_xs
        XSvals.append(this_xs)
    for ii in range(len(XSvals)):
        XSvals[ii] = XSvals[ii]/XSsum
    return XSvals


class VLQCombinationConfig:
    def __init__(self, AnaCode, DataFolder = 'data', WSName = 'combined', VLQCombDir = INPUTDIR, makePaths = False, checkPaths = False):
        if AnaCode not in ALL_ANACODES:
            raise Exception("Unknown Analysis Code!")
        else:
            self.AnaCode = AnaCode
        self.isCombined = True if self.AnaCode == 'SPT_COMBINED' else False

        self.VLQCombDir = VLQCombDir
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
        
        self.setPaths()
        
        # self.TRExFConfigDir = self.VLQCombDir + '/' + self.DataFolder + '/trexf/configs/'  # this directory is NOT split across different folders for different channels
        if makePaths:
            self.makePaths()

        if checkPaths:
            if not self.checkPaths():
                raise Exception()

    def setPaths(self):
        self.InWSDir = self.VLQCombDir + '/' + self.DataFolder + '/' + self.InWSSubDir + '/' +  self.AnaCode + '/'
        self.ScaledWSDir = self.VLQCombDir + '/' + self.DataFolder + '/' + self.ScaledWSSubDir + '/' + self.AnaCode + '/'
        self.ScalingConfigDir = self.VLQCombDir + '/' + self.DataFolder + '/' + self.ScalingConfigSubDir  + '/' + self.AnaCode + '/'
        self.AsimovWSDir = self.VLQCombDir + '/' + self.DataFolder + '/' + self.AsimovWSSubDir + '/' + self.AnaCode + '/'
        self.AsimovConfigDir = self.VLQCombDir + '/' + self.DataFolder + '/' + self.AsimovConfigSubDir  + '/' + self.AnaCode + '/'
        self.CombinedWSDir = self.VLQCombDir + '/' + self.DataFolder + '/' + self.CombinedWSSubDir + '/' + self.AnaCode + '/'
        self.CombinationConfigDir = self.VLQCombDir + '/' + self.DataFolder + '/' + self.CombinationConfigSubDir  + '/' + self.AnaCode + '/'
        self.FittedWSDir = self.VLQCombDir + '/' + self.DataFolder + '/' + self.FittedWSSubDir + '/' + self.AnaCode + '/'
        self.LimitDir = self.VLQCombDir + '/' + self.DataFolder + '/' + self.LimitSubDir  + '/' + self.AnaCode + '/'
        self.LogDir = self.VLQCombDir + '/' + self.DataFolder + '/' + self.LogSubDir  + '/' + self.AnaCode + '/'

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
        # os.system(mkdir.format(self.TRExFConfigDir))

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
        # if not os.path.exists(self.TRExFConfigDir):
        #     print(colored("Limits directory {} not found!".format(self.TRExFConfigDir), color = "black", on_color="on_red"))
        #     return False
        
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
        os.system("cp {}/dtd/Organization.dtd {}".format(os.getenv('VLQCOMBDIR'),self.ScalingConfigDir))
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
        #cmd = '''{0}/WorkspaceChecks/bin/workspace.exe \ self.VLQCombDir, 
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
        code = os.system(cmd)
        return True if code == 0 else None


    def combineWS(self, mass, kappa, brw, datatag, LogFile="log_combine.txt"):
        ConfigName = self.getCombinationConfigPath(mass, kappa, brw, datatag)
        if not os.path.exists(ConfigName):
            return False
        os.system("cp {}/dtd/Combination.dtd {}".format(os.getenv('VLQCOMBDIR'),self.CombinationConfigDir))
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
        os.system("cp {}/dtd/asimovUtil.dtd {}".format(os.getenv('VLQCOMBDIR'),self.AsimovConfigDir))
        code = os.system('quickAsimov -x {} -w {} -m ModelConfig -d {} > {} 2>&1'.format(ConfigName, self.WSName, DataName, LogFile))
        return True if code == 0 else False


    def getFittedResultPath(self, mass, kappa, brw, mu=0, fittype='BONLY', isAsimov=True):
        sigtag = getSigTag(mass, kappa, brw)
        mktag = getMKTag(mass, kappa)
        datatag = "data" if not isAsimov else "asimov_mu{}".format(int(mu*100))
        return "{}/{}_fitted_{}_{}_{}.root".format(self.FittedWSDir, self.AnaCode, sigtag, datatag, fittype)
        
 
    def fitWS(self, mass, kappa, brw, mu=0,  fittype='BONLY', isAsimov=True, LogFile="log.txt"):
        # os.system("cp templates/asimovUtil.dtd {}".format(self.AsimovConfigDir))
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
        code = os.system(cmd)
        return True if code == 0 else False

    def getLimitsPath(self, mass, kappa, brw, mu=0, isAsimov=True):
        sigtag = getSigTag(mass, kappa, brw)
        mktag = getMKTag(mass, kappa)
        datatag = "data" if not isAsimov else "asimov_mu{}".format(int(mu*100))
        return "{}/{}_limits_{}_{}.root".format(self.LimitDir, self.AnaCode, sigtag, datatag)


    def getLimits(self, mass, kappa, brw, mu=0, isAsimov=True, LogFile="log.txt"):
        # os.system("cp templates/asimovUtil.dtd {}".format(self.AsimovConfigDir))
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

        code = os.system(cmd)
        return True if code == 0 else False

def getTRExFConfigs(ConfDir, WSListFile, sigtag, mu=0, fittype="BONLY", isAsimov= True):
    if not os.path.exists(WSListFile):
        return False
    DSName = "asimovData_mu{}".format(int(mu*100)) if isAsimov else "obsData" 
    datatag = "data" if not isAsimov else "asimov_mu{}".format(int(mu*100))
    #cmd = '''{}/WorkspaceChecks/bin/workspace.exe \ VLQCOMBDIR, 
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
    print(cmd)
    code = os.system(cmd)
    return True if code == 0 else False

def getTRExFFitFile(in_log, out_fname):
    if not os.path.exists(in_log):
        return False
    if not os.path.exists('/'.join(out_fname.split('/')[:-1])):
        return False
    cmd = "perl {}/utils/make_TRExNPfile.perl {} {}".format(os.getenv("VLQCOMBDIR"), in_log, out_fname)
    code = os.system(cmd)
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
                dirname = line.strip().split(':')[1].strip() # name of the directory should be the same as the workspace
                os.system("mkdir -p {}/{}/Fits/".format(ConfDir, dirname)) # the directory is in the same place as the config 
                trex_dirs.append(dirname)
                break
        f.close()

    for dirname in trex_dirs:
        if "multifit" in dirname:
            continue
        code = os.system("cp {0}/{1}.txt {2}/{1}/Fits/".format(LogDir, dirname, ConfDir)) # copy the already created fit file from LogDir to the  TRExF's Fits/ dir
        if code != 0:
            return False
    return True


                         
        
                
