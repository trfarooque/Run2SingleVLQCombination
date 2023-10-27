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


    #print('Displaying limits information for ',fname)
    #for key,val in limits.items():
    #    print(key,' : ',val)
    #print('\n')

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
parser.add_argument("-i","--inputDir",help="location of the log files ",dest="baseDir",default="")
parser.add_argument("-c", "--configs",help="",nargs='*',dest="configs",default="")
parser.add_argument("-o","--outDir",help="output folder",dest="outDir",default="./test/")
#parser.add_argument("-s","--signal",help="signal sample",dest="signal",default="TTD")
#parser.add_argument("-m","--mode",help="single VLQ signal mode", dest="mode", default="WTHt")

parser.add_argument("-k","--kappa",type=float,
                    help="kappa value of single VLQ signal",dest="Kappa",default=0.5)
parser.add_argument("-w","--brW",type=float,
                    help="Branching ratio to W of single VLQ signal",dest="BRW",default=0.5)

parser.add_argument("-e","--energy",help="energy",dest="energy",default="13")
parser.add_argument("-a","--addText",help="additional text to plot",dest="addText",default="")
parser.add_argument("-l","--lumi",help="luminosity",dest="lumi",default="140")
parser.add_argument("-d","--data",help="consider data",dest="data",action="store_true",default=False)
parser.add_argument("-x","--suffix",help="suffix of input directory of each mass point",dest="suffix",default="")
parser.add_argument("-t","--theory",help="draw theory",dest="drawTheory",action="store_true",default=False)
parser.add_argument("-n","--nonTheory",help="draw expected and observed limits",dest="drawNonTheory",action="store_true",default=True)
parser.add_argument("-f","--forceranges",help="force ranges",dest="forceRanges",action="store_true",default=False)
parser.add_argument("-s","--outSuffix",help="suffix in output file",dest="outSuffix",default="")
parser.add_argument("-b","--labels",help="list of labels",dest="labels",default="")
parser.add_argument("-r","--ratio",help="make ratio panel",dest="ratio",action="store_true",default=False)

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

signal="TSinglet"

# Build labels
labels = list(map(str, labels.strip('[]').split(',')))

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

###
# Getting the values of the masses and cross-sections
###
masses = []
sigtype=["WTHt","WTZt","ZTHt","ZTZt"]
Masses = [m for m in range(1100,2100,100)]
vlqMode = 'T'
BRZ = 0.5* (1-BRW) #under assumption BRZ = BRH

# Key map: 0=W; 1=Z; 2=H
keyDictionary = {"WT": 0,"ZT": 1,"HT": 2}
 
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
                
        #print("sigtype : ",sig," prodIndex : ",prodIndex," decayIndex : ",decayIndex)
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

# if comparing mutliple configurations
tg_obs = TGraph()
tg_exp = TGraph()
tg_exp1s = TGraph()
tg_exp2s = TGraph()
    
# All limits

# Get number of good mass points (instead of len(masses))
goodmasses = []
for mass in masses:
    goodmasses.append(mass['mass'])

# Multiple configurations
counter = -1
for n,cfg in enumerate(configs):
    counter = -1
    for mass in masses:

        indir = baseDir + '/' + cfg + '/'
        pathname = indir + cfg + "_limits_" + getSigTag(mass['mass'],Kappa,BRW) + "_" + datatag + ".root"

        print(pathname)
        files = glob.glob(pathname)
        if len(files)==0: ## TF 000
            pathname = indir + cfg + "_limits_" + getSigTag(mass['mass'],Kappa,BRW) + "_asimov_mu0" + ".root"
            files = glob.glob(pathname)

        if len(files)==0 or len(files)>1:
            print("<!> ERROR for mass ",mass['mass']," !! --> nFiles = ",len(files))
            continue
        counter+=1
        limpoint = ExtractLimitFromRootFile(files[0])
        this_xsec = mass['xsec']
        print(" Mass: ", mass['mass'], " mu : ", limpoint["obs_lim"], " xsec : ", this_xsec)

        tg_obs.SetPoint(counter,mass['mass'],limpoint["obs_lim"]*this_xsec)
        tg_exp.SetPoint(counter,mass['mass'],limpoint["exp_lim"]*this_xsec)
        tg_exp1s.SetPoint(counter,mass['mass'],limpoint["exp_lim_plus1"]*this_xsec)
        tg_exp2s.SetPoint(counter,mass['mass'],limpoint["exp_lim_plus2"]*this_xsec)
        tg_exp1s.SetPoint(2*len(goodmasses)-counter-1,mass['mass'],limpoint["exp_lim_minus1"]*this_xsec)
        tg_exp2s.SetPoint(2*len(goodmasses)-counter-1,mass['mass'],limpoint["exp_lim_minus2"]*this_xsec)

###
# Creating signal label
###
signal_label = "\#splitline{{T}}{{ \#xi_{{W}}={} }}".format(BRW)

###
# Creating the canvas
###
can = TCanvas("1DLimit_"+signal,"1DLimit_"+signal,1000,800)
can.SetBottomMargin(0.15)
can.SetLeftMargin(0.15)
can.SetRightMargin(0.05)
can.SetTopMargin(0.05)

leg = TLegend(0.57,0.6,0.82,0.9)
leg.SetFillColor(0)
leg.SetLineColor(0)

###
# Making axis limits
###
if forceRanges:
    ylim_min = 0.
    ylim_max = 0.27
    ylim_min_log = 0.0015
    ylim_max_log = 15

else:
    ymin = tg_exp2s.GetHistogram().GetMinimum()
    ymax = tg_exp2s.GetHistogram().GetMaximum()            
    
    ylim_min = ymin - 0.2*(ymax-ymin) if (ymin-0.2*(ymax-ymin)) > 0. else 0.
    ylim_max = ymin + 1.25*(ymax-ymin)
    ylim_min_log = 10**(log10(ymin)-0.35*abs(log10(ymax)-log10(ymin)))
    ylim_max_log = 10**(log10(ymax)+0.7*abs(log10(ymax)-log10(ymin)))
    print(ymin, ylim_min_log, ymax, ylim_max_log)

###
# Limits
###
cols = [kBlue+1,kRed,kBlack,kOrange+4] # max compare 4 configurations
fills = [3002,3004,3005,3007]

tg_exp2s.SetLineColor(kYellow)
tg_exp2s.SetFillColor(kYellow)
tg_exp2s.GetXaxis().SetLimits(goodmasses[0],goodmasses[-1])
tg_exp2s.SetMinimum(ylim_min)
tg_exp2s.SetMaximum(ylim_max)
tg_exp2s.GetXaxis().SetNdivisions(406)
tg_exp2s.SetTitle("")
tg_exp2s.GetXaxis().SetTitle("m_{T} [GeV]")
tg_exp2s.GetYaxis().SetTitle("#sigma(pp #rightarrow qb(T #rightarrow Ht/Zt)) [pb]")
tg_exp2s.GetHistogram().GetXaxis().SetLabelSize(tg_exp2s.GetHistogram().GetXaxis().GetLabelSize()*1.3)
tg_exp2s.GetHistogram().GetYaxis().SetLabelSize(tg_exp2s.GetHistogram().GetYaxis().GetLabelSize()*1.3)
tg_exp2s.GetHistogram().GetXaxis().SetTitleSize(tg_exp2s.GetHistogram().GetXaxis().GetTitleSize()*1.6)
tg_exp2s.GetHistogram().GetYaxis().SetTitleSize(tg_exp2s.GetHistogram().GetYaxis().GetTitleSize()*1.6)
tg_exp2s.GetHistogram().GetXaxis().SetTitleOffset(1.32)
tg_exp2s.GetHistogram().GetYaxis().SetTitleOffset(1.4)
tg_exp2s.Draw("af")
ROOT.gPad.Modified(); ROOT.gPad.Update()

tg_exp1s.SetLineColor(kGreen)
tg_exp1s.SetFillColor(kGreen)
tg_exp1s.Draw("f")
ROOT.gPad.Modified(); ROOT.gPad.Update()

########################

tg_exp.SetLineColor(kBlack)
tg_exp.SetLineWidth(3)
tg_exp.SetLineStyle(2)
tg_exp.Draw("l same")
ROOT.gPad.Modified(); ROOT.gPad.Update()
    
if data:
    tg_obs.SetLineColor(kBlack)
    tg_obs.SetLineWidth(3)
    tg_obs.SetLineStyle(1)
    tg_obs.Draw("l")
    ROOT.gPad.Modified(); ROOT.gPad.Update()
    
    leg.AddEntry(tg_obs,"95% CL observed limit","l")
    
leg.AddEntry(tg_exp,"95% CL expected limit","l")
leg.AddEntry(tg_exp1s,"95% CL expected limit #pm1#sigma","f")
leg.AddEntry(tg_exp2s,"95% CL expected limit #pm2#sigma","f")

leg.SetTextSize(0.032)
leg.Draw()
ROOT.gPad.Modified(); ROOT.gPad.Update()

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
print(canvName)
for key in can.GetListOfPrimitives():
    print(key) 

can.SaveAs(canvName)
print("written")


