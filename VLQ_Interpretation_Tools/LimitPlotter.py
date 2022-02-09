import ROOT
import sys, os
sys.path.append("../../vlqanalysisutilityscripts/")
from PlotterUtils import *

Ms = range(11,24,2)
Ks = ['100']

_x = []
_up2 = []
_up1 = []
_down1 = []
_down2 = []
_med = []

_med2l = []
_med3l = []

## oneDLimitPlotter(_x, _yup2, _yup1, _ydown1, _ydown2, _ymed, _yobs, do_log)
'''
1000.0 0.382263002873
1100.0 0.263547329448
1200.0 0.182821500623
1300.0 0.127412522258
1400.0 0.0891750397085
1500.0 0.0625949424186
1600.0 0.044053731129
1700.0 0.0310707583319
1800.0 0.0219517631847
1900.0 0.0154749350076
2000.0 0.0109098404133
2100.0 0.0077043348696
2200.0 0.00541271756704
2300.0 0.00383851678092
'''
_theory = [0.263547329448, 0.127412522258, 0.0625949424186, 0.0310707583319, 0.0154749350076, 0.0077043348696, 0.00383851678092]

for k in Ks:
    for m in Ms:
        mktag = 'M' + str(m) + 'K' + k
        fname = "../../TRExFitter/SingleVLT_Combination/Results/OSML_VLT_Combination_" + mktag + "/Limits/asymptotics/myLimit_CL95.root"
        f = ROOT.TFile(fname)
        t_stats = f.Get("stats")
        '''
        Limit_map_all[kappa][m*100]["obs"] = t_stats.obs_upperlimit * 0.1
            Limit_map_all[kappa][m*100]["exp"] = t_stats.exp_upperlimit * 0.1
            Limit_map_all[kappa][m*100]["2up"] = t_stats.exp_upperlimit_plus2 * 0.1
            Limit_map_all[kappa][m*100]["1up"] = t_stats.exp_upperlimit_plus1 * 0.1
            Limit_map_all[kappa][m*100]["1dn"] = t_stats.exp_upperlimit_minus1 * 0.1
            Limit_map_all[kappa][m*100]["2dn"] = t_stats.exp_upperlimit_minus2 * 0.1
        '''
        t_stats.GetEntry(0)
        _x.append(m*100.0)
        _med.append(t_stats.exp_upperlimit * 0.1)
        _up2.append(t_stats.exp_upperlimit_plus2 * 0.1)
        _up1.append(t_stats.exp_upperlimit_plus1 * 0.1)
        _down1.append(t_stats.exp_upperlimit_minus1 * 0.1)
        _down2.append(t_stats.exp_upperlimit_minus2 * 0.1)

for m in Ms:
    mktag = 'M' + str(m) + 'K100'
    fname = "/afs/cern.ch/work/a/avroy/TRExFitter/SingleVLT_3l_Results/FitResults/VLT_Single_Trilept_AllSyst_Fit_" + mktag + "/Limits/asymptotics/myLimit_CL95.root"
    f = ROOT.TFile(fname)
    t_stats = f.Get("stats")
    t_stats.GetEntry(0)
    _med3l.append(t_stats.exp_upperlimit * 0.1)

for m in Ms:
    mktag = str(m) + 'K10'
    fname = "/eos/atlas/atlascerngroupdisk/phys-exotics/hqt/OSML/SP2lCombination/SP2l_r32_" + mktag + "/Limits/asymptotics/myLimit_CL95.root"
    f = ROOT.TFile(fname)
    t_stats = f.Get("stats")
    t_stats.GetEntry(0)
    _med2l.append(t_stats.exp_upperlimit * 0.1)

print _med
print _theory
print _med2l
print _med3l

oneDLimitPlotter(_x, _up2, _up1, _down1, _down2, _med, _med, _theory, do_log=True, plotname="Limits_1D_K100_Combination.png", _y2l=_med2l, _y3l=_med3l)
