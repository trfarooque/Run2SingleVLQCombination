import ROOT
import os, sys
from matplotlib import pyplot as plt
from numpy import random, diag, array, asarray, log, exp, arange, sin, cos, append
from VLQCouplingCalculator import VLQCouplingCalculator as vlq
from VLQCouplingCalculator import VLQMixAngleCalculator as vlqx
from VLQCrossSectionCalculator import XS_NWA, PNWA, interpolator
from PlotterUtils import *


'''
def XS_SP_plotter():
    X1 = sorted(XS_map_singleWb.keys())
    Y1 = []

    for x in X1:
        Y1.append(XS_map_singleWb[x])

    Xt = range(500,2401)
    Yt1 = []
    #Yt2 = []
    for x in Xt:
        yy1 = XS_NWA(x,1.0)
        #yy2 = XS_GPpred(x, 1.0)
        Yt1.append(yy1)
        #Yt2.append(yy2)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_yscale('log')
    ax.set_ylabel("Process cross-section (fb)")
    ax.set_xlabel("Top Partner Mass (GeV)")
    ax.plot(Xt, Yt1, linewidth=3, color='r',label='Predicted (LR)')
    #ax.plot(Xt, Yt2, linewidth=3, color='g',linestyle='--',label='Predicted (GP)')
    ax.scatter(X1, Y1, color='black', label='Computed')
    plt.legend()
    plt.savefig("../Figures/XS_SP.png")
    plt.close()

def XS_PPSP_plotter():

    X1 = sorted(XS_map_pair.keys())
    Y1 = []

    for x in X1:
        Y1.append(XS_map_pair[x])

    Xt = range(500,2001,10)
    Yt1 = [] # Gamma/M = 0.1%
    Yt2 = [] # Gamma/M = 1%
    Yt3 = [] # Gamma/M = 5%
    Yt4 = [] # Gamma/M = 10%

    for m in Xt:
        c = vlq(m*1.0)
        c.setGammaBRs(m*0.1/100., 0.98, 0.01)
        cw = c.getcVals()[0]
        #print c.getGamma()/m, cw, XS_NWA(m, cw), XS_NWA(m,1.)
        Yt1.append(XS_NWA(m, cw))
        c.setGammaBRs(m*1./100., 0.98, 0.01)
        cw = c.getcVals()[0]
        Yt2.append(XS_NWA(m, cw))
        c.setGammaBRs(m*5./100., 0.98, 0.01)
        cw = c.getcVals()[0]
        Yt3.append(XS_NWA(m, cw))
        c.setGammaBRs(m*10./100., 0.98, 0.01)
        cw = c.getcVals()[0]
        Yt4.append(XS_NWA(m, cw))
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_yscale('log')
    ax.set_ylabel("Process cross-section (fb)")
    ax.set_xlabel("Top Partner Mass (GeV)")
    ax.plot(Xt, Yt1, linewidth=2, color='r', label='SP Gamma/M = 0.1%')
    ax.plot(Xt, Yt2, linewidth=2, color='g',label='SP Gamma/M = 1%')
    ax.plot(Xt, Yt3, linewidth=2, color='b',label='SP Gamma/M = 5%')
    ax.plot(Xt, Yt4, linewidth=2, color='y',label='SP Gamma/M = 10%')
    #ax.plot(Xt, Yt2, linewidth=3, color='g',linestyle='--',label='Predicted (GP)')
    ax.plot(X1, Y1, color='black', linewidth=3, linestyle='--', label='PP')
    plt.legend()
    plt.savefig("../Figures/XS_SPPPcomp.png")
    plt.close()

def KvM_plotter():
    Xt = range(500,2001,10)
    Yt1 = [] # Gamma/M = 0.1%
    Yt2 = [] # Gamma/M = 1%
    Yt3 = [] # Gamma/M = 5%
    Yt4 = [] # Gamma/M = 10%

    for m in Xt:
        c = vlq(m*1.0)
        c.setGammaBRs(m*0.1/100., 0.98, 0.01)
        K = c.getKappa()
        #print c.getGamma()/m, cw, XS_NWA(m, cw), XS_NWA(m,1.)
        Yt1.append(K)
        c.setGammaBRs(m*1./100., 0.98, 0.01)
        K = c.getKappa()
        Yt2.append(K)
        c.setGammaBRs(m*5./100., 0.98, 0.01)
        K = c.getKappa()
        Yt3.append(K)
        c.setGammaBRs(m*10./100., 0.98, 0.01)
        K = c.getKappa()
        Yt4.append(K)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_yscale('log')
    ax.set_ylabel("$\kappa_T$")
    ax.set_xlabel("Top Partner Mass (GeV)")
    ax.plot(Xt, Yt1, linewidth=2, color='r', label='SP Gamma/M = 0.1%')
    ax.plot(Xt, Yt2, linewidth=2, color='g',label='SP Gamma/M = 1%')
    ax.plot(Xt, Yt3, linewidth=2, color='b',label='SP Gamma/M = 5%')
    ax.plot(Xt, Yt4, linewidth=2, color='y',label='SP Gamma/M = 10%')
    #ax.plot(Xt, Yt2, linewidth=3, color='g',linestyle='--',label='Predicted (GP)')
    #ax.plot(X1, Y1, color='black', linewidth=3, linestyle='--', label='PP')
    plt.legend()
    plt.savefig("../Figures/KvsM.png")
    plt.close()

def LimitReader_fromCSV(fname = "../Data/Limits_OSML.csv"):
    Limit_map = {}  # Map of mass -> limit for kappas: _map [k_index] [m_index] 
    f = open(fname, "r")
    for line in f:
        if len(line.strip()) <= 0: continue
        if line.strip()[0] == '#': continue
        vals = line.strip().split(',')
        try:
            m = float(vals[0])
            k = float(vals[1])
            lim = 1000.*float(vals[2])
        except:
            print line
            continue
        if k not in Limit_map.keys(): Limit_map[k] = {}
        Limit_map[k][m] = lim
    return Limit_map
'''
def LimitReader(Limit_map_all, label="exp"):
    Kappas = sorted(Limit_map_all.keys())
    Ms = sorted(Limit_map_all[Kappas[0]].keys())
    if label not in Limit_map_all[Kappas[0]][Ms[0]].keys():
        print "Label not recognized"
        return {}
    Limit_map = {}
    for k in Kappas:
        Limit_map[k] = {}
        for m in Ms:
            Limit_map[k][m] = Limit_map_all[k][m][label]
    return Limit_map

def LimitMapMaker(Loc):

    ## Makes a dictionary of limits
    ## For each kappa and mass, there is a dictionary entry: limit[kappa][mass], each entry being a dictionary
    ## Each entry stores six numbers, with keys ['obs', 'exp', '2up', '1up', '1dn', '2dn']
    ## These numbers are XS limits in pb
    ## Adapted for OSML_SP3l analysis, can be adapted for any analysis

    Limit_map_all = {}  # Map of mass -> limit for kappas: _map [k_index] [m_index]
    Ms = range(10, 24, 1)
    Ks = ['015', '020','025', '030', '035', '040', '045', '050', '060', '070', '080', '090', '100', '110', '120', '130', '140', '150', '160']
    for m in Ms:
        for k in Ks:
            MKtag = 'M' + str(m) + 'K' + k
            FitJobName = Loc + MKtag
            _dir = FitJobName + '/Limits/asymptotics/myLimit_CL95.root'
            if not os.path.exists(_dir):
                _dir = _dir.replace(MKtag, MKtag[1:])
                if not os.path.exists(_dir):
                    print _dir + " Doesn't Exist!!"
                    continue
            _f = ROOT.TFile(_dir)
            t_stats = _f.Get("stats")
            t_stats.GetEntry(0)
            kappa = int(k)/100.0
            if kappa not in Limit_map_all.keys(): Limit_map_all[kappa] = {}
            if m*100 not in  Limit_map_all[kappa].keys(): Limit_map_all[kappa][m*100] = {}
            Limit_map_all[kappa][m*100]["obs"] = t_stats.obs_upperlimit * 0.1
            Limit_map_all[kappa][m*100]["exp"] = t_stats.exp_upperlimit * 0.1
            Limit_map_all[kappa][m*100]["2up"] = t_stats.exp_upperlimit_plus2 * 0.1
            Limit_map_all[kappa][m*100]["1up"] = t_stats.exp_upperlimit_plus1 * 0.1
            Limit_map_all[kappa][m*100]["1dn"] = t_stats.exp_upperlimit_minus1 * 0.1
            Limit_map_all[kappa][m*100]["2dn"] = t_stats.exp_upperlimit_minus2 * 0.1
    return Limit_map_all


def GetLimit(Limit_map, m , k):

    ## The Limit_map is a map for limits of the form limit[k][m], each entry being a number 
    ## Use bilinear interpolation for limits in between

    Ks = sorted(Limit_map.keys())
    if k < min(Ks) or k > max(Ks): return -9999.0
    if m < min(Limit_map[min(Ks)].keys()) or m > max(Limit_map[min(Ks)].keys()): return -9999.0
    for ii in range(len(Ks)):
        if Ks[ii] == k:
            KLow, KHigh = k, k
            break
        elif k > Ks[ii] and k < Ks[ii+1]:
            KLow, KHigh = Ks[ii], Ks[ii+1]
            break
    Ms = sorted(Limit_map[Ks[0]].keys())
    for ii in range(len(Ms)):
        if Ms[ii] == m:
            MLow, MHigh = m, m
            break
        elif m > Ms[ii] and m < Ms[ii+1]:
            MLow, MHigh = Ms[ii], Ms[ii+1]
            break
    V11, V12, V21, V22 = Limit_map[KLow][MLow], Limit_map[KLow][MHigh], Limit_map[KHigh][MLow], Limit_map[KHigh][MHigh]
    dV_k = 0.5 * ( (V21 - V11) + (V22 - V12) ) / (KHigh - KLow + 1.e-12)
    dV_m = 0.5 * ( (V12 - V11) + (V22 - V21) ) / (MHigh - MLow + 1.e-12)
    V = V11 + dV_k * (k - KLow) + dV_m * (m - MLow) ## Replace by actual bilinear interpolation formula
    return V

def CMSstyle_Map(Limit_map):

    ## Creates plots of XS limits as a function of relative width and VLQ mass
    
    dM = 100.
    #M_min = min(Limit_map[min(Limit_map.keys())].keys()) - dM/2.
    M_min = 800.
    M_max = max(Limit_map[min(Limit_map.keys())].keys()) + dM/2.
    #print M_min, M_max
    Gmin = 5.
    Gmax = 40.
    dG = 5.
    h = ROOT.TH2D("limits_CMS", " ", int((M_max - M_min)/dM), M_min, M_max, int((Gmax - Gmin)/dG), Gmin, Gmax)
    h2 = ROOT.TH2D("exc_line_50", " ", int((M_max - M_min -dM)/1.), M_min+dM/2., M_max-dM/2., int((Gmax - Gmin)/1.), Gmin, Gmax)
    h3 = ROOT.TH2D("exc_line_25", " ", int((M_max - M_min -dM)/1.), M_min+dM/2., M_max-dM/2., int((Gmax - Gmin)/1.), Gmin, Gmax)
    c = vlq()
    for ii in range(h.GetNbinsX()):
        m = h.GetXaxis().GetBinCenter(ii+1)
        #print m
        for jj in range(h.GetNbinsY()):
            G = h.GetYaxis().GetBinCenter(jj+1)/100.
            #print G
            c.setMVLQ(m*1.0)
            c.setGammaBRs(G*m*1.0, 0.4, 0.3)
            k = c.getKappa()
            lim = GetLimit(Limit_map, m, k)
            #print m, G, k, lim
            h.Fill(m, G*100., lim)

    for ii in range(h2.GetNbinsX()):
        m = h2.GetXaxis().GetBinCenter(ii+1)
        if m < M_min + dM/2 and m > M_max - dM/2: continue
        for jj in range(h2.GetNbinsY()):
            G = h2.GetYaxis().GetBinCenter(jj+1)/100.
            #print G
            c.setMVLQ(m*1.0)
            c.setGammaBRs(G*m*1.0, 0.5, 0.5)
            k = c.getKappa()
            cw = c.getcVals()[0]
            lim50 = GetLimit(Limit_map, m, k)
            xs50 = XS_NWA(m, cw)*0.5/PNWA("WTZt",m, G)
            c.setGammaBRs(G*m*1.0, 0.5, 0.25)
            k = c.getKappa()
            cw = c.getcVals()[0]
            lim25 = GetLimit(Limit_map, m, k)
            xs25 = XS_NWA(m, cw)*0.25/PNWA("WTZt",m, G)
            #print m, cw, xs
            #if abs(xs50-lim50) < 0.1:
            #    print "50%", m, G*100.
            h2.Fill(m, G*100., xs50/lim50)
            #if abs(xs25/lim25) < 0.1 and m > 2000.:
            #    print "25%", m, G*100., xs25, lim25
            h3.Fill(m, G*100., xs25/lim25)
    cc2 = ROOT.TCanvas()
    cc2.cd()
    h2.SetStats(0)
    h2.Draw("COLZ")
    cc2.SaveAs("../Figures/CMS_Exclusion_50.png")
    cc3 = ROOT.TCanvas()
    cc3.cd()
    h3.SetStats(0)
    h3.Draw("COLZ")
    cc3.SaveAs("../Figures/CMS_Exclusion_25.png")
    cc = ROOT.TCanvas("C","C",1000,800)
    cc.cd()
    h.Draw("COLZ TEXT")
    h.SetStats(0)
    h.GetXaxis().SetTitle("M_{T} [GeV]")
    h.GetYaxis().SetTitle("#frac{#Gamma}{M_{T}} (%)")
    h.GetZaxis().SetTitle("Excluded cross-section (fb) at 95% CL")
    h2.SetLineColor(1)
    h2.SetLineStyle(1)
    h2.SetLineWidth(2)
    h2.SetContour(1,array([1.0]))
    h2.Draw("CONT2 same")
    h3.SetLineColor(2)
    h3.SetLineStyle(2)
    h3.SetLineWidth(2)
    h3.SetContour(1,array([1.0]))
    h3.Draw("CONT2 same")
    cc.SetRightMargin(0.15)
    f = ROOT.TFile("../Data/ALL_LIMIT_HISTS.root","UPDATE")
    h.Write(h.GetName(), ROOT.TObject.kWriteDelete)
    h2.Write(h2.GetName(), ROOT.TObject.kWriteDelete)
    h3.Write(h2.GetName(), ROOT.TObject.kWriteDelete)
    f.Close()
    cc.SaveAs("../Figures/CMSstyleLimits.png")

def ATLASstyle_Map(Limit_map, kfact=1.0, plotnametag = ""):

    ## Produces Mass limits as functions of cW and cZ

    M_min = min(Limit_map[min(Limit_map.keys())].keys()) 
    M_max = max(Limit_map[min(Limit_map.keys())].keys()) 
    dc = 0.01
    dM = 5.0
    mW = 80.4
    mZ = 91.2
    cws = arange(0.0+dc, 1.00001, dc)
    czs = arange(0.0+dc, 1.00001, dc) ## these are Wulzer couplings
    h = ROOT.TH2D("limits_ATLAS_" + str(int(round(kfact**2))) , " ", len(czs)-1 , min(czs), max(czs), len(cws)-1 , min(cws), max(cws))
    
    c = vlq()
    
    for ii in range(h.GetNbinsX()):
        cw = h.GetXaxis().GetBinCenter(ii+1)
        for jj in range(h.GetNbinsY()):    # these are Wulzer Couplings
            cz = h.GetYaxis().GetBinCenter(jj+1)*(mW/mZ) ## this is tilde coupling
            Mhigh = M_max
            c.setMVLQ(Mhigh*1.0)
            c.setc_Vals(cw, cz, kfact*cz)
            k = c.getKappa()
            G = c.getGamma()/Mhigh
            lim_high = GetLimit(Limit_map, Mhigh, k)
            xs_high = XS_NWA(Mhigh, cw)*c.getBRs()[1]/PNWA("WTZt",Mhigh, G)
            for m in arange(M_max, M_min, -1*dM):
                #print m, cw, cz
                Mlow = m
                c.setMVLQ(Mlow*1.0)
                c.setc_Vals(cw, cz, kfact*cz)
                k = c.getKappa()
                G = c.getGamma()/Mlow
                lim_low = GetLimit(Limit_map, Mlow, k)
                xs_low = XS_NWA(Mlow, cw)*c.getBRs()[1]/PNWA("WTZt",Mlow, G)
                if (lim_low - xs_low)*(lim_high - xs_high) < 0. and lim_low > 0. and lim_high > 0.:
                    h.Fill(cz*(mZ/mW), cw, (Mlow + Mhigh)/2.0)   # Wulzer coupling
                    print cz, cw, Mlow, Mhigh
                    break
                Mhigh = Mlow
                lim_high = lim_low
                xs_high = xs_low
    cc2 = ROOT.TCanvas("C","C",1000,800)
    cc2.cd()
    cc2.SetFrameFillColor(20)
    cc2.SetBottomMargin(0.15)
    cc2.SetLeftMargin(0.15)
    cc2.SetRightMargin(0.2)
    #h.SetMaximum(M_max)
    h.SetMinimum(M_min)
    h.SetStats(0)
    if kfact == 0.0: h.GetXaxis().SetTitle("#tilde{c}_{Z}  (#tilde{c}_{H} = 0)")
    elif kfact == 1.414: h.GetXaxis().SetTitle("#tilde{c}_{Z}  (#tilde{c}_{H} = #sqrt{2} \times #tilde{c}_{Z})")
    elif kfact == 1.0: h.GetXaxis().SetTitle("#sqrt{c_{Z,L}^{2} + c_{Z,R}^{2}}")
    h.GetYaxis().SetTitle("#sqrt{c_{W,L}^{2} + c_{W,R}^{2}}")
    h.GetZaxis().SetTitle("Mass Limit at 95% CL [GeV]     ")
    h.GetZaxis().SetTitleOffset(1.2)
    h.GetXaxis().SetTitleSize(0.05)
    h.GetYaxis().SetTitleSize(0.05)
    h.GetZaxis().SetTitleSize(0.05)
    #f = ROOT.TFile("Data/ALL_LIMIT_HISTS.root","UPDATE")
    #h.Write(h.GetName(), ROOT.TObject.kWriteDelete)
    h.Draw("COLZ")
    cc2.SaveAs("Plots/ATLASstyle_Limits_" + str(int(round(kfact**2))) + "_" + plotnametag + ".png")
    
def Newstyle_Map(Limit_map, kfact=1.0, plotnametag = ""):
    
    ## The new and preferred format by the OSML analysis
    ## Limits a function of relative decay width and BR(T -> Wb)
    
    dBR = 0.025
    BR_min = 0.05
    BR_max = 0.95
    #print M_min, M_max
    Gmin = 10.
    Gmax = 30.
    dG = 1.
    M_min = min(Limit_map[min(Limit_map.keys())].keys()) 
    M_max = max(Limit_map[min(Limit_map.keys())].keys())
    dM = 5.0
    h = ROOT.TH2D("New_limits_"+str(kfact), " ", int((BR_max - BR_min)/dBR), BR_min, BR_max, int((Gmax - Gmin)/dG), Gmin, Gmax)
    #h2 = ROOT.TH2D("exc_line", " ", int((M_max - M_min -dM)/1.), M_min+dM/2., M_max-dM/2., int((Gmax - Gmin)/1.), Gmin, Gmax)
    #h3 = ROOT.TH2D("exc_line", " ", int((M_max - M_min -dM)/1.), M_min+dM/2., M_max-dM/2., int((Gmax - Gmin)/1.), Gmin, Gmax)
    c = vlq()
    for ii in range(h.GetNbinsX()):
        BRW = h.GetXaxis().GetBinCenter(ii+1)
        BRZ = (1.0 - BRW)/(1 + kfact**2)
        for jj in range(h.GetNbinsY()):
            G = h.GetYaxis().GetBinCenter(jj+1)/100.
            Mhigh = M_max
            c.setMVLQ(Mhigh*1.0)
            c.setGammaBRs(G*Mhigh*1.0, BRW, BRZ)
            k = c.getKappa()
            cw = c.getc_Vals()[0]
            lim_high = GetLimit(Limit_map, Mhigh, k)
            xs_high = XS_NWA(Mhigh, cw)*BRZ/PNWA("WTZt",Mhigh, G)
            for m in arange(M_max, M_min-1.0, -1*dM):
                Mlow = m
                c.setMVLQ(Mlow*1.0)
                c.setGammaBRs(G*Mlow*1.0, BRW, BRZ)
                k = c.getKappa()
                cw = c.getc_Vals()[0]
                lim_low = GetLimit(Limit_map, Mlow, k)
                xs_low = XS_NWA(Mlow, cw)*BRZ/PNWA("WTZt",Mlow, G)
                if (lim_high - xs_high)*(lim_low - xs_low) < 0. and lim_high > 0. and lim_low > 0.:
                    h.Fill(BRW, G*100., (Mhigh + Mlow)/2.0)
                    break
                Mhigh = Mlow
                lim_high = lim_low
                xs_hig = xs_low
    cc = ROOT.TCanvas("cc","cc",1000,800)
    cc.cd()
    cc.SetFrameFillColor(20)
    cc.SetBottomMargin(0.15)
    cc.SetLeftMargin(0.15)
    cc.SetRightMargin(0.2)
    h.SetStats(0)
    h.GetXaxis().SetTitle("BR (T #rightarrow Wb)")
    h.GetXaxis().SetTitleSize(0.05)
    h.GetYaxis().SetTitle("#frac{#Gamma}{M}")
    h.GetYaxis().SetTitleSize(0.05)
    h.GetZaxis().SetTitle("Mass Limit at 95% CL    ")
    h.GetZaxis().SetTitleOffset(1.2)
    h.Draw("COLZ")
    #f = ROOT.TFile("../Data/ALL_LIMIT_HISTS.root","UPDATE")
    #h.Write(h.GetName(), ROOT.TObject.kWriteDelete)
    cc.SetRightMargin(0.2)
    cc.SaveAs("Plots/New_Exclusion_" + str(int(kfact)) + plotnametag + ".png")

def XSLimit_Plotter(Limit_map_all, k, Limit_map_2l = None, Limit_map_3l = None, plotnametag = ''):

    ## Creates XS vs Mass plots for one of the chosen kappas

    this_limits = Limit_map_all[k]
    Ms = sorted(this_limits.keys())
    _med = []
    _obs = []
    _2up = [] 
    _1up = []
    _1dn = []
    _2dn = []
    _theory = []
    if Limit_map_2l is not None:
        y_2l = []
    else:
        y_2l = None
    if Limit_map_3l is not None:
        y_3l = []
    else:
        y_3l = None
    c = vlq()
    for m in Ms:
        _med.append(this_limits[m]['exp'])
        _obs.append(this_limits[m]['obs'])
        _2up.append(this_limits[m]['2up'])
        _1up.append(this_limits[m]['1up'])
        _2dn.append(this_limits[m]['2dn'])
        _1dn.append(this_limits[m]['1dn'])
        if Limit_map_2l <> None: 
            y_2l.append(Limit_map_2l[k][m]['exp'])
        if Limit_map_3l <> None:
            y_3l.append(Limit_map_3l[k][m]['exp'])
        c.setMVLQ(m*1.0)
        c.setKappaxi(k, 0.5, 0.25)
        G = c.getGamma()/(m*1.0)
        cw = c.getc_Vals()[0]
        BRZ = c.getBRs()[1]
        _theory.append(XS_NWA(m*1.0, cw)*BRZ/PNWA("WTZt",m*1.0, G))
    for ii in range(len(Ms)): Ms[ii] = Ms[ii]*1.0
    plotname = "Plots/XSLimit_" + str(int(k*100)) + plotnametag +  ".png"
    oneDLimitPlotter(Ms, _2up, _1up, _1dn, _2dn, _med, _obs, _theory, True, k = k, ytype = "xs", plotname = plotname, _y2l = y_2l, _y3l = y_3l)
        
def CWLimit_Plotter(Limit_map_all, plotnametag = ''):

    ## Create cW vs M plot for singlet BRs

    Ks = sorted(Limit_map_all.keys())
    Ms = sorted(Limit_map_all[Ks[0]].keys())
    Ks_to_scan = arange(0.1, 1.61, 0.01)

    Limit_map_obs = LimitReader(Limit_map_all, "obs")
    Limit_map_exp = LimitReader(Limit_map_all, "exp")
    Limit_map_2up = LimitReader(Limit_map_all, "2up")
    Limit_map_1up = LimitReader(Limit_map_all, "1up")
    Limit_map_2dn = LimitReader(Limit_map_all, "2dn")
    Limit_map_1dn = LimitReader(Limit_map_all, "1dn")

    map_Limitmap = { "obs":Limit_map_obs,
                     "exp":Limit_map_exp,
                     "2up":Limit_map_2up,
                     "1up":Limit_map_1up,
                     "1dn":Limit_map_1dn,
                     "2dn":Limit_map_2dn 
                     }

    _obs = [-9999]*len(Ms)
    _exp = [-9999]*len(Ms)
    _2up = [-9999]*len(Ms)
    _1up = [-9999]*len(Ms)
    _1dn = [-9999]*len(Ms)
    _2dn = [-9999]*len(Ms)

    map_cLimit = {"obs":_obs,
                  "exp":_exp,
                  "2up":_2up,
                  "1up":_1up,
                  "1dn":_1dn,
                  "2dn":_2dn
                  }
    
    c= vlq()

    for lim_type in map_Limitmap.keys():
        this_limit_map = map_Limitmap[lim_type]
        this_limit_array = map_cLimit[lim_type]
        for m in Ms:
            mass = m*1.0
            c.setMVLQ(mass)
            k_low = Ks_to_scan[0]
            c.setKappaxi(k_low, 0.5, 0.25)
            cw_low = c.getc_Vals()[0]
            BRZ = c.getBRs()[1]
            G = c.getGamma()/mass
            lim_low = GetLimit(this_limit_map, mass, k_low)
            xs_low = XS_NWA(mass, cw_low)*BRZ/PNWA("WTZt",mass, G)
            for k in Ks_to_scan[1:]:
                k_high = k
                c.setKappaxi(k_high, 0.5, 0.25)
                cw_high = c.getc_Vals()[0]
                BRZ = c.getBRs()[1]
                G = c.getGamma()/mass
                lim_high = GetLimit(this_limit_map, mass, k_high)
                xs_high = XS_NWA(mass, cw_high)*BRZ/PNWA("WTZt",mass, G)
                if (lim_low - xs_low)*(lim_high - xs_high) < 0. and lim_low > 0. and lim_high > 0.:
                    this_limit_array[Ms.index(m)] = (cw_low + cw_high) / 2.0
                    break
                cw_low = cw_high
                lim_low = lim_high
                xs_low = xs_high
            
    indices_to_remove = []
    

    for ii in range(len(Ms)):
        for lim_type in map_Limitmap.keys():
            if map_cLimit[lim_type][ii] < 0 :
                indices_to_remove.append(ii)
                break

    print indices_to_remove

    newMs = []
    newobs = []
    newexp = []
    new2up = []
    new1up = []
    new1dn = []
    new2dn = []

    for ii in range(len(Ms)):
        if ii in indices_to_remove: continue
        newMs.append(Ms[ii]*1.0)
        newobs.append(_obs[ii])
        newexp.append(_exp[ii])
        new2up.append(_2up[ii])
        new1up.append(_1up[ii])
        new1dn.append(_1dn[ii])
        new2dn.append(_2dn[ii])

    plotname = "Plots/cWLimit" + plotnametag + ".png"
    oneDLimitPlotter(newMs, new2up, new1up, new1dn, new2dn, newexp, newobs, [], False, ytype = "coupling", plotname = plotname)

def MixAngleLimit_Plotter(Limit_map_all, multiplet='T', plotnametag = ""):

    ## Makes mixing angle vs mass plot for WTZt channel (this is a two branched plot)
    ## Trying make it adaptable for alternate multiplet structures
    ## Works for singlet now, working on triplet structures

    Ks = sorted(Limit_map_all.keys())
    Ms = sorted(Limit_map_all[Ks[0]].keys())

    Mmin = float(min(Ms))
    Mmax = float(max(Ms))
    dM = 2.0
    
    if multiplet == 'T': thetas_to_scan = arange(0.10, 3.14/2, 0.01) # results with theta < 0.15 is not trustworthy
    else: thetas_to_scan = append(arange(-3.14/8., -0.15, 0.01), arange(0.15,  3.14/8., 0.01))

    Limit_map_obs = LimitReader(Limit_map_all, "obs")
    Limit_map_exp = LimitReader(Limit_map_all, "exp")
    Limit_map_2up = LimitReader(Limit_map_all, "2up")
    Limit_map_1up = LimitReader(Limit_map_all, "1up")
    Limit_map_2dn = LimitReader(Limit_map_all, "2dn")
    Limit_map_1dn = LimitReader(Limit_map_all, "1dn")

    map_Limitmap = { "obs":Limit_map_obs,
                     "exp":Limit_map_exp,
                     "2up":Limit_map_2up,
                     "1up":Limit_map_1up,
                     "1dn":Limit_map_1dn,
                     "2dn":Limit_map_2dn 
                     }

    _obsM = []
    _expM = []
    _2upM = []
    _1upM = []
    _1dnM = []
    _2dnM = []

    _obsLim = []
    _expLim = []
    _2upLim = []
    _1upLim = []
    _1dnLim = []
    _2dnLim = []


    map_AngleLimit = {"obs":_obsLim,
                  "exp":_expLim,
                  "2up":_2upLim,
                  "1up":_1upLim,
                  "1dn":_1dnLim,
                  "2dn":_2dnLim,
                  }
    
    map_MLimit = {"obs":_obsM,
                  "exp":_expM,
                  "2up":_2upM,
                  "1up":_1upM,
                  "1dn":_1dnM,
                  "2dn":_2dnM,
                  }
    
    c = vlqx(multiplet=multiplet)
    smallest_m = 2500.0
    for lim_type in map_MLimit.keys():
        this_Limit_map = map_Limitmap[lim_type]
        this_Limits_array = map_AngleLimit[lim_type]
        this_Ms_array = map_MLimit[lim_type]
        for theta in thetas_to_scan:
            #cw = 1.41*sin(theta)
            #cz = sin(theta)*cos(theta)
            Mlow = Mmin
            c.setMVLQ(Mlow)
            #c.setc_Vals(cw, cz, cz)
            c.setAngleUL(theta)
            c.setCouplings()
            cw = c.getc_Vals()[0]
            k_low = c.getKappa()
            if k_low < min(Ks): continue
            lim_low = GetLimit(this_Limit_map, Mlow, k_low)
            BRZ = c.getBRs()[1]
            G = c.getGamma()/Mlow
            xs_low = XS_NWA(Mlow, cw)*BRZ/PNWA("WTZt",Mlow, G)
            for m in arange(Mmin+dM, Mmax-dM, dM):
                Mhigh = m
                c.setMVLQ(Mhigh)
                c.setAngleUL(theta)
                c.setCouplings()
                #c.setc_Vals(cw, cz, cz)
                cw = c.getc_Vals()[0]
                k_high = c.getKappa()
                if k_high > max(Ks): continue
                lim_high = GetLimit(this_Limit_map, Mhigh, k_high)
                BRZ = c.getBRs()[1]
                G = c.getGamma()/Mhigh
                xs_high = XS_NWA(Mhigh, cw)*BRZ/PNWA("WTZt",Mhigh, G)
                if (lim_low - xs_low)*(lim_high - xs_high) < 0. and lim_low > 0. and lim_high > 0.:
                    this_Limits_array.append(sin(theta))
                    this_Ms_array.append((Mlow + Mhigh) / 2.0)
                    break
                Mlow = Mhigh
                lim_low = lim_high
                xs_low = xs_high
        print lim_type
        #for ii in range(len(this_Limits_array)):
            #print int(this_Limits_array[ii]*100.0)/100.0, ":", this_Ms_array[ii]
            #print this_Ms_array
            #print "\n\n"
        if min(this_Ms_array) < smallest_m:
            smallest_m = min(this_Ms_array)

    for lim_type in map_MLimit.keys():
        this_Limits_array = map_AngleLimit[lim_type]
        this_Ms_array = map_MLimit[lim_type]
        if this_Ms_array[0] > smallest_m:
            extra_lim = interpolator(this_Ms_array[0], this_Limits_array[0], this_Ms_array[1], this_Limits_array[1], smallest_m)
            print lim_type, smallest_m, extra_lim
            map_AngleLimit[lim_type] = [extra_lim] + map_AngleLimit[lim_type]
            map_MLimit[lim_type] = [smallest_m] + map_MLimit[lim_type]
        if this_Ms_array[-1] > smallest_m:
            extra_lim = interpolator(this_Ms_array[-1], this_Limits_array[-1], this_Ms_array[-2], this_Limits_array[-2], smallest_m)
            print lim_type, smallest_m,extra_lim
            map_AngleLimit[lim_type] = map_AngleLimit[lim_type] + [extra_lim]
            map_MLimit[lim_type] = map_MLimit[lim_type] + [smallest_m]
            #this_Limits_array.append(extra_lim)
            #this_Ms_array.append(smallest_m)

    grobs = ROOT.TGraph(len(map_MLimit["obs"]))
    for ii in range(len(map_MLimit["obs"])): grobs.SetPoint(ii, map_MLimit["obs"][ii], map_AngleLimit["obs"][ii])
    grobs.SetLineColor(1)
    grobs.SetLineWidth(3)
    grmed = ROOT.TGraph(len(map_MLimit["exp"])) 
    for ii in range(len(map_MLimit["exp"])): grmed.SetPoint(ii, map_MLimit["exp"][ii], map_AngleLimit["exp"][ii])
    grmed.SetLineColor(1)
    grmed.SetLineWidth(3)
    grmed.SetLineStyle(2)
    gr2dn = ROOT.TGraph(len(map_MLimit["2dn"])) 
    for ii in range(len(map_MLimit["2dn"])): gr2dn.SetPoint(ii, map_MLimit["2dn"][ii], map_AngleLimit["2dn"][ii])
    gr2dn.SetLineColor(5)
    gr2dn.SetFillColor(5)
    gr2up = ROOT.TGraph(len(map_MLimit["2up"])) 
    for ii in range(len(map_MLimit["2up"])): gr2up.SetPoint(ii, map_MLimit["2up"][ii], map_AngleLimit["2up"][ii])
    gr2up.SetLineColor(5)
    gr2up.SetFillColor(0)
    gr1dn = ROOT.TGraph(len(map_MLimit["1dn"]))
    for ii in range(len(map_MLimit["1dn"])): gr1dn.SetPoint(ii, map_MLimit["1dn"][ii], map_AngleLimit["1dn"][ii])
    gr1dn.SetLineColor(3)
    gr1dn.SetFillColor(3)
    gr1up = ROOT.TGraph(len(map_MLimit["1up"]))
    for ii in range(len(map_MLimit["1up"])): gr1up.SetPoint(ii, map_MLimit["1up"][ii], map_AngleLimit["1up"][ii])
    gr1up.SetLineColor(5)
    gr1up.SetFillColor(5)

    leg = ROOT.TLegend(0.12,0.55,0.42,0.8)
    leg.SetFillColor(0)
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.SetTextFont(42)
    leg.SetTextSize(0.027)

    leg.AddEntry(gr2dn,"95% CL Exp. #pm 2#sigma","f")
    leg.AddEntry(gr1dn,"95% CL Exp. #pm 1#sigma","f")
    leg.AddEntry(grmed,"95% CL Exp. Limit","l")
    
    c_AngleLimit = ROOT.TCanvas("c_AngleLimit","c_AngleLimit",1000,800)
    c_AngleLimit.cd()
    if multiplet == 'T': ROOT.gPad.DrawFrame(min(Ms)*1.0, 0., max(Ms)*1.0, 1.0, " ;m_{T}[GeV];|sin#theta_{L}|")
    else:  ROOT.gPad.DrawFrame(min(Ms)*1.0, -0.4, max(Ms)*1.0, 0.4, " ;m_{T}[GeV]; sin#theta_{L}^{U}")
    gr2dn.Draw("f")   # change to f
    gr1dn.Draw("f same")
    gr1up.Draw("f same")
    gr2up.Draw("f same") # change to f
    grmed.Draw("same")
    leg.Draw("same")
    #c_AngleLimit.BuildLegend()
    Draw_ATLAS(0.6,0.2,"Internal")
    ROOT.gPad.RedrawAxis()
    plotname = "Plots/mixAngleLimit_" + multiplet + plotnametag + ".png"
    c_AngleLimit.SaveAs(plotname)
