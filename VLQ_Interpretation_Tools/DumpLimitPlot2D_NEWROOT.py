import os
import string
import random
import re
import time, getpass
import socket
import sys
import datetime
from optparse import OptionParser
from ROOT import *

import glob

sys.path.append("/data/at3/scratch2/farooque/SignalRWUpdate/VLQAnalysisFramework/build/x86_64-centos7-gcc8-opt/python/SignalTools/")
from VLQCouplingCalculator import VLQCouplingCalculator as couplingCalculator
from VLQCrossSectionCalculator import *

from array import array

####
# Setup using: lsetup "root 6.22.00-x86_64-centos7-gcc8-opt"
# not regular VLQAnalysisFramework setup chain
####

####
# Example command format:
# python DumpLimitPlot2D_NEWROOT.py -i <TRExFitter output folder>/Results/ -o <output folder> -s <TS or TD> -m ALL -l 139 -d -t -n -c <suffix>
####

##_____________________________________________________________________________________________
##
def FitFunctionAndDefineIntersection( Theory, Med ):
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
        
        Extra_Exp  = TF1("Extra_Exp","expo",x_ini_th,x_end_th)
        Med.Fit("Extra_Exp","RSQN","",x_ini_th,x_end_th)
        
        for x in range(0,int(x_end_th-x_ini_th)):
            
            xmod=x_ini_th+x
            value_th = Extra_Theory.Eval(xmod)
            value_ex = Extra_Exp.Eval(xmod)
            diff = abs(value_th-value_ex)
            if(diff<diff_min):
                diff_min = diff
                x_int = xmod
                y_int = value_ex

    return x_int
##.....................................................................................
##

gROOT.SetBatch(1)

##________________________________________________________
## OPTIONS
parser = OptionParser()
parser.add_option("-i","--inputDir",help="location of the log files ",dest="inDir",default="")
parser.add_option("-o","--outDir",help="output folder",dest="outDir",default="./test/")
parser.add_option("-s","--signal",help="signal sample",dest="signal",default="TTD")
parser.add_option("-m","--mode",help="single VLQ signal mode", dest="mode", default="WTHt")
parser.add_option("-e","--energy",help="energy",dest="energy",default="13")
parser.add_option("-a","--addText",help="additional text to plot",dest="addText",default="")
parser.add_option("-l","--lumi",help="luminosity",dest="lumi",default="3.2")
parser.add_option("-d","--data",help="consider data",dest="data",action="store_true",default=False)
parser.add_option("-x","--suffix",help="suffix of input directory of each mass point",dest="suffix",default="")
parser.add_option("-t","--theory",help="draw theory",dest="drawTheory",action="store_true",default=False)
parser.add_option("-n","--nonTheory",help="draw expected and observed limits",dest="drawNonTheory",action="store_true",default=False)
parser.add_option("-f","--forceranges",help="force ranges",dest="forceRanges",action="store_true",default=False)
parser.add_option("-c","--outsuffix",help="suffix in output file",dest="outSuffix",default="")
parser.add_option("-b","--labels",help="list of labels",dest="labels",default="")
parser.add_option("-r","--ratio",help="make ratio panel",dest="ratio",action="store_true",default=False)
parser.add_option

(options, args) = parser.parse_args()
inDir=options.inDir
outDir=options.outDir
signal=options.signal
mode=options.mode
energy=options.energy
addText=options.addText.replace("_"," ")
lumi=options.lumi
data=options.data
suffix=options.suffix
drawTheory=options.drawTheory
drawNonTheory=options.drawNonTheory
forceRanges=options.forceRanges
outSuffix=options.outSuffix
labels=options.labels
ratio=options.ratio

# Build labels
labels = map(str, labels.strip('[]').split(','))

if outSuffix != "":
    outSuffix = '_'+outSuffix

os.system("mkdir -p "+outDir)

signal_label = ""
if(signal=="TTD") or (signal=="TD"):
    signal_label = "T doublet"
elif(signal=="TTS") or (signal=="TS"):
    signal_label = "T singlet"

###
# Getting the values of the masses and cross-sections
###
print signal
masses = []
gms = []
if(signal.upper()=="TS" or signal.upper()=="TD"):
    if(mode.upper()=="WTHT"):
        sigtype=["WTHt"]
        signal_label += " (T(#rightarrow Ht)qb)"
    elif(mode.upper()=="WTZT"):
        sigtype=["WTZt"]
        signal_label += " (T(#rightarrow Zt)qb)"            
    elif(mode.upper()=="ZTHT"):
        sigtype=["ZTHt"]
        signal_label += " (T(#rightarrow Ht)qt)"
    elif(mode.upper()=="ZTZT"):
        sigtype=["ZTZt"]
        signal_label += " (T(#rightarrow Zt)qt)"
    elif(mode.upper()=="ALL"):
        sigtype=["WTHt","WTZt","ZTHt","ZTZt"]
    else:
        print "<!> ERROR !! Unrecognized single VLQ mode! Valid options are WTHt, WTZt, ZTHt, ZTZt, or all."
        sys.exit(-1)

elif(signal.upper()=="WTHT" or signal.upper()=="WTZT" or signal.upper()=="ZTHT" or signal.upper()=="ZTZT"):
    sigtype="WTHt"
    xsec = 0.1
    if(signal.upper()=="WTHT"):
       sigtype="WTHt"
    if(signal.upper()=="ZTHT"):
       sigtype="ZTHt"
       xsec = 0.2
    if(signal.upper()=="WTZT"):
       sigtype="WTZt"
    if(signal.upper()=="ZTZT"):
       sigtype="ZTZt"
       xsec = 0.2


Masses = [m for m in range(1000,2200,100)]
Kappas = [0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6]

vlqMode = 'T'

for M in Masses:
    for Kappa in Kappas:

        if (signal.upper()=="TS" or signal.upper()=="TD"):
            if mode.upper()=="ALL":
                signalName = "sVLQ_"+signal.upper() + 'K'+str(int(100*Kappa))+str(M)
                lmsuffix = 'low_mass'
                nmsuffix = 'nom_mass'
            else:
                signalName = sigtype[0]+str(M)+'K'+str(int(100*Kappa))
                lmsuffix = ''
                nmsuffix = ''
        else:
            signalName = sigtype[0]+str(M)+'K'+str(int(100*Kappa))
            masses += [{'name': signalName, 'mass':M, 'mass_theory':M, 'xsec':xsec, 'xsecTheory': 0.1, 'errUp':0., 'errDown':0., "Kappa": Kappa}]

        if not (signal.upper()=="TS" or signal.upper()=="TD"):
            continue

        vlqSinglet = couplingCalculator(M, vlqMode)
        vlqDoublet = couplingCalculator(M, vlqMode)
        vlqSinglet.setKappaxi(Kappa, 0.5, 0.25) # kappa, xiW, xiZ. xiH = 1 - xiW - xiZ
        vlqDoublet.setKappaxi(Kappa, 0., 0.5) # kappa, xiW, xiZ. xiH = 1 - xiW - xiZ
        
        cSinglet = vlqSinglet.getcVals()
        cDoublet = vlqDoublet.getcVals()
        BRSinglet = vlqSinglet.getBRs()
        BRDoublet = vlqDoublet.getBRs()
        
        GammaSinglet = vlqSinglet.getGamma()
        GammaDoublet = vlqDoublet.getGamma()

        # Key map: 0=W; 1=Z; 2=H
        keyDictionary = {"WT": 0,"ZT": 1,"HT": 2}
        
        TotalXSecSinglet = 0
        TotalXSecDoublet = 0
        for sig in sigtype:

            prodIndex = keyDictionary[sig[:2:]]
            decayIndex = keyDictionary[sig[2::].upper()]
            
            XSecSinglet = XS_NWA(M, cSinglet[prodIndex], sig[:2:])*BRSinglet[decayIndex]/PNWA(proc=sig, mass=M, GM=GammaSinglet/M)
            XSecDoublet = XS_NWA(M, cDoublet[prodIndex], sig[:2:])*BRDoublet[decayIndex]/PNWA(proc=sig, mass=M, GM=GammaDoublet/M)

            TotalXSecSinglet += XSecSinglet
            TotalXSecDoublet += XSecDoublet

        if signal.upper()=="TS":
            if mode.upper()=="ALL":
                masses +=[{'name': signalName+lmsuffix, 'mass':M-100., 'mass_theory':M, 'xsec': 0.1, 'xsecTheory':TotalXSecSinglet, "Kappa": Kappa}]
            masses +=[{'name': signalName+nmsuffix, 'mass':M, 'mass_theory':M, 'xsec': 0.1, 'xsecTheory':TotalXSecSinglet, "Kappa": Kappa}]
        elif signal.upper()=="TD":
            if mode.upper()=="ALL":
                masses +=[{'name': signalName+lmsuffix, 'mass':M-100., 'mass_theory':M, 'xsec': 0.1, 'xsecTheory':TotalXSecDoublet, "Kappa": Kappa}]
            masses +=[{'name': signalName+nmsuffix, 'mass':M, 'mass_theory':M, 'xsec': 0.1, 'xsecTheory':TotalXSecDoublet, "Kappa": Kappa}]


# Palette 

number = 3
azurem9 = gROOT.GetColor(kAzure+2);
orangem4 = gROOT.GetColor(kYellow-9);
yellowm9 = gROOT.GetColor(kOrange-4);
Red = [yellowm9.GetRed(),orangem4.GetRed(),azurem9.GetRed()];
Green = [yellowm9.GetGreen(),orangem4.GetGreen(),azurem9.GetGreen()];
Blue = [yellowm9.GetBlue(),orangem4.GetBlue(),azurem9.GetBlue()];
length = [0,0.5,1]
l = array('d',[1.2,5.0])
TColor.CreateGradientColorTable(int(number),array('d',length),array('d',Red),array('d',Green),array('d',Blue),50);
gStyle.SetNumberContours(50);

###
# Effectively building the plots
###
tg_theory = TGraph2D()
tg_theory_GammaM = TGraph2D()
tg_theory_diff = TGraph2D()

tg_obs = TGraph2D()
tg_exp = TGraph2D()
tg_exp_plus1s,tg_exp_min1s = TGraph2D(),TGraph2D()
tg_exp_plus2s,tg_exp_min2s = TGraph2D(),TGraph2D()

tg_obs_diff = TGraph2D()
tg_exp_diff = TGraph2D()
tg_exp_plus1s_diff,tg_exp_min1s_diff = TGraph2D(),TGraph2D()
tg_exp_plus2s_diff,tg_exp_min2s_diff = TGraph2D(),TGraph2D()

tg_diff_list = [tg_obs_diff,tg_exp_diff,tg_exp_plus1s_diff,tg_exp_min1s_diff,tg_exp_plus2s_diff,tg_exp_min2s_diff]

# THEORY PLOTS

for iMass in range(len(gms)):
    if gms[iMass]['mass_theory'] > 2100.:
        continue
    tg_theory.SetPoint(iMass,gms[iMass]['mass_theory'],gms[iMass]['Kappa'],gms[iMass]['xsecTheory'])
    tg_theory_GammaM.SetPoint(iMass,gms[iMass]['mass_theory'],gms[iMass]['Kappa'],gms[iMass]['Gamma']/gms[iMass]['mass_theory'])

# HEAT MAP XS
"""
can2 = TCanvas("Limit_XS_"+signal,"Limit_XS_"+signal,950,900)
can2.SetBottomMargin(0.13)
can2.SetLeftMargin(0.125)
can2.SetRightMargin(0.185)
can2.SetTopMargin(0.11)

gStyle.SetPalette(kGreyYellow) #kBird
can2.cd()

tg_theory.SetTitle("#splitline{#scale[0.9]{"+signal_label+" cross section}}{#scale[0.75]{#sqrt{s}=13 TeV}}")
tg_theory.GetHistogram().GetXaxis().SetLimits(1000,2000)
tg_theory.GetHistogram().GetYaxis().SetLimits(0.1,1.6)
tg_theory.GetHistogram().SetMinimum(0.00005)
tg_theory.GetHistogram().SetMaximum(2.0)
tg_theory.GetHistogram().GetXaxis().SetNdivisions(406)
tg_theory.GetHistogram().GetXaxis().SetTitle("m_{T} [GeV]")
tg_theory.GetHistogram().GetYaxis().SetTitle("#kappa")
tg_theory.GetHistogram().GetZaxis().SetTitle("#sigma [pb]")
tg_theory.GetHistogram().GetXaxis().SetLabelSize(tg_theory.GetHistogram().GetXaxis().GetLabelSize()*1.2)
tg_theory.GetHistogram().GetYaxis().SetLabelSize(tg_theory.GetHistogram().GetYaxis().GetLabelSize()*1.2)
tg_theory.GetHistogram().GetZaxis().SetLabelSize(tg_theory.GetHistogram().GetZaxis().GetLabelSize()*1.2)
tg_theory.GetHistogram().GetXaxis().SetTitleSize(tg_theory.GetHistogram().GetXaxis().GetTitleSize()*1.3)
tg_theory.GetHistogram().GetYaxis().SetTitleSize(tg_theory.GetHistogram().GetYaxis().GetTitleSize()*1.3)
tg_theory.GetHistogram().GetZaxis().SetTitleSize(tg_theory.GetHistogram().GetZaxis().GetTitleSize()*1.3)
tg_theory.GetHistogram().GetXaxis().SetTitleOffset(1.32)
tg_theory.GetHistogram().GetYaxis().SetTitleOffset(1.4)
tg_theory.GetHistogram().GetZaxis().SetTitleOffset(1.45)
tg_theory.Draw('colz')

tl_siglabel = TLatex(0.2,1.15,signal_label)
tl_siglabel.SetNDC()
tl_siglabel.SetTextSize(0.042)
tl_siglabel.SetTextFont(42)
tl_siglabel.Draw()

gPad.Update()
gPad.SetLogz()
gPad.RedrawAxis()
can2.SetTickx()
can2.SetTicky()

can2.Print(outDir + "/" + signal.upper()+"_"+lumi.replace(".","")+outSuffix+"_XS_THEORY.pdf")

# HEAT MAP GAMMA/M

can3 = TCanvas("Limit_GAMMAM_"+signal,"Limit_GAMMAM_"+signal,900,900)
can3.SetBottomMargin(0.13)
can3.SetLeftMargin(0.13)
can3.SetRightMargin(0.14)
can3.SetTopMargin(0.08)

gStyle.SetPalette(kCividis)
can3.cd()

tg_theory_GammaM.SetTitle(signal_label)
tg_theory_GammaM.GetHistogram().GetXaxis().SetLimits(1000,2000)
tg_theory_GammaM.GetHistogram().GetYaxis().SetLimits(0.1,1.6)
tg_theory_GammaM.GetHistogram().GetXaxis().SetNdivisions(406)
tg_theory_GammaM.GetHistogram().GetXaxis().SetTitle("m_{T} [GeV]")
tg_theory_GammaM.GetHistogram().GetYaxis().SetTitle("#kappa")
tg_theory_GammaM.GetHistogram().GetZaxis().SetTitle("#Gamma/M_{T}")
tg_theory_GammaM.GetHistogram().GetXaxis().SetLabelSize(tg_theory_GammaM.GetHistogram().GetXaxis().GetLabelSize()*1.2)
tg_theory_GammaM.GetHistogram().GetYaxis().SetLabelSize(tg_theory_GammaM.GetHistogram().GetYaxis().GetLabelSize()*1.2)
tg_theory_GammaM.GetHistogram().GetZaxis().SetLabelSize(tg_theory_GammaM.GetHistogram().GetZaxis().GetLabelSize()*1.2)
tg_theory_GammaM.GetHistogram().GetXaxis().SetTitleSize(tg_theory_GammaM.GetHistogram().GetXaxis().GetTitleSize()*1.3)
tg_theory_GammaM.GetHistogram().GetYaxis().SetTitleSize(tg_theory_GammaM.GetHistogram().GetYaxis().GetTitleSize()*1.3)
tg_theory_GammaM.GetHistogram().GetZaxis().SetTitleSize(tg_theory_GammaM.GetHistogram().GetZaxis().GetTitleSize()*1.3)
tg_theory_GammaM.GetHistogram().GetXaxis().SetTitleOffset(1.32)
tg_theory_GammaM.GetHistogram().GetYaxis().SetTitleOffset(1.4)
tg_theory_GammaM.GetHistogram().GetZaxis().SetTitleOffset(0.97)
tg_theory_GammaM.Draw('colz')

tl_siglabel = TLatex(0.2,1.15,signal_label)
tl_siglabel.SetNDC()
tl_siglabel.SetTextSize(0.042)
tl_siglabel.SetTextFont(42)
tl_siglabel.Draw()

gPad.Update()
# gPad.SetLogz()
gPad.RedrawAxis()
can3.SetTickx()
can3.SetTicky()

can3.Print(outDir + "/" + signal.upper()+"_"+lumi.replace(".","")+outSuffix+"_GAMMAM_THEORY.pdf")

exit()
"""
# LIMIT PLOTS

counter=-1
goodmasses = []
for mass in masses:
    typename = mass['name']
    thismass = mass['mass']
    # if 'low_mass' in typename:
    #     thismass = mass['mass']-100.
    files = glob.glob(inDir + "/*"+typename+suffix+"*/Limits/asymptotics/*.root")
    if len(files)==0 or len(files)>1:
        continue
    counter += 1
    goodmasses.append(thismass)
    rootfile = TFile(files[0],"read")
    limtree = rootfile.Get('stats')
    limtree.GetEntry(0)
    print  " Mass: ", thismass," Kappa: ", mass['Kappa'], " mu : ", limtree.obs_upperlimit, " xsec : ", mass['xsec']
    tg_obs.SetPoint(counter,thismass,mass['Kappa'],limtree.obs_upperlimit*mass['xsec'])
    tg_exp.SetPoint(counter,thismass,mass['Kappa'],limtree.exp_upperlimit*mass['xsec'])
    tg_exp_plus1s.SetPoint(counter,thismass,mass['Kappa'],limtree.exp_upperlimit_plus1*mass['xsec'])
    tg_exp_plus2s.SetPoint(counter,thismass,mass['Kappa'],limtree.exp_upperlimit_plus2*mass['xsec'])
    tg_exp_min1s.SetPoint(counter,thismass,mass['Kappa'],limtree.exp_upperlimit_minus1*mass['xsec'])
    tg_exp_min2s.SetPoint(counter,thismass,mass['Kappa'],limtree.exp_upperlimit_minus2*mass['xsec'])
    rootfile.Close()

goodmasses = sorted(list(set(goodmasses)))

for iMass in range(len(masses)):

    ycoord = masses[iMass]['Kappa']

    obs_interp = tg_obs.Interpolate(masses[iMass]['mass_theory'],ycoord)
    exp_interp = tg_exp.Interpolate(masses[iMass]['mass_theory'],ycoord)
    exp_plus1s_interp = tg_exp_plus1s.Interpolate(masses[iMass]['mass_theory'],ycoord)
    exp_plus2s_interp = tg_exp_plus2s.Interpolate(masses[iMass]['mass_theory'],ycoord)
    exp_min1s_interp = tg_exp_min1s.Interpolate(masses[iMass]['mass_theory'],ycoord)
    exp_min2s_interp = tg_exp_min2s.Interpolate(masses[iMass]['mass_theory'],ycoord)

    tg_obs_diff.SetPoint(iMass,masses[iMass]['mass_theory'],ycoord,obs_interp-masses[iMass]['xsecTheory'])
    tg_exp_diff.SetPoint(iMass,masses[iMass]['mass_theory'],ycoord,exp_interp-masses[iMass]['xsecTheory'])
    tg_exp_plus1s_diff.SetPoint(iMass,masses[iMass]['mass_theory'],ycoord,exp_plus1s_interp-masses[iMass]['xsecTheory'])
    tg_exp_plus2s_diff.SetPoint(iMass,masses[iMass]['mass_theory'],ycoord,exp_plus2s_interp-masses[iMass]['xsecTheory'])
    tg_exp_min1s_diff.SetPoint(iMass,masses[iMass]['mass_theory'],ycoord,exp_min1s_interp-masses[iMass]['xsecTheory'])
    tg_exp_min2s_diff.SetPoint(iMass,masses[iMass]['mass_theory'],ycoord,exp_min2s_interp-masses[iMass]['xsecTheory'])

# PLOTTING

can = TCanvas("Limit_"+signal,"Limit_"+signal,900,900)
can.SetBottomMargin(0.15)
can.SetLeftMargin(0.15)
can.SetRightMargin(0.05)
can.SetTopMargin(0.05)

tg_obs_diff.SetLineColor(kBlack)
tg_obs_diff.SetLineStyle(1)

tg_exp_diff.SetLineColor(kBlack)
tg_exp_diff.SetLineStyle(2)

for tg_diff in tg_diff_list:
    tg_diff.SetLineWidth(3)
    tg_diff.GetHistogram().SetContour(2)
    tg_diff.GetHistogram().SetContourLevel(1,0.0)

# retrieve contours
tg_exp_plus2s_diff.Draw('contz list')
can.Update()
conts = gROOT.GetListOfSpecials().FindObject("contours")
tg_line_exp_plus2s = conts.At(0).First().Clone()

tg_exp_min2s_diff.Draw('cont list')
can.Update()
conts = gROOT.GetListOfSpecials().FindObject("contours")
tg_line_exp_min2s = conts.At(0).First().Clone()

tg_exp_plus1s_diff.Draw('cont list')
can.Update()
conts = gROOT.GetListOfSpecials().FindObject("contours")
tg_line_exp_plus1s = conts.At(0).First().Clone()

tg_exp_min1s_diff.Draw('cont list')
can.Update()
conts = gROOT.GetListOfSpecials().FindObject("contours")
tg_line_exp_min1s = conts.At(0).First().Clone()

tg_obs_diff.Draw('cont list')
can.Update()
conts = gROOT.GetListOfSpecials().FindObject("contours")
tg_line_obs = conts.At(0).First().Clone()

tg_exp_diff.Draw('cont list')
can.Update()
conts = gROOT.GetListOfSpecials().FindObject("contours")
tg_line_exp = conts.At(0).First().Clone()

tg_fill_exp_2s = TGraph()
tg_fill_exp_1s = TGraph()

# 2 SIGMA BAND
for i in range(tg_line_exp_plus2s.GetN()):
    tg_fill_exp_2s.SetPoint(i,tg_line_exp_plus2s.GetPointX(i),tg_line_exp_plus2s.GetPointY(i))
# corner point
if signal.upper()=="TS":
    tg_fill_exp_2s.SetPoint(tg_line_exp_plus2s.GetN(),tg_line_exp_min2s.GetPointX(tg_line_exp_min2s.GetN()-1),tg_line_exp_plus2s.GetPointY(tg_line_exp_plus2s.GetN()-1))
for i in range(tg_line_exp_min2s.GetN()):
    if signal.upper()=="TS":
        tg_fill_exp_2s.SetPoint(tg_line_exp_plus2s.GetN()+tg_line_exp_min2s.GetN()-i,tg_line_exp_min2s.GetPointX(i),tg_line_exp_min2s.GetPointY(i))
    else:
        tg_fill_exp_2s.SetPoint(tg_line_exp_plus2s.GetN()+tg_line_exp_min2s.GetN()-i-1,tg_line_exp_min2s.GetPointX(i),tg_line_exp_min2s.GetPointY(i))
# final closing
tg_fill_exp_2s.SetPoint(tg_fill_exp_2s.GetN(),tg_fill_exp_2s.GetPointX(tg_fill_exp_2s.GetN()-1),tg_fill_exp_2s.GetPointY(0))

# 1 SIGMA BAND
for i in range(tg_line_exp_plus1s.GetN()):
    tg_fill_exp_1s.SetPoint(i,tg_line_exp_plus1s.GetPointX(i),tg_line_exp_plus1s.GetPointY(i))
# corner point
if signal.upper()=="TS":
    tg_fill_exp_1s.SetPoint(tg_line_exp_plus1s.GetN(),tg_line_exp_min1s.GetPointX(tg_line_exp_min1s.GetN()-1),tg_line_exp_plus1s.GetPointY(tg_line_exp_plus1s.GetN()-1))
for i in range(tg_line_exp_min1s.GetN()):
    if signal.upper()=="TS":
        tg_fill_exp_1s.SetPoint(tg_line_exp_plus1s.GetN()+tg_line_exp_min1s.GetN()-i,tg_line_exp_min1s.GetPointX(i),tg_line_exp_min1s.GetPointY(i))
    else:
        tg_fill_exp_1s.SetPoint(tg_line_exp_plus1s.GetN()+tg_line_exp_min1s.GetN()-i-1,tg_line_exp_min1s.GetPointX(i),tg_line_exp_min1s.GetPointY(i))
# final closing
tg_fill_exp_1s.SetPoint(tg_fill_exp_1s.GetN(),tg_fill_exp_1s.GetPointX(tg_fill_exp_1s.GetN()-1),tg_fill_exp_1s.GetPointY(0))

# final drawing
can.Update()

tg_line_exp_plus1s.SetLineColor(kGreen)
tg_line_exp_plus2s.SetLineColor(kYellow)
tg_line_exp_min1s.SetLineColor(kGreen)
tg_line_exp_min2s.SetLineColor(kYellow)

tg_fill_exp_2s.SetFillColor(kYellow)
tg_fill_exp_1s.SetFillColor(kGreen)
tg_fill_exp_2s.SetLineColor(0)
tg_fill_exp_1s.SetLineColor(0)

tg_fill_exp_2s.SetTitle("")
tg_fill_exp_2s.GetXaxis().SetLimits(goodmasses[0],goodmasses[-1])
tg_fill_exp_2s.GetXaxis().SetNdivisions(406)
tg_fill_exp_2s.GetXaxis().SetTitle("m_{T} [GeV]")

tg_fill_exp_2s.GetYaxis().SetTitle("#kappa")
tg_fill_exp_2s.SetMinimum(0.25)
tg_fill_exp_2s.SetMaximum(1.6)

tg_fill_exp_2s.GetXaxis().SetLabelSize(tg_fill_exp_2s.GetHistogram().GetXaxis().GetLabelSize()*1.2)
tg_fill_exp_2s.GetYaxis().SetLabelSize(tg_fill_exp_2s.GetHistogram().GetYaxis().GetLabelSize()*1.2)
tg_fill_exp_2s.GetXaxis().SetTitleSize(tg_fill_exp_2s.GetHistogram().GetXaxis().GetTitleSize()*1.3)
tg_fill_exp_2s.GetYaxis().SetTitleSize(tg_fill_exp_2s.GetHistogram().GetYaxis().GetTitleSize()*1.3)
tg_fill_exp_2s.GetXaxis().SetTitleOffset(1.32)
tg_fill_exp_2s.GetYaxis().SetTitleOffset(1.4)

tg_fill_exp_2s.Draw('af')
tg_fill_exp_1s.Draw('f same')

# CONTOURS

if (signal.upper()=="TS" or signal.upper()=="TD") and (mode.upper()=="ALL"):
    clones = []
    contour_labels = []
    if signal.upper()=="TS":
        contour_gm = [0.05,0.1,0.2,0.5]
    elif signal.upper()=="TD":
        contour_gm = [0.3,0.5,1.0]
    
    for i,gm in enumerate(contour_gm):
        even = ((-1)**i < 0)
        clones += [tg_theory_GammaM.Clone("gmclon"+`i`)]
        clones[i].GetHistogram().SetDirectory(0)
        clones[i].GetHistogram().SetContour(1)
        clones[i].GetHistogram().SetContourLevel(0,gm)
        clones[i].SetLineWidth(2)
        clones[i].SetLineColor(kGray+2)
        clones[i].SetLineStyle(7)
        if signal.upper()=="TS":
            clones[i].GetHistogram().GetYaxis().SetRangeUser(0.25,1.15)
        elif signal.upper()=="TD":
            if i==0:
                clones[i].GetHistogram().GetYaxis().SetRangeUser(0.6,1.6)
            if i==1:
                clones[i].GetHistogram().GetYaxis().SetRangeUser(0.8,1.6)
    
        clones[i].Draw("samecont3")
    
        if signal.upper()=="TS":
            if gm==0.05:
                contour_labels += [TLatex(1290,0.33,"#Gamma_{T}/M_{T}="+"%.0f"%(100*gm)+"%")]
                contour_labels[i].SetTextAngle(-12.5)
            elif gm==0.1:
                contour_labels += [TLatex(1720,0.35,"#Gamma_{T}/M_{T}="+"%.0f"%(100*gm)+"%")]
                contour_labels[i].SetTextAngle(-11)
            elif gm==0.2:
                contour_labels += [TLatex(1900,0.44,"#Gamma_{T}/M_{T}="+"%.0f"%(100*gm)+"%")]
                contour_labels[i].SetTextAngle(-12)
            elif gm==0.5:
                contour_labels += [TLatex(1170,1.0,"#Gamma_{T}/M_{T}="+"%.0f"%(100*gm)+"%")]
                contour_labels[i].SetTextAngle(-30)
    
        elif signal.upper()=="TD":
            if gm==0.3:
                contour_labels += [TLatex(1090,0.82,"#Gamma_{T}/M_{T}="+"%.0f"%(100*gm)+"%")]
                contour_labels[i].SetTextAngle(-30)
            elif gm==0.5:
                contour_labels += [TLatex(1285,0.895,"#Gamma_{T}/M_{T}="+"%.0f"%(100*gm)+"%")]
                contour_labels[i].SetTextAngle(-28)
            elif gm==1.0:
                contour_labels += [TLatex(1710,1.07,"#Gamma_{T}/M_{T}="+"%.0f"%(100*gm)+"%")]
                contour_labels[i].SetTextAngle(-26)
                
        contour_labels[i].SetTextSize(0.028)
        contour_labels[i].SetTextFont(42)
        contour_labels[i].SetTextColor(kGray+2)
        contour_labels[i].Draw()

tg_exp_diff.Draw('cont3 same')
tg_obs_diff.Draw('cont3 same')

if signal.upper()=="TS":
    leg = TLegend(0.17,0.64,0.48,0.795)
else:
    leg = TLegend(0.42,0.31,0.72,0.465)
    # leg = TLegend(0.38,0.31,0.92,0.465)
    # leg.SetTextAlign(31)
leg.SetFillColor(0)
leg.SetLineColor(0)

leg.AddEntry(tg_obs_diff,"95% CL observed limit","l")
leg.AddEntry(tg_exp_diff,"95% CL expected limit","l")
leg.AddEntry(tg_fill_exp_1s,"95% CL expected limit #pm1#sigma","f")
leg.AddEntry(tg_fill_exp_2s,"95% CL expected limit #pm2#sigma","f")

leg.SetTextSize(0.0365)
leg.Draw()

# FORMATTING
if signal.upper()=="TS":
    atl_x = 0.19
    atl_y = 0.88
else:
    atl_x = 0.19
    atl_y = 0.25

tl_atlas = TLatex(atl_x,atl_y,"ATLAS")
tl_atlas.SetNDC()
tl_atlas.SetTextFont(72)
tl_atlas.SetTextSize(tl_atlas.GetTextSize()*0.85)
tl_atlas.Draw()
tl_int = TLatex(atl_x+0.15,atl_y,"Work in Progress")#"Work in Progress")
tl_int.SetNDC()
tl_int.SetTextFont(42)
tl_int.SetTextSize(tl_int.GetTextSize()*0.85)
tl_int.Draw()
tl_energy = TLatex(atl_x,atl_y-0.06,"#sqrt{s} = "+energy+" TeV, "+lumi+" fb^{-1}")
tl_energy.SetNDC()
tl_energy.SetTextFont(42)
tl_energy.SetTextSize(tl_energy.GetTextSize()*0.85)
tl_energy.Draw()

if signal.upper()=="TS":
    tl_siglabel = TLatex(0.39,0.59,signal_label)
else:
    tl_siglabel = TLatex(0.67,0.49,signal_label)

tl_siglabel.SetNDC()
tl_siglabel.SetTextSize(0.0365)
tl_siglabel.SetTextFont(42)
tl_siglabel.Draw()

gPad.Update()
gPad.RedrawAxis()
can.SetTickx()
can.SetTicky()

can.Print(outDir + "/" + signal.upper()+"_"+lumi.replace(".","")+outSuffix+"_CONT.pdf")
can.Print(outDir + "/" + signal.upper()+"_"+lumi.replace(".","")+outSuffix+"_CONT.png")
can.Print(outDir + "/" + signal.upper()+"_"+lumi.replace(".","")+outSuffix+"_CONT.eps")

# exit()
#
# OBSERVED AND EXCLUDED XS LIMITS
#

# remove to plot XS limit map

# PLOTTING

can2 = TCanvas("Limit_XS_"+signal,"Limit_XS_"+signal,1000,950)
can2.SetBottomMargin(0.13)
can2.SetLeftMargin(0.115)
can2.SetRightMargin(0.220)
can2.SetTopMargin(0.165)
can2.cd()

# OBSERVED LIMITS

tg_line_obs.SetLineColor(kBlack)
tg_line_obs.SetLineWidth(3)
tg_line_obs.SetLineStyle(1)

tg_obs.SetTitle("")
tg_obs.GetHistogram().GetXaxis().SetLimits(1000,2100)
tg_obs.GetHistogram().GetYaxis().SetLimits(0.3,1.6)
tg_obs.GetHistogram().SetMinimum(0.025)
tg_obs.GetHistogram().SetMaximum(0.3)
tg_obs.GetHistogram().GetXaxis().SetNdivisions(406)
tg_obs.GetHistogram().GetZaxis().SetMoreLogLabels()
tg_obs.GetHistogram().GetXaxis().SetTitle("m_{T} [GeV]")
tg_obs.GetHistogram().GetYaxis().SetTitle("#kappa")
tg_obs.GetHistogram().GetZaxis().SetTitle("95% CL #sigma limit [pb]")
tg_obs.GetHistogram().GetXaxis().SetLabelSize(tg_obs.GetHistogram().GetXaxis().GetLabelSize()*1.2)
tg_obs.GetHistogram().GetYaxis().SetLabelSize(tg_obs.GetHistogram().GetYaxis().GetLabelSize()*1.2)
tg_obs.GetHistogram().GetZaxis().SetLabelSize(tg_obs.GetHistogram().GetZaxis().GetLabelSize()*1.15)
tg_obs.GetHistogram().GetXaxis().SetTitleSize(tg_obs.GetHistogram().GetXaxis().GetTitleSize()*1.3)
tg_obs.GetHistogram().GetYaxis().SetTitleSize(tg_obs.GetHistogram().GetYaxis().GetTitleSize()*1.3)
tg_obs.GetHistogram().GetZaxis().SetTitleSize(tg_obs.GetHistogram().GetZaxis().GetTitleSize()*1.3)
tg_obs.GetHistogram().GetXaxis().SetTitleOffset(1.32)
tg_obs.GetHistogram().GetYaxis().SetTitleOffset(1.3)
tg_obs.GetHistogram().GetZaxis().SetTitleOffset(2.0)

tg_obs.Draw('colz')

# CONTOURS

if (signal.upper()=="TS" or signal.upper()=="TD") and (mode.upper()=="ALL"):
    clones = []
    contour_labels = []
    contour_xs = [0.04,0.06,0.08,0.1,0.15,0.25]
    for i,xs in enumerate(contour_xs):
        even = ((-1)**i < 0)
        clones += [tg_obs.Clone("obsclon"+`i`)]
        clones[i].GetHistogram().SetDirectory(0)
        clones[i].GetHistogram().SetContour(1)
        clones[i].GetHistogram().SetContourLevel(0,xs)
        clones[i].SetLineWidth(2)
        clones[i].SetLineColor(kRed+1)
        clones[i].SetLineStyle(1)
        if (even): clones[i].SetLineStyle(7)
        clones[i].Draw("samecont3")
    
        if signal.upper()=="TS":
            if xs==0.04:
                contour_labels += [TLatex(1900,0.402,str(xs))]
            elif xs==0.06:
                contour_labels += [TLatex(1750,0.65,str(xs))]
            elif xs==0.08:
                contour_labels += [TLatex(1550,0.9,str(xs))]
            elif xs==0.1:
                contour_labels += [TLatex(1340,1.45,str(xs))]
            elif xs==0.15:
                contour_labels += [TLatex(1125,1.3,str(xs))]
            elif xs==0.25:
                contour_labels += [TLatex(1065,0.95,str(xs))]
    
        elif signal.upper()=="TD":
            if xs==0.04:
                contour_labels += [TLatex(1900,0.410,str(xs))]
            elif xs==0.06:
                contour_labels += [TLatex(1800,0.65,str(xs))]
            elif xs==0.08:
                contour_labels += [TLatex(1690,0.91,str(xs))]
            elif xs==0.1:
                contour_labels += [TLatex(1610,1.23,str(xs))]
            elif xs==0.15:
                contour_labels += [TLatex(1125,1.3,str(xs))]
            elif xs==0.25:
                contour_labels += [TLatex(1060,0.75,str(xs))]

        contour_labels[i].SetTextSize(0.03)
        contour_labels[i].SetTextFont(42)
        contour_labels[i].SetTextColor(kRed+1)
        contour_labels[i].Draw()

tg_line_obs.Draw('l same')

# FORMATTING

leg = TLegend(0.55,0.865,.79,.92)
leg.SetFillStyle(0)
leg.SetFillColor(0)
leg.SetLineColor(0)
leg.AddEntry(tg_line_obs,"95% CL observed limit","l")
leg.SetTextSize(0.037)
leg.Draw()

atl_x = 0.05
atl_y = 0.94

tl_atlas = TLatex(atl_x,atl_y,"ATLAS")
tl_atlas.SetNDC()
tl_atlas.SetTextFont(72)
tl_atlas.SetTextSize(tl_atlas.GetTextSize()*0.85)
tl_atlas.Draw()
tl_int = TLatex(atl_x+0.15,atl_y,"Work in Progress")#"Work in Progress")
tl_int.SetNDC()
tl_int.SetTextFont(42)
tl_int.SetTextSize(tl_int.GetTextSize()*0.85)
tl_int.Draw()
tl_energy = TLatex(atl_x,atl_y-0.06,"#sqrt{s} = "+energy+" TeV, "+lumi+" fb^{-1}")
tl_energy.SetNDC()
tl_energy.SetTextFont(42)
tl_energy.SetTextSize(tl_energy.GetTextSize()*0.85)
tl_energy.Draw()

tl_siglabel = TLatex(0.795,0.93,signal_label)
tl_siglabel.SetNDC()
tl_siglabel.SetTextSize(0.037)
tl_siglabel.SetTextFont(42)
tl_siglabel.Draw()

gPad.Update()
gPad.SetLogz()
gPad.RedrawAxis()
can2.SetTickx()
can2.SetTicky()

can2.Print(outDir + "/" + signal.upper()+"_"+lumi.replace(".","")+outSuffix+"_XSLIM_OBS.pdf")
can2.Print(outDir + "/" + signal.upper()+"_"+lumi.replace(".","")+outSuffix+"_XSLIM_OBS.eps")
can2.Print(outDir + "/" + signal.upper()+"_"+lumi.replace(".","")+outSuffix+"_XSLIM_OBS.png")

# EXPECTED LIMITS

tg_line_exp.SetLineColor(kBlack)
tg_line_exp.SetLineWidth(3)
tg_line_exp.SetLineStyle(2)

tg_exp.SetTitle("")
tg_exp.GetHistogram().GetXaxis().SetLimits(1000,2100)
tg_exp.GetHistogram().GetYaxis().SetLimits(0.3,1.6)
tg_exp.GetHistogram().SetMinimum(0.025)
tg_exp.GetHistogram().SetMaximum(0.3)
tg_exp.GetHistogram().GetXaxis().SetNdivisions(406)
tg_exp.GetHistogram().GetZaxis().SetMoreLogLabels()
tg_exp.GetHistogram().GetXaxis().SetTitle("m_{T} [GeV]")
tg_exp.GetHistogram().GetYaxis().SetTitle("#kappa")
tg_exp.GetHistogram().GetZaxis().SetTitle("95% CL #sigma limit [pb]")

tg_exp.GetHistogram().GetXaxis().SetLabelSize(tg_exp.GetHistogram().GetXaxis().GetLabelSize()*1.2)
tg_exp.GetHistogram().GetYaxis().SetLabelSize(tg_exp.GetHistogram().GetYaxis().GetLabelSize()*1.2)
tg_exp.GetHistogram().GetZaxis().SetLabelSize(tg_exp.GetHistogram().GetZaxis().GetLabelSize()*1.15)
tg_exp.GetHistogram().GetXaxis().SetTitleSize(tg_exp.GetHistogram().GetXaxis().GetTitleSize()*1.3)
tg_exp.GetHistogram().GetYaxis().SetTitleSize(tg_exp.GetHistogram().GetYaxis().GetTitleSize()*1.3)
tg_exp.GetHistogram().GetZaxis().SetTitleSize(tg_exp.GetHistogram().GetZaxis().GetTitleSize()*1.3)
tg_exp.GetHistogram().GetXaxis().SetTitleOffset(1.32)
tg_exp.GetHistogram().GetYaxis().SetTitleOffset(1.3)
tg_exp.GetHistogram().GetZaxis().SetTitleOffset(2.0)

tg_exp.Draw('colz')

# CONTOURS

if (signal.upper()=="TS" or signal.upper()=="TD") and (mode.upper()=="ALL"):
    clones = []
    contour_labels = []
    contour_xs = [0.04,0.06,0.08,0.1,0.15,0.25]
    for i,xs in enumerate(contour_xs):
        even = ((-1)**i < 0)
        clones += [tg_exp.Clone("expclon"+`i`)]
        clones[i].GetHistogram().SetDirectory(0)
        clones[i].GetHistogram().SetContour(1)
        clones[i].GetHistogram().SetContourLevel(0,xs)
        clones[i].SetLineWidth(2)
        clones[i].SetLineColor(kRed+1)
        clones[i].SetLineStyle(1)
        if (even): clones[i].SetLineStyle(7)
        clones[i].Draw("samecont3")
    
        if signal.upper()=="TS":
            if xs==0.04:
                contour_labels += [TLatex(1970,0.365,str(xs))]
            elif xs==0.06:
                contour_labels += [TLatex(1940,0.53,str(xs))]
            elif xs==0.08:
                contour_labels += [TLatex(1870,0.69,str(xs))]
            elif xs==0.1:
                contour_labels += [TLatex(1630,0.8,str(xs))]
            elif xs==0.15:
                contour_labels += [TLatex(1270,0.9,str(xs))]
            elif xs==0.25:
                contour_labels += [TLatex(1065,0.95,str(xs))]
    
        elif signal.upper()=="TD":
            if xs==0.04:
                contour_labels += [TLatex(1975,0.435,str(xs))]
            elif xs==0.06:
                contour_labels += [TLatex(1920,0.65,str(xs))]
            elif xs==0.08:
                contour_labels += [TLatex(1800,0.82,str(xs))]
            elif xs==0.1:
                contour_labels += [TLatex(1630,0.89,str(xs))]
            elif xs==0.15:
                contour_labels += [TLatex(1325,0.965,str(xs))]
            elif xs==0.25:
                contour_labels += [TLatex(1110,1.0,str(xs))]
        contour_labels[i].SetTextSize(0.03)
        contour_labels[i].SetTextFont(42)
        contour_labels[i].SetTextColor(kRed+1)
        contour_labels[i].Draw()

tg_line_exp.Draw('l same')

leg = TLegend(0.55,0.865,.79,.92)
leg.SetFillStyle(0)
leg.SetFillColor(0)
leg.SetLineColor(0)
leg.AddEntry(tg_line_exp,"95% CL expected limit","l")
leg.SetTextSize(0.037)
leg.Draw()

tl_atlas.Draw()
tl_int.Draw()
tl_energy.Draw()

tl_siglabel = TLatex(0.795,0.93,signal_label)
tl_siglabel.SetNDC()
tl_siglabel.SetTextSize(0.037)
tl_siglabel.SetTextFont(42)
tl_siglabel.Draw()

gPad.Update()
gPad.SetLogz()
gPad.RedrawAxis()
can2.SetTickx()
can2.SetTicky()

can2.Print(outDir + "/" + signal.upper()+"_"+lumi.replace(".","")+outSuffix+"_XSLIM_EXP.pdf")
can2.Print(outDir + "/" + signal.upper()+"_"+lumi.replace(".","")+outSuffix+"_XSLIM_EXP.eps")
can2.Print(outDir + "/" + signal.upper()+"_"+lumi.replace(".","")+outSuffix+"_XSLIM_EXP.png")
