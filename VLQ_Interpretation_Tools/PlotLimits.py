import os
#import string
import random
#import re
import time, getpass
import socket
import sys
import datetime
#import glob
#from array import array
from argparse import ArgumentParser
from LimitPlotUtils import LimitPlotter
#from ROOT import *
#import numpy as np

#from VLQCouplingCalculator import VLQCouplingCalculator as couplingCalculator
#from VLQCrossSectionCalculator import *

#sys.path.append(os.getenv("VLQCOMBDIR") + "/python/")
#from CombUtils import *

#gROOT.SetBatch(1)


##________________________________________________________
## OPTIONS
parser = ArgumentParser()
parser.add_argument("--inputDir",help="location of the limit files",required=True)
parser.add_argument("--outputDir",help="output folder",default="./test/")
parser.add_argument("--configs",help="",default="SPT_COMBINED")
parser.add_argument("--labels",help="list of labels",default="combined")
parser.add_argument("--addText",help="additional text to plot",default="")
parser.add_argument("--outSuffix",help="suffix in output file",default="")

parser.add_argument("--masses",help="comma-separated list of masses",default="")
parser.add_argument("--kappas",help="comma-separated list of kappas",default="")
parser.add_argument("--BRWs",help="comma-separated list of BR(T->bW) points",default="0.5")
parser.add_argument("--signal",help="signal interpretation. TSinglet or TDoublet",default="") #Only used for labelling

parser.add_argument("--useData",help="consider data",action="store",default=0, type=int)
parser.add_argument("--drawTheory",help="draw theory",action="store",default=0, type=int)
parser.add_argument("--drawExp",help="draw expected and observed limits",action="store",default=1, type=int )
parser.add_argument("--drawIndObs",help="draw individual observed limits",action="store",default=0, type=int )
parser.add_argument("--forceRanges",help="force ranges",action="store",default=0, type=int)
parser.add_argument("--drawRatio",help="make ratio panel",action="store",default=0, type=int)
parser.add_argument("--dataTag",help="tag used in limit file (asimov, data_mu0, data_mu1,...)", default="")

parser.add_argument("--do1DXSecPlots",help="Make 1D xsec vs mass plots",
                    action="store",default=1,type=int)
parser.add_argument("--do2DXSecPlots",help="Make 2D xsec limit plots in mass-kappa plane",
                    dest="do2DXSecPlots",action="store",default=0,type=int)
parser.add_argument("--do2DMKContour",help="Make 2D limit contours in mass-kappa plane",
                    dest="do2DMKContour",action="store",default=0,type=int)
parser.add_argument("--do2DGammaBRWContour",help="Make 2D mass limit contours in Gamma/M-BRW plane",
                    dest="do2DGammaBRWContour",action="store",default=0,type=int)

options = parser.parse_args()

inputDir=options.inputDir
outputDir=options.outputDir

configs = list(map(str, options.configs.strip('[]').split(',')))
labels = list(map(str, options.labels.strip('[]').split(',')))
signal=options.signal
addText=options.addText.replace("_"," ")
outSuffix=options.outSuffix

do1DXSecPlots=options.do1DXSecPlots
do2DXSecPlots=options.do2DXSecPlots
do2DMKContour=options.do2DMKContour
do2DGammaBRWContour=options.do2DGammaBRWContour

do2DPlots=do2DXSecPlots or do2DMKContour or do2DGammaBRWContour


MassList = [int(m) for m in options.masses.strip('[]').split(',')] if options.masses!="" \
           else [m for m in range(1000,2700,100)]
KappaList = [float(k) for k in options.kappas.strip('[]').split(',')]  if options.kappas!="" \
            else ( [0.1*k for k in range(1,16,1)] if do2DPlots else [0.5] )
BRWList = [float(w) for w in options.BRWs.strip('[]').split(',')]

#masses = list(map(str, options.masses.strip('[]').split(',')))
#kappas = list(map(str, options.kappas.strip('[]').split(',')))
#BRWs = list(map(str, options.BRWs.strip('[]').split(',')))

useData=options.useData
drawTheory=options.drawTheory
drawExp=options.drawExp
drawIndObs=options.drawIndObs
forceRanges=options.forceRanges
drawRatio=options.drawRatio
dataTag=options.dataTag

os.system("mkdir -p "+outputDir)

# Prepare for comparing multiple configurations in limit plots
doMulti = True if (len(configs)>1) else False
if len(labels) != len(configs):
    print("<!> ERROR !! Give labels of equal length when giving multiple input directories !!")
    sys.exit(-1)

if drawRatio and not doMulti:
    print("<!> ERROR !! Cannot do ratio panel if not given multiple input directories !!")
    sys.exit(-1)

#### Initialise the limit plotter
limPlotter = LimitPlotter(inputDir, outputDir, configs, 
                            MassList, KappaList, BRWList,
                            useData, drawTheory, drawExp, drawIndObs, drawRatio, forceRanges,
                            addText=addText,signal=signal,dataTag=dataTag)

print("do1DXSecPlots:",do1DXSecPlots)
print("do2DMKContour:",do2DMKContour)

if do1DXSecPlots:
    for _BRW in BRWList:
        for _kappa in KappaList:
            print('1D plot: k=',_kappa,' , BR=',_BRW)
            limPlotter.Make1DLimitPlot(_kappa, _BRW,outSuffix=outSuffix,labels=labels)

if do2DMKContour:
    for _BRW in BRWList:
        print('2D plot: BR=',_BRW)
        limPlotter.Make2DMassKappaPlot(_BRW,outSuffix=outSuffix,labels=labels)

##############################################################################
