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
from optparse import OptionParser
from ROOT import *

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

gROOT.SetBatch(1)

##________________________________________________________
## OPTIONS
parser = OptionParser()
parser.add_option("-i","--inputDir",help="location of the log files ",dest="inDir",default="")
parser.add_option("-o","--outDir",help="output folder",dest="outDir",default="./test/")
parser.add_option("-s","--signal",help="signal",dest="signal",default="TT")
parser.add_option("-b","--br",help="branching ratio configuration",dest="br",default="Singlet")
parser.add_option("-t","--template",help="template of the path",dest="template",default="Limits/LimitsANALYSIS/ANALYSIS_MASS_BR/signal.root")
parser.add_option("-a","--analyses",help="coma-separated list of analyses", dest="analyses",default="WBX,HTX,ZTMET")
parser.add_option("-c","--combination",help="name of the combination", dest="combination",default="Combined_WBX_ZTMET_HTX")
parser.add_option("-d","--data",help="consider data",dest="data",action="store_true",default=False)

(options, args) = parser.parse_args()
inDir=options.inDir
outDir=options.outDir
signal=options.signal
br=options.br
template=options.template
analyses=options.analyses.split(",")
combination=options.combination
data=options.data

os.system("mkdir -p "+outDir)

###
# Getting the values of the masses and cross-sections
###
masses = []
if(signal.upper()=="TT" or signal.upper()=="BB"):
    # masses += [{'name':"TT_600",'mass':600,'xsec':1.16,'err':0.10}]
    masses += [{'name':"700",'mass':700,'xsec':0.455,'err':0.043}]
    masses += [{'name':"750",'mass':750,'xsec':0.295,'err':0.029}]
    masses += [{'name':"800",'mass':800,'xsec':0.195,'err':0.020}]
    masses += [{'name':"850",'mass':850,'xsec':0.132,'err':0.014}]
    masses += [{'name':"900",'mass':900,'xsec':0.0900,'err':0.0096}]
    masses += [{'name':"950",'mass':950,'xsec':0.0624,'err':0.0068}]
    masses += [{'name':"1000",'mass':1000,'xsec':0.0438,'err':0.0048}]
    masses += [{'name':"1050",'mass':1050,'xsec':0.0311,'err':0.0035}]
    masses += [{'name':"1100",'mass':1100,'xsec':0.0223,'err':0.0025}]
    #masses += [{'name':"TT_1150",'mass':1150,'xsec':0.0161,'err':0.0018}]
    masses += [{'name':"1200",'mass':1200,'xsec':0.0117,'err':0.0013}]
    masses += [{'name':"1300",'mass':1300,'xsec':0.00634,'err':0.00075}]
    masses += [{'name':"1400",'mass':1400,'xsec':0.00350,'err':0.00043}]

###
# Effectively building the plots
###
tg_theory = TGraphErrors(len(masses))

tg_obs_comb = TGraph(len(masses))
tg_exp_comb = TGraph(len(masses))
tg_exp1s_comb = TGraph(2*len(masses))
tg_exp2s_comb = TGraph(2*len(masses))

v_tg_obs = []
v_tg_exp = []
v_tg_exp1s = []

##
## Theory plot
##
for iMass in range(len(masses)):
    tg_theory.SetPoint(iMass,masses[iMass]['mass'],masses[iMass]['xsec'])
    if 'err' in masses[iMass].keys():
        tg_theory.SetPointError(iMass,0,masses[iMass]['err'])
    else:
        tg_theory.SetPointError(iMass,0,0.)
tg_theory.SetLineColor(kRed)
tg_theory.SetFillColor(kRed-9)
tg_theory.GetXaxis().SetLimits(masses[0]['mass'],masses[len(masses)-1]['mass'])
tg_theory.GetHistogram().SetMaximum(tg_theory.GetHistogram().GetMaximum()*100.)
tg_theory.SetLineWidth(2)

##
## Creating the canvas
##
can = TCanvas("1DLimit_"+signal,"1DLimit_"+signal,800,800)
leg = TLegend(0.30,0.68,0.82,0.90)
leg.SetFillColor(0)
leg.SetLineColor(0)

##
## Theory
##
if(signal.upper()=="TT" or signal.upper()=="BB"):
    tg_theory.GetHistogram().SetMinimum(0.0002)
tg_theory.Draw("al3")
tg_theory.SetTitle("")
tg_theory.GetHistogram().GetXaxis().SetLabelSize(tg_theory.GetHistogram().GetXaxis().GetLabelSize()*1.2)
tg_theory.GetHistogram().GetYaxis().SetLabelSize(tg_theory.GetHistogram().GetYaxis().GetLabelSize()*1.2)
tg_theory.GetHistogram().GetXaxis().SetTitleSize(tg_theory.GetHistogram().GetXaxis().GetTitleSize()*1.2)
tg_theory.GetHistogram().GetYaxis().SetTitleSize(tg_theory.GetHistogram().GetYaxis().GetTitleSize()*1.2)
tg_theory.GetHistogram().GetXaxis().SetTitleOffset(1.4)
tg_theory.GetHistogram().GetYaxis().SetTitleOffset(1.4)
if(signal.upper()=="TT"):
    tg_theory.GetXaxis().SetTitle("m_{T} [GeV]")
    tg_theory.GetYaxis().SetTitle("#sigma(pp #rightarrow T#bar{T}) [pb]")
if(signal.upper()=="BB"):
    tg_theory.GetXaxis().SetTitle("m_{B} [GeV]")
    tg_theory.GetYaxis().SetTitle("#sigma(pp #rightarrow B#bar{B}) [pb]")

counter = -1
for mass in masses:
    counter += 1
    files = glob.glob(template.replace("MASS",mass['name']).replace("ANALYSIS",combination).replace("BR",br).replace("_"+signal.upper()+"_","_"))
    print template.replace("MASS",mass['name']).replace("ANALYSIS",combination).replace("BR",br).replace("_"+signal.upper()+"_","_")
    if len(files)==0 or len(files)>1:
        print "<!> ERROR for mass " + `mass['mass']` + " !!"
    else:
        rootfile = TFile(files[0],"read")
        histogram = rootfile.Get("limit")
        tg_obs_comb.SetPoint(counter,mass['mass'],histogram.GetBinContent(1)*mass['xsec'])
        tg_exp_comb.SetPoint(counter,mass['mass'],histogram.GetBinContent(2)*mass['xsec'])
        tg_exp1s_comb.SetPoint(counter,mass['mass'],histogram.GetBinContent(4)*mass['xsec'])
        tg_exp2s_comb.SetPoint(counter,mass['mass'],histogram.GetBinContent(3)*mass['xsec'])
        tg_exp1s_comb.SetPoint(2*len(masses)-counter-1,mass['mass'],histogram.GetBinContent(5)*mass['xsec'])
        tg_exp2s_comb.SetPoint(2*len(masses)-counter-1,mass['mass'],histogram.GetBinContent(6)*mass['xsec'])
        rootfile.Close()

##
## Limits
##
if not data:
    tg_exp2s_comb.SetLineColor(kYellow)
    tg_exp2s_comb.SetFillColor(kYellow)
    tg_exp2s_comb.Draw("f")

    tg_exp1s_comb.SetLineColor(kGreen)
    tg_exp1s_comb.SetFillColor(kGreen)
    tg_exp1s_comb.Draw("f")

tg_theory.Draw("l3")
tg_theory.Draw("lX")

tg_exp_comb.SetLineColor(kBlack)
tg_exp_comb.SetLineWidth(3)
tg_exp_comb.SetLineStyle(2)
tg_exp_comb.Draw("l")

tg_obs_comb.SetLineColor(kBlack)
tg_obs_comb.SetLineWidth(3)
tg_obs_comb.Draw("l")


##
## All limits
##
colors=[kBlack,kRed,kCyan,kOrange,kViolet,kGreen]
ana_counter=0
leg_indiv=TLegend(0.20,0.18,0.9,0.23)
leg_indiv.SetLineColor(kWhite)
leg_indiv.SetTextSize(0.04)
leg_indiv.SetNColumns(len(analyses))
for ana in analyses:
    tg_obs = TGraph()
    tg_exp = TGraph()
    tg_exp1s = TGraph()
    counter = -1
    for mass in masses:
        counter += 1
        files = glob.glob(template.replace("MASS",mass['name']).replace("ANALYSIS",ana).replace("BR",br))
        if len(files)==0 or len(files)>1:
            print "<!> ERROR for mass " + `mass['mass']` + " !!"
        else:
            rootfile = TFile(files[0],"read")
            histogram = rootfile.Get("limit")
            tg_obs.SetPoint(counter,mass['mass'],histogram.GetBinContent(1)*mass['xsec'])
            tg_exp.SetPoint(counter,mass['mass'],histogram.GetBinContent(2)*mass['xsec'])
            tg_exp1s.SetPoint(counter,mass['mass'],histogram.GetBinContent(4)*mass['xsec'])
            tg_exp1s.SetPoint(2*len(masses)-counter-1,mass['mass'],histogram.GetBinContent(5)*mass['xsec'])
            rootfile.Close()
    tg_exp.SetLineColor(colors[ana_counter])
    tg_exp.SetLineWidth(3)
    tg_exp.SetLineStyle(3)
    tg_obs.SetLineColor(colors[ana_counter])
    tg_obs.SetLineWidth(2)
    tg_exp1s.SetFillColorAlpha(colors[ana_counter],0.10)
    tg_exp.Draw("l")
    if data:
        tg_obs.Draw("l")
    v_tg_exp += [tg_exp]
    v_tg_exp1s += [tg_exp1s]
    v_tg_obs += [tg_obs]
    leg_indiv.AddEntry(tg_obs,ana,"l")
    ana_counter+=1


##
## Legend
##
leg.AddEntry(tg_theory,"Theory (NNLO prediction #pm1#sigma)","lf")
if data:
    leg.AddEntry(tg_obs_comb,"95% CL combined observed","l")
else:
    leg.AddEntry(tg_exp1s_comb,"95% CL expected limit #pm1#sigma","f")
    leg.AddEntry(tg_exp2s_comb,"95% CL expected limit #pm2#sigma","f")
leg.AddEntry(tg_exp_comb,"95% CL combined expected","l")
leg.SetTextSize(0.04)
leg.Draw()
leg_indiv.Draw()

#Intersections
# intersx=FitFunctionAndDefineIntersection(tg_theory,tg_exp,isData=False )
# print "Expected limit: " + `intersx[0]`
# intersx[1].Draw("lp")
# if(data):
#     intersxData=FitFunctionAndDefineIntersection(tg_theory,tg_obs,isData=True )
#     print "Observed limit: " + `intersxData[0]`

can.SetBottomMargin(0.15)
can.SetLeftMargin(0.15)
can.SetRightMargin(0.05)
can.SetTopMargin(0.05)
tl_atlas = TLatex(0.19,0.32,"ATLAS")
tl_atlas.SetNDC()
tl_atlas.SetTextFont(72)
tl_atlas.SetTextSize(tl_atlas.GetTextSize()*0.85)
tl_atlas.Draw()
tl_int = TLatex(0.35,0.32,"Internal")
tl_int.SetNDC()
tl_int.SetTextFont(42)
tl_int.SetTextSize(tl_int.GetTextSize()*0.85)
tl_int.Draw()
tl_energy = TLatex(0.19,0.25,"#sqrt{s} = 13 TeV, 36.1 fb^{-1}")
tl_energy.SetNDC()
tl_energy.SetTextFont(42)
tl_energy.SetTextSize(tl_energy.GetTextSize()*0.85)
tl_energy.Draw()
signal_legend = ""
if(br=="Doublet"):
    signal_legend = "SU(2) doublet"
elif(br=="Singlet"):
    signal_legend = "SU(2) singlet"
if signal_legend!="":
    tl_sigleg = TLatex(0.6,0.6,signal_legend)
    tl_sigleg.SetNDC()
    tl_sigleg.SetTextFont(42)
    tl_sigleg.SetTextSize(tl_sigleg.GetTextSize()*0.85)
    tl_sigleg.Draw()
#
gPad.RedrawAxis()
can.SetTickx()
can.SetTicky()
can.SetLogy()

can.Print(outDir + "/" + signal.upper()+"_" + br + "_" + combination + ".eps")
can.Print(outDir + "/" + signal.upper()+"_" + br + "_" + combination + ".pdf")
