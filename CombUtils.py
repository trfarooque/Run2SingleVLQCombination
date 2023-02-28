import sys, os
sys.path.append("VLQ_Interpretation_Tools")

from VLQCouplingCalculator import VLQCouplingCalculator as vlq
from VLQCrossSectionCalculator import *
from termcolor import colored

ALL_ANACODES = ['SPT_OSML', 'SPT_HTZT', 'SPT_MONOTOP', 'SPT_ALLHAD', 'SPT_TYWB', 'SPT_COMBINED']
VLQCOMBDIR = os.getcwd()

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
    def __init__(self, AnaCode, DataFolder = 'data', WSName = 'combined', VLQCombDir = VLQCOMBDIR, makePaths = False):
        if AnaCode not in ALL_ANACODES:
            raise Exception("Unknown Analysis Code!")
        else:
            self.AnaCode = AnaCode
        self.isCombined = True if self.AnaCode == 'SPT_COMBINED' else False
        self.VLQCombDir = VLQCombDir
        self.DataFolder = DataFolder
        self.WSName = WSName
        self.InWSDir = self.VLQCombDir + '/' + self.DataFolder + '/workspaces/input_workspaces/' + self.AnaCode + '/'
        self.ScaledWSDir = self.VLQCombDir + '/' + self.DataFolder + '/workspaces/scaled_workspaces/' + self.AnaCode + '/'
        self.ScalingConfigDir = self.VLQCombDir + '/' + self.DataFolder + '/xml/scaling/' + self.AnaCode + '/'
        self.AsimovWSDir = self.VLQCombDir + '/' + self.DataFolder + '/workspaces/asimov_workspaces/' + self.AnaCode + '/'
        self.AsimovConfigDir = self.VLQCombDir + '/' + self.DataFolder + '/xml/asimov/' + self.AnaCode + '/'
        self.CombinedWSDir = self.VLQCombDir + '/' + self.DataFolder + '/workspaces/combined_workspaces/' + self.AnaCode + '/'
        self.CombinationConfigDir = self.VLQCombDir + '/' + self.DataFolder + '/xml/combination/' + self.AnaCode + '/'
        self.FittedWSDir = self.VLQCombDir + '/' + self.DataFolder + '/workspaces/fitted_workspaces/' + self.AnaCode + '/'
        self.LimitsDir = self.VLQCombDir + '/' + self.DataFolder + '/Limits/' + self.AnaCode + '/'
        if makePaths:
            self.makePaths()
        if not self.checkPaths():
            raise Exception()
    
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
        os.system(mkdir.format(self.LimitsDir))

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
        if not os.path.exists(self.LimitsDir):
            print(colored("Limits directory {} not found!".format(self.FittedWSDir), color = "black", on_color="on_red"))
            return False
        
        return True

    def getInputWSPath(self, mass, kappa, brw):
        sigtag = getSigTag(mass, kappa, brw)
        mktag = getMKTag(mass, kappa)
        return "{}/{}_combined_{}.root".format(self.InWSDir, self.AnaCode, mktag)

    def getScaledWSPath(self, mass, kappa, brw):
        sigtag = getSigTag(mass, kappa, brw)
        mktag = getMKTag(mass, kappa)
        return "{}/{}_scaled_{}.root".format(self.ScaledWSDir, self.AnaCode, sigtag)
        
    def getScalingConfigPath(self, mass, kappa, brw):
        sigtag = getSigTag(mass, kappa, brw)
        mktag = getMKTag(mass, kappa)
        return "{}/{}_scaling_{}.xml".format(self.ScalingConfigDir, self.AnaCode, sigtag)

    def getScalingConfing(self, mass, kappa, brw, DataName="asimovData"):

        InFilePath = self.getInputWSPath(mass, kappa, brw)
        if not os.path.exists(InFilePath):
            print(colored("Input WS {} not found!".format(INFilePath), color = "black", on_color="on_red"))
            return False
    
        OutFilePath = self.getScaledWSPath(mass, kappa, brw)
        OutConfigPath = self.getScalingConfigPath(mass, kappa, brw)

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
        print("Config written to {}".format(colored(OutConfigPath, color = "black", on_color="on_green")))
        return True # "{}  :  {}  :  {}".format(AnaChannel, OutFilePath, WSName)

    def scaleWS(self, mass, kappa, brw, LogFile="log.txt"):
        ConfigName = self.getScalingConfigPath(mass, kappa, brw)
        if not os.path.exists(ConfigName):
            return False
        os.system("cp templates/Organization.dtd {}".format(self.ScalingConfigDir))
        code = os.system('manager -w edit -x {} 2>&1 |tee {}'.format(ConfigName, LogFile))
        return True if code == 0 else False    

    def getCombinationConfigPath(self, mass, kappa, brw):
        sigtag = getSigTag(mass, kappa, brw)
        mktag = getMKTag(mass, kappa)
        return "{}/{}_combination_{}.xml".format(self.CombinationConfigDir, self.AnaCode, sigtag)

    def getCombinedWSPath(self, mass, kappa, brw):
        sigtag = getSigTag(mass, kappa, brw)
        mktag = getMKTag(mass, kappa)
        return "{}/{}_combined_{}.root".format(self.CombinedWSDir, self.AnaCode, sigtag)

    def getCombinationConfig(self, WSListFile, mass, kappa, brw, DataName = 'asimovData'):
        
        if not os.path.exists(WSListFile):
            return False
        sigtag = getSigTag(mass, kappa, brw)
        mktag = getMKTag(mass, kappa)
        cmd = '''{0}/WorkspaceChecks/bin/workspace.exe \
file_path={1} \
data_name="{2}" \
output_xml_folder={3} \
output_xml_name={4} \
output_ws_folder={5} \
output_ws_name={6} \
do_config_dump=TRUE \
do_checks=FALSE \
abort_on_error=FALSE '''.format(self.VLQCombDir, 
                                WSListFile, 
                                DataName, 
                                self.CombinationConfigDir,
                                self.getCombinationConfigPath(mass, kappa, brw).split('/')[-1],
                                self.CombinedWSDir,
                                self.getCombinedWSPath(mass, kappa, brw).split('/')[-1])
        # print(cmd)
        code = os.system(cmd)
        return True if code == 0 else None


    def combineWS(self, mass, kappa, brw, LogFile="log_combine.txt"):
        ConfigName = self.getCombinationConfigPath(mass, kappa, brw)
        if not os.path.exists(ConfigName):
            return False
        os.system("cp templates/Combination.dtd {}".format(self.CombinationConfigDir))
        code = os.system("manager -w combine -x {} 2>&1 |tee {}".format(ConfigName, LogFile))
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
        if self.isCombined:
            InFilePath = self.getCombinedWSPath(mass, kappa, brw)
        else:
            InFilePath = self.getScaledWSPath(mass, kappa, brw)
        
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
        #return [AnaChannel, OutConfigPath, WSName, 'combData' if AnaChannel == 'SPT_COMBINED' else 'asimovData']

    def getAsimovWS(self, mass, kappa, brw, mu=0, LogFile="log.txt"):
        ConfigName = self.getAsimovConfigPath(mass, kappa, brw, mu)
        DataName = 'asimovData' if not self.isCombined else 'combData'
        if not os.path.exists(ConfigName):
            return False
        os.system("cp templates/asimovUtil.dtd {}".format(self.AsimovConfigDir))
        code = os.system('quickAsimov -x {} -w {} -m ModelConfig -d {}  2>&1 |tee {}'.format(ConfigName, self.WSName, DataName, LogFile))
        return True if code == 0 else False


    def getFittedResultPath(self, mass, kappa, brw, mu=0, isAsimov=True):
        sigtag = getSigTag(mass, kappa, brw)
        mktag = getMKTag(mass, kappa)
        if isAsimov:
            return "{}/{}_fitted_asimov_mu{}_{}.root".format(self.FittedWSDir, self.AnaCode, int(mu*100), sigtag)
        else:
            return "{}/{}_fitted_{}.root".format(self.FittedWSDir, self.AnaCode, sigtag)
        
 
    def fitWS(self, mass, kappa, brw, mu=0, isAsimov=True, LogFile="log.txt"):
        # os.system("cp templates/asimovUtil.dtd {}".format(self.AsimovConfigDir))
        DSName = "asimovData_mu{}".format(int(mu*100)) if isAsimov else ("obsData" if not self.isCombined else "combData")
        InWSPath = self.getAsimovWSPath(mass, kappa, brw, mu) if isAsimov \
                   else (self.getCombinedWSPath(mass, kappa, brw) if self.isCombined \
                         else self.getScaledWSPath(mass, kappa, brw))
        cmd = '''quickFit -w {} -f {} -d {}  -o {} \
--savefitresult 1 --hesse 1 --minos 1 {} 2>&1 |tee {}'''.format(self.WSName,
                                                                InWSPath,
                                                                DSName,
                                                                self.getFittedResultPath(mass, kappa, brw, mu, isAsimov), 
                                                                '-p mu_signal=0' if isAsimov else '',
                                                                LogFile)
        code = os.system(cmd)
        return True if code == 0 else False

    def getLimitsPath(self, mass, kappa, brw, mu=0, isAsimov=True):
        sigtag = getSigTag(mass, kappa, brw)
        mktag = getMKTag(mass, kappa)
        if isAsimov:
            return "{}/{}_limits_asimov_mu{}_{}.root".format(self.LimitsDir, self.AnaCode, int(mu*100), sigtag)
        else:
            return "{}/{}_limits_{}.root".format(self.LimitsDir, self.AnaCode, sigtag)



    def getLimits(self, mass, kappa, brw, mu=0, isAsimov=True, LogFile="log.txt"):
        # os.system("cp templates/asimovUtil.dtd {}".format(self.AsimovConfigDir))
        DSName = "asimovData_mu{}".format(int(mu*100)) if isAsimov else ("obsData" if not self.isCombined else "combData")
        InWSPath = self.getAsimovWSPath(mass, kappa, brw, mu) if isAsimov \
                   else (self.getCombinedWSPath(mass, kappa, brw) if self.isCombined \
                         else self.getScaledWSPath(mass, kappa, brw))
        cmd = '''quickLimit -w {} -f {} -d {} -p mu_signal \
-o {} 2>&1 |tee {}'''.format(self.WSName,
                             InWSPath,
                             DSName,
                             self.getLimitsPath(mass, kappa, brw, mu, isAsimov),
                             LogFile)

        code = os.system(cmd)
        return True if code == 0 else False



#####################################################################################

# def getSigTag(mass, kappa, brw):
#     return "M{:02d}K{:03d}brw{:02d}".format(int(mass/100), int(kappa*100), int(brw*100))

# def getMKTag(mass, kappa):
#     return "M{:02d}K{:03d}".format(int(mass/100), int(kappa*100))


# def getSF(mass, kappa, brw, all_modes = ['WTZt', 'WTHt', 'ZTZt', 'ZTHt']):
#     c = vlq(mass, 'T')
#     c.setKappaxi(kappa, brw, (1-brw)/2.0)
#     GM = c.getGamma()/mass
#     cw, cz, _, _ = c.getc_Vals()
#     XSvals = []
#     XSsum = 0.
#     for mode in all_modes:
#         this_xs = XS_NWA(mass, cw if mode[0] == 'W' else cz, mode = mode[0:2]) * (brw if mode[2] == 'W' else (1-brw)/2.) * \
#                   FtFactor(proc=mode, mass=mass, GM=GM)/PNWA(proc=mode, mass=mass, GM=GM)
#         XSsum += this_xs
#         XSvals.append(this_xs)
#     for ii in range(len(XSvals)):
#         XSvals[ii] = XSvals[ii]/XSsum
#     return XSvals


# #def getScalingConfingXML(InFilePath, OutFilePath, OutConfigPath, AnaChannel, 
# #                         mass, kappa, brw, WSName= "combined", DataName="asimovData"):
# def getScalingConfingXML(vlqcfg, mass, kappa, brw, 
#                          WSName= "combined", DataName="asimovData"):
#     if not os.path.exists(vlqcfg.InWSDir):
#         print(colored("Input WS {} not found!".format(vlqcfg.InWSDir), color = "black", on_color="on_red"))
#         return False
#     if not os.path.exists(vlqcfg.ScaledWSDir):
#         print(colored("Output WS directory {} not found!".format(vlqcfg.ScaledWSDir)), color = "black", on_color="on_red"))
#         return False
#     if not os.path.exists(vlqcfg.ScaledConfigDir):
#         print(colored("Output directory for config {} not found!".format(vlqcfg.ScaledConfigDir), color = "black", on_color="on_red"))
#         return False
#     sigtag = getSigTag(mass, kappa, brw)
#     sfWTZt, sfWTHt, sfZTZt, sfZTHt = getSF(mass, kappa, brw, all_modes = ['WTZt', 'WTHt', 'ZTZt', 'ZTHt'])
#     str_to_print = '''
# <!DOCTYPE Organization  SYSTEM 'Organization.dtd'>
# <Organization
#     InFile="{}"'''.format(InFilePath) + '''
#     OutFile="{}"'''.format(OutFilePath) + '''
#         ModelName="{}_{}"'''.format(AnaChannel, sigtag) + '''
#         POINames="mu_signal"
#         WorkspaceName="{}"'''.format(WSName) + '''
#         ModelConfigName="ModelConfig"
#         DataName="{}"'''.format(DataName) + '''
#         >
#   <Item Name="sc_TS_WTZt[{}]"/>
#   <Item Name="sc_TS_WTHt[{}]"/>
#   <Item Name="sc_TS_ZTZt[{}]"/>
#   <Item Name="sc_TS_ZTHt[{}]"/>'''.format(sfWTZt, sfWTHt, sfZTZt, sfZTHt) + '''
#   <Item Name="mu_signal[1,-100,100]"/>

#   <Item Name="expr::mu_sc_TS_WTZt('@0*@1', sc_TS_WTZt, mu_signal)" />
#   <Item Name="expr::mu_sc_TS_WTHt('@0*@1', sc_TS_WTHt, mu_signal)" />
#   <Item Name="expr::mu_sc_TS_ZTZt('@0*@1', sc_TS_ZTZt, mu_signal)" />
#   <Item Name="expr::mu_sc_TS_ZTHt('@0*@1', sc_TS_ZTHt, mu_signal)" />
#   <Map Name="EDIT::NEWPDF(OLDPDF,                                                                                                                                           
#              mu_WTZt=mu_sc_TS_WTZt,                                                                                                                                         
#              mu_WTHt=mu_sc_TS_WTHt,                                                                                                                                         
#              mu_ZTZt=mu_sc_TS_ZTZt,                                                                                                                                         
#              mu_ZTHt=mu_sc_TS_ZTHt)" />
# </Organization>
# '''

#     f = open(OutConfigPath, 'w')
#     f.write(str_to_print)
#     f.close()
#     print("Config written to {}".format(colored(OutConfigPath, color = "black", on_color="on_green")))
#     return "{}  :  {}  :  {}".format(AnaChannel, OutFilePath, WSName)
    

# def scaleWS(ConfigName, LogFile="log.txt"):
#     os.system("cp templates/Organization.dtd {}".format('/'.join(ConfigName.split('/')[:-1])))
#     code = os.system('manager -w edit -x {} 2>&1 |tee {}'.format(ConfigName, LogFile))
#     return True if code == 0 else False
    

# def getAsimovConfigXML(InFilePath, OutFilePath, OutConfigPath, AnaChannel, WSName):
#     if AnaChannel not in list(ALL_ANACODES.keys()) + ['SPT_COMBINED']:
#         print(colored("Invalid Analysis Channel!", color = "black", on_color="on_red"))
#         return False
#     if not os.path.exists(InFilePath):
#         print(colored("Input WS {} not found!".format(InFilePath), color = "black", on_color="on_red"))
#         return False
#     if not os.path.exists('/'.join(OutFilePath.split('/')[:-1])):
#         print(colored("Output WS directory {} not found!".format('/'.join(OutFilePath.split('/')[:-1])), color = "black", on_color="on_red"))
#         return False
#     if not os.path.exists('/'.join(OutConfigPath.split('/')[:-1])):
#         print(colored("Output directory for config {} not found!".format('/'.join(OutConfigPath.split('/')[:-1])), color = "black", on_color="on_red"))
#         return False
#     str_to_print='''<!DOCTYPE Asimov  SYSTEM 'asimovUtil.dtd'>  
# <Asimov 
#     InputFile="{}" 
#     OutputFile="{}"
#     POI="mu_signal" 
#     >
#   <Action Name="Prepare" Setup="" Action="nominalNuis:nominalGlobs"/>
#   <Action Name="asimovData_mu0" Setup="mu_signal=0" Action="genasimov:nominalGlobs"/>
# </Asimov>'''.format(InFilePath, OutFilePath)
#     f = open(OutConfigPath, 'w')
#     f.write(str_to_print)
#     f.close()
#     return [AnaChannel, OutConfigPath, WSName, 'combData' if AnaChannel == 'SPT_COMBINED' else 'asimovData']
    
# def getAsimovWS(ConfigName, WSName, DataName, LogFile="log.txt"):
#     os.system("cp templates/asimovUtil.dtd {}".format('/'.join(ConfigName.split('/')[:-1])))
#     code = os.system('quickAsimov -x {} -w {} -m ModelConfig -d {}'.format(ConfigName, WSName, DataName))
#     return True if code == 0 else False

# def getCombWS(WSListFile, sigtag):
#     cmd = '''{0}/WorkspaceChecks/bin/workspace.exe \
# file_path={1} \
# data_name="asimovData" \
# output_xml_folder={0}/data_devloc/xml/combination/ \
# output_ws_folder={0}/data_devloc/workspaces/combined_workspaces/ \
# output_ws_name={2}_combined.root \
# do_config_dump=TRUE \
# do_checks=FALSE \
# abort_on_error=FALSE '''.format(VLQCOMBDIR, WSListFile, sigtag)
#     # print(cmd)
#     code = os.system(cmd)
#     return "{}/data_devloc/xml/combination/combination.xml".format(VLQCOMBDIR) if code == 0 else False

# def combineWS(CombConfig, LogFile="log_combine.txt"):
#     os.system("cp templates/Combination.dtd {}".format('/'.join(CombConfig.split('/')[:-1])))
#     code = os.system("manager -w combine -x {} 2>&1 |tee {}".format(CombConfig, LogFile))
#     return True if code == 0 else False
                     


 


if __name__ == "__main__":
    mass = 1600.
    kappa = 0.5
    brw = 0.5 # singlet
    # print(getSF(mass=mass, kappa=kappa, brw=brw))
    sigtag = getSigTag(mass, kappa, brw)
    mktag = getMKTag(mass, kappa)
    ws_list = ""
    asimov_ws_list = ""
    do_asimov = True
    for anacode in ALL_ANACODES.keys():
        wsinfo = getScalingConfingXML(InFilePath =  "{}/{}_combined_{}.root".format(ALL_ANACODES[anacode]['InWSDir'], anacode, mktag),
                                      OutFilePath = "{}/{}_scaled_{}.root".format(ALL_ANACODES[anacode]['ScaledWSDir'], anacode, sigtag), 
                                      OutConfigPath = "{}/{}_scaling_{}.xml".format(ALL_ANACODES[anacode]['ScaledConfigDir'], anacode, sigtag), 
                                      AnaChannel = anacode,
                                      mass = mass, 
                                      kappa = kappa, 
                                      brw = brw, 
                                      WSName = ALL_ANACODES[anacode]['WSName'], 
                                      DataName="asimovData")
        if not wsinfo:
            print(colored("Scaling Config File Could not be Generated for " + anacode + " at M = {} and K = {}".format(mass, kappa), color = "black", on_color="on_red"))
            continue
        ws_list += wsinfo + '\n'
        if not scaleWS(ConfigName = "{}/{}_scaling_{}.xml".format(ALL_ANACODES[anacode]['ScaledConfigDir'], anacode, sigtag), LogFile="log_{}.txt".format(anacode)):
            print(colored("Scaling WS failed for " + anacode + " at M = {}, K= {}, and brw = {}".format(mass, kappa, brw), color = "black", on_color="on_red"))
            continue
        asimovwsinfo = getAsimovConfigXML(InFilePath = "{}/{}_scaled_{}.root".format(ALL_ANACODES[anacode]['ScaledWSDir'], anacode, sigtag), 
                                          OutFilePath = "{}/{}_MU0ASIMOV_{}.root".format(ALL_ANACODES[anacode]['ScaledWSDir'], anacode, sigtag),
                                          OutConfigPath = "{}/{}_MU0ASIMOV_{}.xml".format(ALL_ANACODES[anacode]['AsimovConfigDir'], anacode, sigtag),
                                          AnaChannel = anacode, 
                                          WSName = ALL_ANACODES[anacode]['WSName'])
        if not asimovwsinfo:
            print(colored("ASIMOV config failed for " + anacode + " at M = {}, K= {}, and brw = {}".format(mass, kappa, brw), color = "black", on_color="on_red"))
            continue
        else:
            _anachan, _configpath, _wsname, _dataname = asimovwsinfo
        if not getAsimovWS(_configpath, _wsname, _dataname, LogFile="log.txt"):
            print(colored("ASIMOV WS failed for " + anacode + " at M = {}, K= {}, and brw = {}".format(mass, kappa, brw), color = "black", on_color="on_red"))
            continue
        
    f = open("wsList.txt", "w")
    f.write(ws_list)
    f.close()
    print("WS List is available at " + colored('wsList.txt', color = "black", on_color="on_green"))
    CombConfig = getCombWS(WSListFile = "wsList.txt", sigtag=sigtag)
    if not CombConfig:
        print(colored("Generating Combination Config failed for M = {}, K= {}, and brw = {}".format(mass, kappa, brw), color = "black", on_color="on_red"))
        sys.exit(1)
    if not combineWS(CombConfig, LogFile="log_combine.txt"):
        print(colored("Combination failed for M = {}, K= {}, and brw = {}".format(mass, kappa, brw), color = "black", on_color="on_red"))
        sys.exit(1)

    asimovwsinfo = getAsimovConfigXML(InFilePath = "{}/data_devloc/workspaces/combined_workspaces/{}_combined.root".format(VLQCOMBDIR, sigtag),
                                      OutFilePath = "{}/data_devloc/workspaces/asimov_workspaces/SPT_COMBINED/{}_MU0ASIMOV_combined.root".format(VLQCOMBDIR, sigtag),
                                      OutConfigPath = "{}/data_devloc/xml/asimov/SPT_COMBINED/{}_MU0ASIMOV_COMBINED.xml".format(VLQCOMBDIR, sigtag),
                                      AnaChannel = 'SPT_COMBINED',
                                      WSName = 'combWS')
    
