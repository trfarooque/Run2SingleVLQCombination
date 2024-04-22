import os
import ROOT

import numpy as np
from scipy.interpolate import NearestNDInterpolator, LinearNDInterpolator, interp1d, RBFInterpolator

from CombUtils import *
from VLQCouplingCalculator import VLQCouplingCalculator as vlq
from VLQCrossSectionCalculator import *
from Helper import *


sigtype=["WTHt","WTZt","ZTHt","ZTZt"]
keyDictionary = {"WT": 0,"ZT": 1,"HT": 2}



def LimitMapMaker(Loc="/data/chenlian/combinationRunResults/limits/", Cfg="SPT_COMBINED"):
    """
    Makes a dictionary of limits.
    For each kappa and mass, there is a dictionary entry: limit[kappa][mass], each entry being a dictionary.
    Each entry stores six numbers, with keys ['obs', 'exp', '2up', '1up', '1dn', '2dn'].
    These numbers are XS limits in pb.
    Adapted for OSML_SP3l analysis, can be adapted for any analysis.
    """
    limit_map_all = {
        'obs': [],
        'exp': [],
        '2up': [],
        '1up': [],
        '1dn': [],
        '2dn': []
    }
    
    Ms = list(range(1000, 2701, 100))
    Ks = [0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00]
    BRWs = [0.00, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 0.99]
    Fail_list = []

    for mass in Ms:
        for kappa in Ks:
            for brw in BRWs:
                sigtag = getSigTag(mass, kappa, brw)
                limit_file = os.path.join(Loc, Cfg, f"{Cfg}_limits_{sigtag}_data.txt")

                if not os.path.exists(limit_file):
                    print(f"{limit_file} doesn't exist!")
                    Fail_list.append([mass, kappa, brw])
                    continue

                try:
                    with open(limit_file, 'r') as file:
                        line = file.readline().strip()
                        values = np.array(line.split(' '), dtype='float64') * 0.1
                        limit_map_all["obs"].append([mass, kappa, brw, values[0]])
                        limit_map_all["exp"].append([mass, kappa, brw, values[1]])
                        limit_map_all["2up"].append([mass, kappa, brw, values[2]])
                        limit_map_all["1up"].append([mass, kappa, brw, values[3]])
                        limit_map_all["1dn"].append([mass, kappa, brw, values[4]])
                        limit_map_all["2dn"].append([mass, kappa, brw, values[5]])
                except Exception as e:
                    print(f"{limit_file} failed: {e}")
                    Fail_list.append([mass * 100, kappa, brw])
                    continue
    
    return limit_map_all, Fail_list



def GetInterpolator(Limit_map, debug = False):
    Limit_map = np.array(Limit_map)
    #print(Limit_map.dtype)
    X = Limit_map[:, :-1]
    Y = Limit_map[:, -1]
    # return NearestNDInterpolator(X,Y,rescale=True)
    return BuildInterpolator(X,Y,debug=debug)



class BuildInterpolator:
    def __init__(self, X, Y, flag=-1e+6, debug=True):
        self.X = X
        self.Y = Y
        self.flag = flag
        self.debug = debug
        
        self.interp_nearest = NearestNDInterpolator(self.X, self.Y, rescale=True)
        self.interp_rbf = RBFInterpolator(self.X, self.Y, kernel='multiquadric', smoothing=2, degree=1, epsilon=0.7)
        
        try:
            self.interp_linear = LinearNDInterpolator(self.X, self.Y, fill_value=self.flag, rescale=True)
        except Exception:
            self.interp_linear = self.interp_nearest

    def __call__(self, x):
        result_linear = self.interp_linear(x)
        result_nearest = self.interp_nearest(x)
        indices = result_linear == self.flag
        
        if self.debug:
            print(result_linear)
            print(result_nearest)
            print(indices)
        
        result_linear[indices] = result_nearest[indices]
        return result_linear



def MassLimitsPlotter(limit_map_all, kfact=1.0, plotnametag="", plotsubdir="", limit_type='exp'):
    interpolator = GetInterpolator(limit_map_all[limit_type])
    dBR = 0.025
    BR_min = 0.00
    BR_max = 0.95
    Gmin = 10.
    Gmax = 50.
    dG = 2
    M_values = np.array(limit_map_all[limit_type])[:, 0]
    M_min = M_values.min()
    M_max = M_values.max()
    dM = 10.0

    h = ROOT.TH2D("New_limits_" + str(kfact), " ", int((BR_max - BR_min) / dBR), BR_min, BR_max,
                  int((Gmax - Gmin) / dG), Gmin, Gmax)
    c = vlq()

    for i in range(1, h.GetNbinsX() + 1):
        BRW = h.GetXaxis().GetBinCenter(i)
        BRZ = (1.0 - BRW) / (1 + kfact ** 2)
        for j in range(1, h.GetNbinsY() + 1):
            xs_high = 0
            G = h.GetYaxis().GetBinCenter(j) / 100.
            Mhigh = M_max
            c.setMVLQ(Mhigh * 1.0)
            c.setGammaBRs(G * Mhigh * 1.0, BRW, BRZ)
            k = c.getKappa()
            cVals = c.getc_Vals()
            BR = c.getBRs()

            lim_high = interpolator(np.array([[Mhigh, k, BRW]])).reshape(-1)[0]

            for sig in sigtype:
                prodIndex = keyDictionary[sig[:2:]]
                decayIndex = keyDictionary[sig[2::].upper()]
                XSec = XS_NWA(Mhigh, cVals[prodIndex], sig[:2:]) * BR[decayIndex] * \
                       FtFactor(proc=sig, mass=Mhigh, GM=G, useAverageXS=True)[0] / PNWA(proc=sig, mass=Mhigh, GM=G)
                xs_high += XSec

            for m in np.arange(M_max, M_min - 1.0, -1 * dM):
                xs_low = 0
                Mlow = m
                c.setMVLQ(Mlow * 1.0)
                c.setGammaBRs(G * Mlow * 1.0, BRW, BRZ)
                k = c.getKappa()
                cVals = c.getc_Vals()
                BR = c.getBRs()

                lim_low = interpolator(np.array([[Mlow, k, BRW]])).reshape(-1)[0]

                for sig in sigtype:
                    prodIndex = keyDictionary[sig[:2:]]
                    decayIndex = keyDictionary[sig[2::].upper()]
                    XSec = XS_NWA(Mlow, cVals[prodIndex], sig[:2:]) * BR[decayIndex] * \
                           FtFactor(proc=sig, mass=Mlow, GM=G, useAverageXS=True)[0] / PNWA(proc=sig, mass=Mlow, GM=G)
                    xs_low += XSec

                if (lim_high - xs_high) * (lim_low - xs_low) < 0. and lim_high > 0. and lim_low > 0.:
                    h.Fill(BRW, G * 100., (Mhigh + Mlow) / 2.0)
                    break
                Mhigh = Mlow
                lim_high = lim_low
                xs_high = xs_low

    ROOT.gROOT.SetBatch(True)
    cnvs = ROOT.TCanvas("cnvs", "cnvs", 1000, 800)
    cnvs.cd()
    cnvs.SetFrameFillColor(20)
    cnvs.SetBottomMargin(0.15)
    cnvs.SetLeftMargin(0.15)
    cnvs.SetRightMargin(0.2)
    cnvs.SetTopMargin(0.15)
    h.SetStats(0)
    h.SetMinimum(M_min)
    h.GetXaxis().SetTitle("#xi_{W}")
    h.GetXaxis().SetTitleSize(0.045)
    h.GetXaxis().SetLabelSize(0.035)
    h.GetYaxis().SetTitle("#Gamma_{T}/M_{T} (%)")
    h.GetYaxis().SetTitleSize(0.045)
    h.GetYaxis().SetLabelSize(0.035)
    h.GetYaxis().SetNdivisions(9)
    
    if limit_type == "exp":
        h.GetZaxis().SetTitle("Exp Mass Limit at 95% CL [GeV]   ")
    elif limit_type == "obs":
        h.GetZaxis().SetTitle("Obs Mass Limit at 95% CL [GeV]   ")
    h.GetZaxis().SetTitleOffset(1.3)
    h.GetZaxis().SetTitleSize(0.045)
    h.GetZaxis().SetLabelSize(0.035)
    if plotnametag == "SPT_OSML":
        h.GetZaxis().SetRangeUser(1000, 2100)
    elif plotnametag == "SPT_HTZT":
        h.GetZaxis().SetRangeUser(1000, 2100)
    elif plotnametag == "SPT_MONOTOP":
        h.GetZaxis().SetRangeUser(1100, 1900)
    else:
        h.GetZaxis().SetRangeUser(1100, 2200)
    h.Draw("COLZ")

    ROOT.gStyle.SetPadTickY(1)
    ROOT.gStyle.SetPadTickX(1)
    ROOT.gPad.Update()
    ROOT.gPad.RedrawAxis()
    ROOT.gPad.RedrawAxis("F")

    h2 = h.Clone("forcontour")
    if plotnametag == "SPT_OSML":
        contours = np.array([1500., 1700., 1900.])
    elif plotnametag == "SPT_HTZT":
        if limit_type == "obs":
            contours = np.array([1600., 1800., 2000.])
        else:
            contours = np.array([1400., 1600., 1800.])
    elif plotnametag == "SPT_MONOTOP":
        contours = np.array([1400., 1600., 1800.])
    else:
        contours = np.array([1700., 1900., 2100.])
    h2.SetContour(len(contours), contours)
    h2.SetLineColor(1)
    h2.SetLineStyle(2)
    h2.SetLineWidth(2)
    h2.Draw("CONT3 same")

    tl = ROOT.TLatex()
    tl.SetTextSize(0.025)

    if limit_type == "exp":
        if plotnametag == "SPT_OSML":
            tl.DrawLatex(0.11, 15, "1500")
            tl.DrawLatex(0.76, 15, "1500")
            tl.DrawLatex(0.70, 22.5, "1700")
            tl.DrawLatex(0.62, 39, "1900")
        elif plotnametag == "SPT_HTZT":
            tl.DrawLatex(0.45, 12, "1400")
            tl.DrawLatex(0.59, 22.5, "1600")
            tl.DrawLatex(0.53, 39, "1800")
        elif plotnametag == "SPT_MONOTOP":
            tl.DrawLatex(0.17, 12, "1400")
            tl.DrawLatex(0.76, 12, "1400")
            tl.DrawLatex(0.72, 18, "1600")
            tl.DrawLatex(0.53, 30, "1800")
        else:
            tl.DrawLatex(0.16, 15, "1700")
            tl.DrawLatex(0.74, 15, "1700")
            tl.DrawLatex(0.59, 22.5, "1900")
            tl.DrawLatex(0.53, 39, "2100")            
    elif limit_type == "obs":
        if plotnametag == "SPT_OSML":
            tl.DrawLatex(0.11, 15, "1500")
            tl.DrawLatex(0.76, 15, "1500")
            tl.DrawLatex(0.65, 22.5, "1700")
            tl.DrawLatex(0.63, 39, "1900")
        elif plotnametag == "SPT_HTZT":
            tl.DrawLatex(0.18, 15, "1600")
            tl.DrawLatex(0.70, 15, "1600")
            tl.DrawLatex(0.65, 22.5, "1800")
            tl.DrawLatex(0.53, 39, "2000")
        elif plotnametag == "SPT_MONOTOP":
            tl.DrawLatex(0.20, 12, "1400")
            tl.DrawLatex(0.73, 12, "1400")
            tl.DrawLatex(0.59, 16, "1600")
            tl.DrawLatex(0.53, 35, "1800")
        else:
            tl.DrawLatex(0.16, 15, "1700")
            tl.DrawLatex(0.74, 15, "1700")
            tl.DrawLatex(0.30, 22.5, "1900")
            tl.DrawLatex(0.58, 22.5, "1900")
            tl.DrawLatex(0.59, 39, "2100")

    cnvs.SetRightMargin(0.2)
    Draw_ATLAS(0.15, 0.92, " ")
    cnvs.SaveAs("MassLimits_" + limit_type + ("_{}".format(plotnametag) if plotnametag != "" else "") + ".png")



def KappaLimitPlotter(limit_map_all, brw=0.5, plotnametag='', plotsubdir='', dm=20.):
    
    gammaMax = 0.5
    interp_exp = GetInterpolator(limit_map_all['exp'])
    interp_obs = GetInterpolator(limit_map_all['obs'])
    interp_2up = GetInterpolator(limit_map_all['2up'])
    interp_1up = GetInterpolator(limit_map_all['1up'])
    interp_1dn = GetInterpolator(limit_map_all['1dn'])
    interp_2dn = GetInterpolator(limit_map_all['2dn'])

    Ms_sparse = np.arange(1000, 2710, 100)
    Ms_to_scan = np.arange(1000, 2710, dm)
    Ks_to_scan = np.flip(np.arange(0.1, 1., 0.01))

    map_Interp = {
        "obs": interp_obs,
        "exp": interp_exp,
        "2up": interp_2up,
        "1up": interp_1up,
        "1dn": interp_1dn,
        "2dn": interp_2dn
    }

    map_cLimit_sparse = {lim_type: {} for lim_type in map_Interp.keys()}
    map_cLimit = {lim_type: {} for lim_type in map_Interp.keys()}
    c = vlq()

    for lim_type, this_Interp in map_Interp.items():
        this_limit_cmap = map_cLimit_sparse[lim_type]
        for m in Ms_sparse:
            mass = m * 1.0
            xs_low = 0
            lim_low = 0
            c.setMVLQ(mass)
            k_low = Ks_to_scan[0]
            c.setKappaxi(k_low, brw, (1. - brw) / 2.)
            cVals = c.getc_Vals()
            BR = c.getBRs()
            gm = c.getGamma() / mass
            lim_low = this_Interp(np.array([[mass, k_low, brw]])).reshape(-1)[0]

            for sig in sigtype:
                prodIndex = keyDictionary[sig[:2:]]
                decayIndex = keyDictionary[sig[2::].upper()]
                XSec = XS_NWA(mass, cVals[prodIndex], sig[:2:]) * BR[decayIndex] * \
                       FtFactor(proc=sig, mass=mass, GM=gm, useAverageXS=True)[0] / PNWA(proc=sig, mass=mass, GM=gm)
                xs_low += XSec

            for k in Ks_to_scan[1:]:
                xs_high = 0
                lim_high = 0
                k_high = k
                c.setKappaxi(k_high, brw, (1. - brw) / 2.)
                cVals = c.getc_Vals()
                BR = c.getBRs()
                gm = c.getGamma() / mass
                lim_high = this_Interp(np.array([[mass, k_high, brw]])).reshape(-1)[0]

                for sig in sigtype:
                    prodIndex = keyDictionary[sig[:2:]]
                    decayIndex = keyDictionary[sig[2::].upper()]
                    XSec = XS_NWA(mass, cVals[prodIndex], sig[:2:]) * BR[decayIndex] * \
                           FtFactor(proc=sig, mass=mass, GM=gm, useAverageXS=True)[0] / PNWA(proc=sig, mass=mass, GM=gm)
                    xs_high += XSec

                if (lim_low - xs_low) * (lim_high - xs_high) < 0. and lim_low > 0. and lim_high > 0.:
                    this_limit_cmap[m] = (k_low + k_high) / 2.0
                    break
                else:
                    c.setGammaBRs(m * gammaMax, brw, (1 - brw) / 2.)
                    k_max = c.getKappa()
                    this_limit_cmap[m] = k_max + 0.05
                    k_low = k_high
                    lim_low = lim_high
                    xs_low = xs_high

    if dm == 100.:
        map_cLimit = map_cLimit_sparse
    else:
        for key in map_cLimit.keys():
            this_Ms = np.array(list(map_cLimit_sparse[key].keys()))
            this_Ks = [map_cLimit_sparse[key][m] for m in this_Ms]
            f = interp1d(this_Ms, this_Ks)
            Ks_smooth = f(Ms_to_scan)
            for ii, m in enumerate(Ms_to_scan):
                map_cLimit[key][m] = Ks_smooth[ii]

    plotname = "KappaLimit" + ("_{}".format(plotnametag) if plotnametag != "" else "") + "_{}.png".format(brw)

    oneDLimitCouplingPlotter(map_cLimit["2up"], map_cLimit["1up"],
                             map_cLimit["1dn"], map_cLimit["2dn"],
                             map_cLimit["exp"], map_cLimit["obs"],
                             False, brw=brw, plotname=plotname)
    


def XSLimitPlotter(limit_map_all, k, brw, plotnametag='', plotsubdir=''):
    # Creates XS vs Mass plots for one of the chosen kappas

    Ms = np.array(list(range(1000, 2200, 100)) + [2300, 2500, 2700])

    interp_exp = GetInterpolator(limit_map_all['exp'])
    interp_obs = GetInterpolator(limit_map_all['obs'])
    interp_2up = GetInterpolator(limit_map_all['2up'])
    interp_1up = GetInterpolator(limit_map_all['1up'])
    interp_1dn = GetInterpolator(limit_map_all['1dn'])
    interp_2dn = GetInterpolator(limit_map_all['2dn'])

    _theory = []

    for m in Ms:
        c = vlq(m, 'T')
        c.setKappaxi(k, brw, (1. - brw) / 2.)
        cVals = c.getc_Vals()
        BR = c.getBRs()
        gm = c.getGamma() / m
        cw = c.getc_Vals()[0]
        cz = c.getc_Vals()[1]
        BRZ = c.getBRs()[1]

        total_XSec = 0.

        for sig in sigtype:
            prodIndex = keyDictionary[sig[:2:]]
            decayIndex = keyDictionary[sig[2::].upper()]
            XSec = XS_NWA(m, cVals[prodIndex], sig[:2:]) * BR[decayIndex] * \
                   FtFactor(proc=sig, mass=m, GM=gm, useAverageXS=True)[0] / PNWA(proc=sig, mass=m, GM=gm)
            total_XSec += XSec

        _theory.append(total_XSec)

    plotname = f"plots/XSLimit_K{k*100:03d}_BRW{brw*100:02d}" + (f"_{plotnametag}.png" if plotnametag else '.png')
    signal_benchmark = 'other'

    if brw == 0.5: 
        signal_benchmark = 'singlet'
    elif brw == 0.0:
        signal_benchmark = 'doublet'

    oneDLimitPlotter(Ms, interp_2up(Ms), interp_1up(Ms), interp_1dn(Ms), interp_2dn(Ms),
                     interp_exp(Ms), interp_obs(Ms), _theory, True, k=k, brw=brw, ytype="xs", 
                     plotname=plotname, signal_benchmark=signal_benchmark)
