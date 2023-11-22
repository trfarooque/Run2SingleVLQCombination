import os
import string
import random
import re
import time, getpass
import socket
import sys
import datetime
import glob
from array import array
from argparse import ArgumentParser
from ROOT import *
from numpy import log10, sqrt

from VLQCouplingCalculator import VLQCouplingCalculator as couplingCalculator
from VLQCrossSectionCalculator import *

sys.path.append(os.getenv("VLQCOMBDIR") + "/python/")
from CombUtils import *

##____________________________________________________________________________________________
def ExtractLimitFromRootFile(fname):

    infile = TFile(fname,"read")
    h_lim = infile.Get("limit")

    limits = {}
    limits["obs_lim"] = h_lim.GetBinContent(1)
    limits["exp_lim"] = h_lim.GetBinContent(2)
    limits["exp_lim_plus2"] = h_lim.GetBinContent(3)
    limits["exp_lim_plus1"] = h_lim.GetBinContent(4)
    limits["exp_lim_minus2"] = h_lim.GetBinContent(5)
    limits["exp_lim_minus1"] = h_lim.GetBinContent(6)
    infile.Close()

    return limits

##_____________________________________________________________________________________________
##
def FitFunctionAndDefineIntersection( Theory, Med, isData ):
    '''
    Function to determine the intersection between theory and limits by
    doing an exponential extrapolation between the different points for
    the expected/observe limit.
    '''
    diff_min = 1000
    for i in xrange(0,Theory.GetN()-1):

        x_ini_th = Double(-1)
        x_end_th = Double(-1)
        x_ini_ex = Double(-1)
        x_end_ex = Double(-1)

        y_ini_th = Double(-1)
        y_end_th = Double(-1)
        y_ini_ex = Double(-1)
        y_end_ex = Double(-1)

        Theory.GetPoint(i,x_ini_th, y_ini_th)
        Theory.GetPoint(i+1,x_end_th, y_end_th)

        Med.GetPoint(i,x_ini_ex, y_ini_ex)
        Med.GetPoint(i+1,x_end_ex, y_end_ex)

        Extra_Theory = TF1("Extra_Theory","expo",x_ini_th,x_end_th)
        Theory.Fit("Extra_Theory","RSNQ","",x_ini_th,x_end_th)
        Extra_Theory.SetLineColor(kBlack)
        Extra_Theory.SetLineStyle(2)

        Extra_Exp  = TF1("Extra_Exp","expo",x_ini_th,x_end_th)
        Med.Fit("Extra_Exp","RSQN","",x_ini_th,x_end_th)
        Extra_Exp.SetLineColor(kBlack)
        Extra_Exp.SetLineStyle(2)
        if not isData:
            Extra_Exp.Draw("same")
            ROOT.gPad.Modified(); ROOT.gPad.Update()

        for x in range(0,int(x_end_th-x_ini_th)):

            xmod=x_ini_th+x
            value_th = Extra_Theory.Eval(xmod)
            value_ex = Extra_Exp.Eval(xmod)
            diff = abs(value_th-value_ex)
            if(diff<diff_min):
                diff_min = diff
                x_int = xmod
                y_int = value_ex

    vertical = TGraph(2)
    vertical.SetPoint(0,x_int,0)
    vertical.SetPoint(1,x_int,y_int)
    vertical.SetLineStyle(2)
    if not isData:
        vertical.SetLineColor(kBlue)
    else:
        vertical.SetLineColor(kRed)
    vertical.SetLineWidth(2)

    return x_int,vertical

##.....................................................................................
##

def SumQuad(val1,val2):
    return sqrt(val1**2 + val2**2)
##.....................................................................................
##

gROOT.SetBatch(1)

##________________________________________________________
## OPTIONS
parser = ArgumentParser()
parser.add_argument("-i","--inputDir",help="location of the limit files ",dest="baseDir",default="")
parser.add_argument("-c", "--configs",help="",dest="configs",default="")
parser.add_argument("-o","--outDir",help="output folder",dest="outDir",default="./test/")

parser.add_argument("-k","--kappa",type=float,
                    help="kappa value of single VLQ signal",dest="Kappa",default=0.5)
parser.add_argument("-w","--brW",type=float,
                    help="Branching ratio to W of single VLQ signal",dest="BRW",default=0.5)

parser.add_argument("-e","--energy",help="energy",dest="energy",default="13")
parser.add_argument("-a","--addText",help="additional text to plot",dest="addText",default="")
parser.add_argument("-l","--lumi",help="luminosity",dest="lumi",default="139")
parser.add_argument("-d","--data",help="consider data",dest="data",action="store_true",default=False)
parser.add_argument("-x","--suffix",help="suffix of input directory of each mass point",dest="suffix",default="")
parser.add_argument("-t","--theory",help="draw theory",dest="drawTheory",action="store_true",default=False)
parser.add_argument("-n","--nonTheory",help="draw expected and observed limits",dest="drawNonTheory",action="store_true",default=True)
parser.add_argument("-f","--forceranges",help="force ranges",dest="forceRanges",action="store_true",default=False)
parser.add_argument("-s","--outSuffix",help="suffix in output file",dest="outSuffix",default="")
parser.add_argument("-b","--labels",help="list of labels",dest="labels",default="")
parser.add_argument("-r","--ratio",help="make ratio panel",dest="ratio",action="store_true",default=False)
parser.add_argument("-m","--masses",help="list of masses",dest="masses",default="")
parser.add_argument("-S","--signal",help="signal interpretation. TSinglet or TDoublet",dest="signal",default="TSinglet")

options = parser.parse_args()

baseDir=options.baseDir
configs=options.configs
outDir=options.outDir
energy=options.energy
addText=options.addText.replace("_"," ")
lumi=options.lumi
data=options.data
suffix=options.suffix
drawTheory=options.drawTheory
drawNonTheory=options.drawNonTheory
Kappa=options.Kappa
BRW=options.BRW
forceRanges=options.forceRanges
outSuffix=options.outSuffix
labels=options.labels
ratio=options.ratio
masses=options.masses
signal=options.signal

# Build labels
labels = list(map(str, labels.strip('[]').split(',')))

# Build configs
configs = list(map(str, configs.strip('[]').split(',')))

# Build masses
masses = list(map(str, masses.strip('[]').split(',')))

# if outSuffix != "":
#     outSuffix = '_'+outSuffix

os.system("mkdir -p "+outDir)

# Prepare for comparing multiple configurations in limit plots
doMulti = True if (len(configs)>1) else False
if len(labels) != len(configs):
    print("<!> ERROR !! Give labels of equal length when giving multiple input directories !!")
    sys.exit(-1)

if ratio and not doMulti:
    print("<!> ERROR !! Cannot do ratio panel if not given multiple input directories !!")
    sys.exit(-1)

#Data vs Asimov tag
datatag = "data" if data else "asimov_mu0"

#Signal label
signal_label = "\#splitline{{T}}{{ \#xi_{{W}}={} }}".format(BRW)

###
# Getting the values of the masses and cross-sections
###

sigtype=["WTHt","WTZt","ZTHt","ZTZt"]
#Masses = [m for m in range(1100,2100,100)]
Masses = [int(m) for m in masses]
vlqMode = 'T'
BRZ = 0.5* (1-BRW) #under assumption BRZ = BRH

# Key map: 0=W; 1=Z; 2=H
keyDictionary = {"WT": 0,"ZT": 1,"HT": 2}

masses = []
for M in Masses:

    vlq = couplingCalculator(M, vlqMode)
            
    ## Set the VLQ Parameters: kappa, xi parameterization as in https://arxiv.org/pdf/1305.4172.pdf
    vlq.setKappaxi(Kappa, BRW, BRZ) # kappa, xiW, xiZ. xiH = 1 - xiW - xiZ
            
    cVals = vlq.getcVals()
    BR = vlq.getBRs()
    Gamma = vlq.getGamma()

    TotalXSec = 0
    for sig in sigtype:
        
        prodIndex = keyDictionary[sig[:2:]]
        decayIndex = keyDictionary[sig[2::].upper()]
                
        XSec = XS_NWA(M, cVals[prodIndex], sig[:2:])*BR[decayIndex]/PNWA(proc=sig, mass=M, GM=Gamma/M)
        TotalXSec += XSec

        #print("process : ",sig," M =",M,", kappa =",Kappa,", BRW =",BRW,", width/mass =",Gamma/M)
        #print("Xsec = ", XSec, "pb")

    XSecErrors = XSUncertainty(M)
    XSecErrorUp = XSecErrors[0]*TotalXSec
    XSecErrorDown = XSecErrors[1]*TotalXSec
    
    masses +=[{'name': getSigTag(M,Kappa,BRW), 'mass':M, 'mass_theory':M, 'xsec': 0.1, 'xsecTheory':TotalXSec, 'errUp':XSecErrorUp, 'errDown':XSecErrorDown}]

###
# Effectively building the plots
###
tg_theory = TGraphAsymmErrors()
tg_obs = [TGraph() for i in range(len(configs))]
tg_exp = [TGraph() for i in range(len(configs))]
tg_exp1s = [TGraph() for i in range(len(configs))]
tg_exp2s = [TGraph() for i in range(len(configs))]

tg_ratio = [TGraph() for i in range(len(configs))]

###################### Fill all required TGraphs ########################
if drawTheory:
    # Theory plot
    for iMass in range(len(masses)):
        tg_theory.SetPoint(iMass,masses[iMass]['mass_theory'],masses[iMass]['xsecTheory'])
        tg_theory.SetPointError(iMass,0,0,masses[iMass]['errDown'],masses[iMass]['errUp'])

if drawNonTheory:

    counter = -1
    for n,cfg in enumerate(configs):
        counter = -1
        for mass in masses:

            indir = baseDir + '/' + cfg + '/'
            pathname = indir + cfg + "_limits_" + getSigTag(mass['mass'],Kappa,BRW) + "_" + datatag + ".root"
            files = glob.glob(pathname)

            if len(files)==0 or len(files)>1:
                print("<!> ERROR for", cfg, "mass", mass['mass']," !! --> nFiles = ",len(files))
                continue
            counter+=1
            limpoint = ExtractLimitFromRootFile(files[0])
            this_xsec = mass['xsec']

            tg_obs[n].SetPoint(counter,mass['mass'],limpoint["obs_lim"]*this_xsec)
            tg_exp[n].SetPoint(counter,mass['mass'],limpoint["exp_lim"]*this_xsec)
            tg_exp1s[n].SetPoint(counter,mass['mass'],limpoint["exp_lim_plus1"]*this_xsec)
            tg_exp2s[n].SetPoint(counter,mass['mass'],limpoint["exp_lim_plus2"]*this_xsec)
            tg_exp1s[n].SetPoint(2*len(masses)-counter-1,mass['mass'],limpoint["exp_lim_minus1"]*this_xsec)
            tg_exp2s[n].SetPoint(2*len(masses)-counter-1,mass['mass'],limpoint["exp_lim_minus2"]*this_xsec)
                
            if ratio:
                tg_ratio[n].SetPoint(counter,mass['mass'],tg_exp[n].Eval(mass['mass'])
                                     /tg_exp[0].Eval(mass['mass']))

###################### All required TGraphs filled ########################

cols = [kBlack,kBlue+1,kMagenta,kOrange+4] # max compare 4 configurations
fills = [3002,3004,3005,3007]

#Make multigraph and legend, set graph styles and add all required graphs to multigraph and to legend

leg = TLegend(0.57,0.6,0.82,0.9)
leg.SetFillColor(0)
leg.SetLineColor(0)

tmg_main = TMultiGraph()
tmg_ratio = TMultiGraph()

if drawNonTheory:

    for n,cfg in enumerate(configs):

        if ratio:
            tg_ratio[n].SetLineColor(cols[n])
            tg_ratio[n].SetLineWidth(3)
            tg_ratio[n].SetLineStyle(2)
            tmg_ratio.Add(tg_ratio[n], "l")

        if n==0:
            tg_exp2s[n].SetLineColor(kYellow)
            tg_exp2s[n].SetFillColor(kYellow)
            print("Adding exp line :",n)
            tmg_main.Add(tg_exp2s[n], "fl")
            leg.AddEntry(tg_exp2s[n],"95% CL expected limit #pm2#sigma","f")
            
            tg_exp1s[n].SetLineColor(kGreen)
            tg_exp1s[n].SetFillColor(kGreen)
            tmg_main.Add(tg_exp1s[n], "fl")
            leg.AddEntry(tg_exp1s[n],"95% CL expected limit #pm1#sigma","f")

            tg_exp[n].SetLineColor(kBlack)
            tg_exp[n].SetLineWidth(3)
            tg_exp[n].SetLineStyle(2)
            tmg_main.Add(tg_exp[n], "l")
            leg.AddEntry(tg_exp[n],"95% CL expected limit","l")
        
            if data:
                tg_obs[n].SetLineColor(kBlack)
                tg_obs[n].SetLineWidth(3)
                tg_obs[n].SetLineStyle(1)
                tmg_main.Add(tg_obs[n], "l")
                leg.AddEntry(tg_obs[n],"95% CL observed limit","l")

        else:
            tg_exp[n].SetLineColor(cols[n])
            tg_exp[n].SetFillColor(cols[n])
            tg_exp[n].SetFillStyle(3005)
            tg_exp[n].SetLineWidth(3)
            tg_exp[n].SetLineStyle(2)
            print("Adding exp line :",n)
            tmg_main.Add(tg_exp[n], "l")
            leg.AddEntry(tg_exp[n],labels[n],"l")


if drawTheory:
    tg_theory.SetLineColor(kRed)
    tg_theory.SetFillColor(kRed-9)
    print("Adding theory")
    tmg_main.Add(tg_theory, "4lx")
    leg.AddEntry(tg_theory,"Theory (NLO)","lf")



###
# Creating the canvas
###

if ratio:
    can = TCanvas("1DLimit_"+signal,"1DLimit_"+signal,1000,1150)
    pad1 = TPad("pad1","",0,0.4,1,1)
    pad1.SetBottomMargin(0.15)
    pad1.SetLeftMargin(0.15)
    pad1.SetRightMargin(0.03)
    pad1.SetTopMargin(0.05)
    pad1.Draw()
    ROOT.gPad.Modified(); ROOT.gPad.Update()
    pad2 = TPad("pad2","",0,0.00,1,0.4)
    pad2.SetBottomMargin(0.15)
    pad2.SetLeftMargin(0.15)
    pad2.SetRightMargin(0.03)
    pad2.SetTopMargin(0.03)
    pad2.Draw()
    ROOT.gPad.Modified(); ROOT.gPad.Update()

else:
    can = TCanvas("1DLimit_"+signal,"1DLimit_"+signal,1000,800)
    can.SetBottomMargin(0.15)
    can.SetLeftMargin(0.15)
    can.SetRightMargin(0.05)
    can.SetTopMargin(0.05)

###
# Making axis limits
###
#if forceRanges:
#    ylim_min = 0.
#    ylim_max = 0.27
#    ylim_min_log = 0.0015
#    ylim_max_log = 15
#
#else:
#    if drawTheory:
#        if drawNonTheory:
#            ymin = tg_theory.GetHistogram().GetMinimum() if tg_theory.GetHistogram().GetMinimum() < min([t.GetHistogram().GetMinimum() for t in tg_exp2s]) else min([t.GetHistogram().GetMinimum() for t in tg_exp2s])
#            ymax = tg_theory.GetHistogram().GetMaximum() if tg_theory.GetHistogram().GetMaximum() > max([t.GetHistogram().GetMaximum() for t in tg_exp2s]) else max([t.GetHistogram().GetMaximum() for t in tg_exp2s])
#        else:
#            ymin = tg_theory.GetHistogram().GetMinimum()
#            ymax = tg_theory.GetHistogram().GetMaximum()
#    else:
#        ymin = min([t.GetHistogram().GetMinimum() for t in tg_exp2s])
#        ymax = max([t.GetHistogram().GetMaximum() for t in tg_exp2s])
#    
#    ylim_min = ymin - 0.2*(ymax-ymin) if (ymin-0.2*(ymax-ymin)) > 0. else 0.
#    ylim_max = ymin + 1.25*(ymax-ymin)
#    ylim_min_log = 10**(log10(ymin)-0.35*abs(log10(ymax)-log10(ymin)))
#    ylim_max_log = 10**(log10(ymax)+0.7*abs(log10(ymax)-log10(ymin)))
#    print(ymin, ylim_min_log, ymax, ylim_max_log)

###
# Limits
###
if ratio:
    #first draw the ratio plots
    pad2.cd()
    tmg_ratio.Draw("a")
    pad1.cd()
else:
    can.cd()

tmg_main.Draw("a")

tmg_main.GetXaxis().SetNdivisions(406)
tmg_main.SetTitle("")
tmg_main.GetXaxis().SetTitle("m_{T} [GeV]")
#tmg_main.GetYaxis().SetTitle("#sigma(pp #rightarrow qb(T #rightarrow Ht/Zt)) [pb]")
tmg_main.GetYaxis().SetTitle("#sigma(pp #rightarrow qbT )[pb]")
tmg_main.GetHistogram().GetXaxis().SetLabelSize(tmg_main.GetHistogram().GetXaxis().GetLabelSize()*1.3)
tmg_main.GetHistogram().GetYaxis().SetLabelSize(tmg_main.GetHistogram().GetYaxis().GetLabelSize()*1.3)
tmg_main.GetHistogram().GetXaxis().SetTitleSize(tmg_main.GetHistogram().GetXaxis().GetTitleSize()*1.6)
tmg_main.GetHistogram().GetYaxis().SetTitleSize(tmg_main.GetHistogram().GetYaxis().GetTitleSize()*1.6)
tmg_main.GetHistogram().GetXaxis().SetTitleOffset(1.32)
tmg_main.GetHistogram().GetYaxis().SetTitleOffset(1.4)
ROOT.gPad.Modified(); ROOT.gPad.Update()


leg.SetTextSize(0.032)
leg.Draw()


#Intersections
#intersx=FitFunctionAndDefineIntersection(tg_theory,tg_exp,isData=False )
#print "Expected limit: " + `intersx[0]`
#intersx[1].Draw("lp")
#if(data):
#    intersxData=FitFunctionAndDefineIntersection(tg_theory,tg_obs,isData=True )
#    print "Observed limit: " + `intersxData[0]`


tl_atlas = TLatex(0.19,0.88,"ATLAS")
tl_atlas.SetNDC()
tl_atlas.SetTextFont(72)
tl_atlas.SetTextSize(tl_atlas.GetTextSize()*0.85)
tl_atlas.Draw()
tl_int = TLatex(0.31,0.88,"Internal")#"Internal")
tl_int.SetNDC()
tl_int.SetTextFont(42)
tl_int.SetTextSize(tl_int.GetTextSize()*0.85)
tl_int.Draw()
tl_energy = TLatex(0.19,0.82,"#sqrt{s} = "+energy+" TeV, "+lumi+" fb^{-1}")
tl_energy.SetNDC()
tl_energy.SetTextFont(42)
tl_energy.SetTextSize(tl_energy.GetTextSize()*0.85)
tl_energy.Draw()
ROOT.gPad.Modified(); ROOT.gPad.Update()
if(addText!=""):
    tl_addtext = TLatex(0.19,0.18,addText)
    tl_addtext.SetNDC()
    tl_addtext.SetTextFont(42)
    tl_addtext.SetTextSize(tl_addtext.GetTextSize()*0.85)
    tl_addtext.Draw()
    ROOT.gPad.Modified(); ROOT.gPad.Update()

#if signal_label!="":
#    leg.AddEntry(TObject(), " ", "")
#    leg.AddEntry(TObject(), signal_label+", #kappa=%s"%Kappa, "")


gPad.RedrawAxis()
can.SetTickx()
can.SetTicky()
ROOT.gPad.Modified(); ROOT.gPad.Update()

print(can.GetName())
canvName = outDir + "/" + signal.upper()+"_"+lumi.replace(".","")+outSuffix+".png"

can.SaveAs(canvName)

# No log plot if comparison
