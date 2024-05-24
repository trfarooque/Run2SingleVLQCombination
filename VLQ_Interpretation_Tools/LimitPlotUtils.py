import os
import sys
import glob
from array import array
from ROOT import *
import ctypes
import numpy as np
from scipy.interpolate import RBFInterpolator as rbf
#from scipy.interpolate import Rbf as rbf
import math


from VLQCouplingCalculator import VLQCouplingCalculator as couplingCalculator
from VLQCrossSectionCalculator import *

sys.path.append(os.getenv("VLQCOMBDIR") + "/python/")
from CombUtils import *

gROOT.SetBatch(1)

##.....................................................................................
## UTILITY FUNCTIONS
##.....................................................................................



##_____________________________________________________________________________________________
##
def GetGM(M,K,BRW,vlqMode='T'):
    vlq = couplingCalculator(M, vlqMode)
    ## Set the VLQ Parameters: kappa, xi parameterization as in https://arxiv.org/pdf/1305.4172.pdf
    vlq.setKappaxi(K, BRW, 0.5*(1.-BRW)) # kappa, xiW, xiZ. xiH = 1 - xiW - xiZ
            
    GM = vlq.getGamma()/M

    return GM
##_____________________________________________________________________________________________
##
def FitFunctionAndDefineIntersection( Theory, Med, isData ):
    '''
    Function to determine the intersection between theory and limits by
    doing an exponential extrapolation between the different points for
    the expected/observe limit.
    '''
    diff_min = 1000
    for i in range(0,Theory.GetN()-1):

        x_ini_th = ctypes.c_double(-1)
        x_end_th = ctypes.c_double(-1)
        x_ini_ex = ctypes.c_double(-1)
        x_end_ex = ctypes.c_double(-1)

        y_ini_th = ctypes.c_double(-1)
        y_end_th = ctypes.c_double(-1)
        y_ini_ex = ctypes.c_double(-1)
        y_end_ex = ctypes.c_double(-1)

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

        # Convert c_double to float
        x_ini_th_value = x_ini_th.value
        x_end_th_value = x_end_th.value
        
        # Correct the range calculation
        for x in range(0, int(x_end_th_value - x_ini_th_value)):

        #for x in range(0,int(x_end_th-x_ini_th)):

            xmod=x_ini_th_value+x
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

    return x_int, y_int, vertical

##____________________________________________________________________________________________
def SumQuad(val1,val2):
    return np.sqrt(val1**2 + val2**2)



##____________________________________________________________________________________________
def GetLimitContour(gr_xsratio_lim, level=1.0, linecolor=kBlack, linestyle=1,smooth=1.0,mode='linear',degree=4):
#def GetLimitContour(h_cont, level=1.0, linecolor=kBlack, linestyle=1):
    #h_cont = gr_xsratio_lim.GetHistogram().Clone("smooth_{}".format(gr_xsratio_lim.GetName()))
    #h_cont.SetDirectory(0)

    #Get interpolated histogram
    h_cont=GetSmoothHist(gr_xsratio_lim,smooth=smooth,mode=mode,degree=degree)
    h_cont.SetContour(1)
    h_cont.SetContourLevel(0,1.0)

    h_cont.Draw("cont list")
    gPad.Update()
    contours = gROOT.GetListOfSpecials().FindObject("contours")
    ncontours = contours.GetSize()
    nparts = contours.At(0).GetSize()
    #gr_cont=contours.At(0).First().Clone("cont_{}".format(gr_xsratio_lim.GetName()))
    gr_cont=contours.At(0).First().Clone("cont_{}".format(h_cont.GetName()))
    gr_cont.SetLineColor(linecolor)
    gr_cont.SetLineStyle(linestyle)
    gr_cont.SetLineWidth(2)
    gROOT.GetListOfSpecials().FindObject("contours").RemoveAll()
    #print('ncontours: ',ncontours,'; first_contour_size: ',nparts)

    return gr_cont

##____________________________________________________________________________________________
def DoSmoothingComparisons(gr,zmin,zmax,doContours=False,smooth=1.0):

    npt = gr.GetN()
    x=ctypes.c_double(0.)
    y=ctypes.c_double(0.)
    z=ctypes.c_double(0.)

    n_sparse = gr.GetN()
    x_sparse=np.empty(n_sparse)
    y_sparse=np.empty(n_sparse)
    z_sparse=np.empty(n_sparse)

    h_gr = gr.GetHistogram().Clone("sparse_{}".format(gr.GetName()))
    h_gr.SetDirectory(0)
    h_gr.Reset()   
    for i in range(n_sparse):
        gr.GetPoint(i,x,y,z)
        x_sparse[i] = x.value
        y_sparse[i] = y.value
        z_sparse[i] = math.log(z.value)
        #z_sparse[i] = z.value
        h_gr.Fill(x.value,y.value,z.value)

    tempcan=TCanvas("can_sparse_"+gr.GetName(),"",800,800)
    tempcan.SetBottomMargin(0.15)
    tempcan.SetLeftMargin(0.15)
    tempcan.SetRightMargin(0.14)
    tempcan.SetTopMargin(0.05)
    tempcan.cd()
    hframe=gPad.DrawFrame(1000.,0.1,2300.,1.2)
    hframe.GetXaxis().SetTitle("m_{T} [GeV]")
    hframe.GetYaxis().SetTitle("#kappa_{T} [GeV]")
    tempcan.Update()
    h_gr.GetZaxis().SetRangeUser(0.,0.25)
    h_gr.Draw("same colz")
    tempcan.SaveAs("can_sparse_"+gr.GetName()+".png")

    h_cont = gr.GetHistogram().Clone("smoothROOT_{}".format(gr.GetName()))
    h_cont.SetDirectory(0)

    if doContours:
        h_cont.SetContour(1)
        h_cont.SetContourLevel(0,1.0)
        h_cont.Draw("cont list")
        gPad.Update()
        contours = gROOT.GetListOfSpecials().FindObject("contours")
        ncontours = contours.GetSize()
        nparts = contours.At(0).GetSize()
        gr_cont=contours.At(0).First().Clone("contROOT_{}".format(h_cont.GetName()))

        gr_cont.SetLineColor(kBlack)
        gr_cont.SetLineWidth(2)
        gROOT.GetListOfSpecials().FindObject("contours").RemoveAll()

    tempcan=TCanvas("can_smoothROOT_"+gr.GetName(),"",800,800)
    tempcan.SetBottomMargin(0.15)
    tempcan.SetLeftMargin(0.15)
    tempcan.SetRightMargin(0.14)
    tempcan.SetTopMargin(0.05)
    tempcan.cd()
    hframe=gPad.DrawFrame(1000.,0.1,2300.,1.2)
    hframe.GetXaxis().SetTitle("m_{T} [GeV]")
    hframe.GetYaxis().SetTitle("#kappa_{T} [GeV]")
    tempcan.Update()

    h_cont.GetZaxis().SetRangeUser(0.,0.25)
    h_cont.Draw("same colz")
    if doContours:
        gr_cont.Draw("c same")
    tempcan.SaveAs("can_smoothROOT_"+gr.GetName()+".png")
    
    ##########################################################
    #Compare smoothing algorithms here
    ##########################################################
    
    modeList = ['cubic','thin_plate','linear']
    #modeList = ['cubic','thin_plate_spline','linear']
    degreeList = [1]#,2,3,4]
    ln_cols = [kBlue+1,kMagenta,kOrange+4,kRed,kGreen+1] # max compare 5 configurations

    smoothList = {}
    contourList = {} if doContours else None
    for mode in modeList:
        for degree in degreeList:
            h_smooth = GetSmoothHist(gr,smooth=smooth,mode=mode,degree=degree)
            smoothList['{}_{}'.format(mode,degree)] = h_smooth
            if doContours:
                h_cont = GetLimitContour(gr,level=1.0, linecolor=kBlack, 
                                         linestyle=1,smooth=smooth,mode=mode,degree=degree)
                contourList['{}_{}'.format(mode,degree)] = h_cont

            tempcan = TCanvas("can_{}".format(h_smooth.GetName()), "", 800, 800)
            tempcan.SetBottomMargin(0.15)
            tempcan.SetLeftMargin(0.15)
            tempcan.SetRightMargin(0.14)
            tempcan.SetTopMargin(0.05)
            tempcan.cd()
            hframe=gPad.DrawFrame(1000.,0.1,2300.,1.2)
            hframe.GetXaxis().SetTitle("m_{T} [GeV]")
            hframe.GetYaxis().SetTitle("#kappa_{T} [GeV]")
            tempcan.Update()
            h_smooth.GetZaxis().SetRangeUser(zmin,zmax)
            h_smooth.Draw("same colz")
            if doContours:
                h_cont.Draw("same c")
            tempcan.SaveAs("{}.png".format(tempcan.GetName()))    


    #####
    if doContours:
        for degree in degreeList:
        #for mode in modeList:
            tempcan = TCanvas("can_smoothComp_{}_{}".format(gr.GetName(),degree), "", 800, 800)
            tempcan.SetBottomMargin(0.15)
            tempcan.SetLeftMargin(0.15)
            tempcan.SetRightMargin(0.05)
            tempcan.SetTopMargin(0.05)
            tempcan.cd()
            hframe=gPad.DrawFrame(1000.,0.1,2300.,1.2)
            hframe.GetXaxis().SetTitle("m_{T} [GeV]")
            hframe.GetYaxis().SetTitle("#kappa_{T} [GeV]")
            tempcan.Update()

            leg = TLegend(0.57,0.6,0.82,0.9)
            leg.SetFillColor(0)
            leg.SetFillStyle(0)
            leg.SetLineColor(0)
            leg.SetLineStyle(0)
            leg.SetBorderSize(0)
            leg.SetTextSize(0.028)

            leg.AddEntry(gr_cont, "ROOT Delauney", "l")
            gr_cont.Draw("same c")
            #for n,degree in enumerate(degreeList):
            for n,mode in enumerate(modeList):
                contourList['{}_{}'.format(mode,degree)].SetLineColor(ln_cols[n])
                contourList['{}_{}'.format(mode,degree)].Draw("same c")
                #leg.AddEntry(contourList['{}_{}'.format(mode,degree)], "degree:{}".format(degree), "l")
                leg.AddEntry(contourList['{}_{}'.format(mode,degree)], "mode:{}".format(mode), "l")
            leg.Draw()
            tempcan.SaveAs("{}.png".format(tempcan.GetName()))    


    return



##____________________________________________________________________________________________
def GetSmoothHist(gr,smooth=1.0,mode="linear",degree=4):

    npt = gr.GetN()
    x=ctypes.c_double(0.)
    y=ctypes.c_double(0.)
    z=ctypes.c_double(0.)

    n_sparse = gr.GetN()
    x_sparse=np.empty(n_sparse)
    y_sparse=np.empty(n_sparse)
    z_sparse=np.empty(n_sparse)

    for i in range(n_sparse):
        gr.GetPoint(i,x,y,z)
        x_sparse[i] = x.value
        y_sparse[i] = y.value
        z_sparse[i] = math.log(z.value)
    sparse_points = np.stack([x_sparse, y_sparse], -1)# shape (N, 2) in 2d

    h_cont = gr.GetHistogram().Clone("smooth_{}_{}_{}_{}".format(smooth, mode, degree, gr.GetName()))
    h_cont.SetDirectory(0)
    h_cont.Reset()

    n_dense=h_cont.GetNbinsX()*h_cont.GetNbinsY()
    x_dense=np.empty(n_dense)
    y_dense=np.empty(n_dense)

    k=0
    for i in range(1,h_cont.GetXaxis().GetNbins()+1):
        for j in range(1,h_cont.GetYaxis().GetNbins()+1):
            x_dense[k]= h_cont.GetXaxis().GetBinCenter(i)
            y_dense[k]= h_cont.GetYaxis().GetBinCenter(j)

            if( GetGM(x_dense[k],y_dense[k],0.5) ) > 0.5:
                break

            k+=1

    dense_points = np.stack([x_dense, y_dense], -1)  # shape (N, 2) in 2d
    z_rbf = rbf(sparse_points, z_sparse.ravel(),smoothing=smooth,kernel=mode,degree=degree)
    z_dense = z_rbf(dense_points)  
    #z_rbf = rbf(x_sparse,y_sparse, z_sparse,smoothing=smooth,function=mode)
    #z_dense = z_rbf(x_dense,y_dense)


    k=0
    for i in range(1,h_cont.GetXaxis().GetNbins()+1):
        for j in range(1,h_cont.GetYaxis().GetNbins()+1):

            mass= h_cont.GetXaxis().GetBinCenter(i)
            kappa= h_cont.GetYaxis().GetBinCenter(j)

            if( GetGM(mass,kappa,0.5) ) > 0.5:
                break
            h_cont.SetBinContent(i,j,math.exp(z_dense[k]))
            k+=1

    return h_cont


##____________________________________________________________________________________________
def GetLimitContourList(gr_xsratio_lim, levels, linecolor=kBlack,smooth=1.0,mode='linear',degree=4):

    arr_levels = np.array(levels)
    #Get interpolated histogram
    print("GetLimitContourList : ",gr_xsratio_lim.GetName())
    h_cont=GetSmoothHist(gr_xsratio_lim,smooth=smooth,mode=mode,degree=degree)
    #h_cont = gr_xsratio_lim.GetHistogram().Clone("smooth_{}".format(gr_xsratio_lim.GetName()))
    #h_cont.SetDirectory(0)
    h_cont.SetContour(len(levels),arr_levels)

    h_cont.Draw("cont list")
    gPad.Update()
    contours = gROOT.GetListOfSpecials().FindObject("contours")
    ncontours = contours.GetSize()

    grList_cont=[]
    for n,contList in enumerate(contours):
        #gr_cont=contList.First().Clone("cont_{}_{}".format(gr_xsratio_lim.GetName(),levels[n]))
        even=((-1)**n < 0)
        for k,gr in enumerate(contList):
            gr_cont=gr.Clone("cont_{}_{}_{}".format(gr_xsratio_lim.GetName(),levels[n],k))
            gr_cont.SetLineColor(linecolor)
            gr_cont.SetLineWidth(2)
            gr_cont.SetLineStyle(7) if even else gr_cont.SetLineStyle(1)
            grList_cont +=[gr_cont]
        #print('n: ',n,'; parts: ',len(contList))
    gROOT.GetListOfSpecials().FindObject("contours").RemoveAll()
    #print('ncontours: ',ncontours,'; first_contour_size: ',nparts)

    return grList_cont

##____________________________________________________________________________________________
def MakeErrorBand(gr_p, gr_m, fillcolor=kGray, setaxis=False, 
                  xtitle="m_{T} [GeV]", ytitle="#kappa"):
    gr_band = TGraph()

    for i in range(gr_p.GetN()):
        gr_band.SetPoint(i,gr_p.GetPointX(i),gr_p.GetPointY(i))

    # corner point
    gr_band.SetPoint(gr_p.GetN(),gr_m.GetPointX(gr_m.GetN()-1),gr_p.GetPointY(gr_p.GetN()-1))

    for i in range(gr_m.GetN()):
        gr_band.SetPoint(gr_p.GetN()+gr_m.GetN()-i,gr_m.GetPointX(i),gr_m.GetPointY(i))

    # final closing
    gr_band.SetPoint(gr_band.GetN(),gr_band.GetPointX(gr_band.GetN()-1),gr_band.GetPointY(0))

    gr_band.SetLineColor(0)
    gr_band.SetFillColor(fillcolor)

    return gr_band


##____________________________________________________________________________________________
def GetGammaBorder(tg_GM):

    tmp_can = TCanvas()
    tmp_can.cd()
    tg_GM.Draw("cont list")
    tmp_can.Update()
    conts = gROOT.GetListOfSpecials().FindObject("contours")
    tg_gm_border = conts.At(0).First().Clone("gm_border")
    gROOT.GetListOfSpecials().FindObject("contours").RemoveAll()

    return tg_gm_border

##____________________________________________________________________________________________
def GetGammaContours(gmLevels, tg_GM):#, canvas):

    contours = []
    contour_labels = []
    for i,gm in enumerate(gmLevels):
        even = ((-1)**i < 0)
        contours += [tg_GM.Clone("gmclon{}".format(i))]
        contours[i].GetHistogram().SetDirectory(0)
        contours[i].GetHistogram().SetContour(1)
        contours[i].GetHistogram().SetContourLevel(0,gm)
        contours[i].SetLineWidth(1)
        contours[i].SetLineColor(kGray+2)
        contours[i].SetLineStyle(7)
            
        gm_text = "#Gamma_{T}/M_{T}="+"%.0f"%(100*gm)+"%"

        if gm==0.05:
            text_angle = -12.5
            text_x = 2090
            text_y = 0.21
        elif  gm==0.1:
            text_angle = -11
            text_x = 2190
            text_y = 0.275
        elif  gm==0.2:
            text_angle = -11
            text_x = 2250
            text_y = 0.37
        elif  gm==0.5:
            text_angle = -13
            text_x = 2170
            text_y = 0.59

        contour_labels += [TLatex(text_x,text_y,gm_text)]
        contour_labels[i].SetTextAngle(text_angle)

        contour_labels[i].SetTextSize(0.028)
        contour_labels[i].SetTextFont(42)
        contour_labels[i].SetTextColor(kGray+2)


    return [ contours, contour_labels ]

##____________________________________________________________________________________________
def SetRootPalette():
        # Palette
        '''
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
        '''
        gStyle.SetPalette(72)

        return

##.....................................................................................

##.....................................................................................
## CLASS CONTAINER FOR EXP LIMIT INFORMATION
##.....................................................................................
class ExpInfo:

    def __init__(self):
        self.expLim = {"obs":-1.,
                       "exp":-1.,
                       "exp_p2":-1., #+2sig
                       "exp_p1":-1., #+1sig
                       "exp_m2":-1., #-2sig
                       "exp_m1":-1.} #-1sig

    #..................................................................
    def ExtractLimitsFromFile(self,fname,useData):

        infile = TFile(fname,"read")
        h_lim = infile.Get("limit")

        self.expLim["obs"] = h_lim.GetBinContent(1) if useData else -1.
        self.expLim["exp"] = h_lim.GetBinContent(2)
        self.expLim["exp_p2"] = h_lim.GetBinContent(3)
        self.expLim["exp_p1"] = h_lim.GetBinContent(4)
        self.expLim["exp_m1"] = h_lim.GetBinContent(5)
        self.expLim["exp_m2"] = h_lim.GetBinContent(6)

        return

##.....................................................................................
## CLASS CONTAINER FOR THEORY INFORMATION
##.....................................................................................
class TheoryInfo:

    #..................................................................
    def __init__(self, mass, kappa, BRW):

        self.mass = mass
        self.kappa = kappa
        self.BRW = BRW
        self.BRZ = 0.5*(1-BRW)
        self.GM = 0.
        self.xsec = -1.
        self.xsecUp = -1.
        self.xsecDown = -1.

    #..................................................................
    def CalcTheory(self,vlqMode='T', sigModes=["WTHt","WTZt","ZTHt","ZTZt"]):

        vlq = couplingCalculator(self.mass, vlqMode)
        ## Set the VLQ Parameters: kappa, xi parameterization as in https://arxiv.org/pdf/1305.4172.pdf
        vlq.setKappaxi(self.kappa, self.BRW, self.BRZ) # kappa, xiW, xiZ. xiH = 1 - xiW - xiZ
            
        cVals = vlq.getc_Vals()
        BR = vlq.getBRs()
        #Gamma = vlq.getGamma()
        self.GM = vlq.getGamma()/self.mass

        # Key map: 0=W; 1=Z; 2=H
        keyDictionary = {"WT": 0,"ZT": 1,"HT": 2}
        self.xsec=0.
        self.xsecUp=0.
        self.xsecDown=0.
        for sig in sigModes:
        
            prodIndex = keyDictionary[sig[:2:]]
            decayIndex = keyDictionary[sig[2::].upper()]
                
            xsecMode = XS_NWA(self.mass, cVals[prodIndex], sig[:2:])*BR[decayIndex]*\
            FtFactor(proc=sig, mass=self.mass, GM=self.GM, useAverageXS = True)[0]/\
            PNWA(proc=sig, mass=self.mass, GM=self.GM)
            self.xsec += xsecMode
        XSecErrors = XSUncertainty(self.mass)
        self.xsecUp = XSecErrors[0]*self.xsec
        self.xsecDown = XSecErrors[1]*self.xsec

        return


##.....................................................................................
## CLASS CONTAINER FOR INFO RELATING TO EACH SIGNAL POINT
##.....................................................................................
class LimitPointInfo:

    #..................................................................
    def __init__(self, mass, kappa, BRW, cfgList):

        self.sigTag = getSigTag(mass,kappa,BRW)
        self.cfgList = cfgList

        self.mass = mass
        self.kappa = kappa
        self.BRW = BRW
        self.BRZ = 0.5*(1-BRW)
        self.GM = 0.
        self.norm_xsec = 0.1
        self.theoryInfo = TheoryInfo(mass, kappa, BRW)
        self.expInfo = {}

    #..................................................................
    def ReadExpLimits(self,dataTag,baseDir,cfg,useData):

        indir = baseDir + '/' + cfg + '/'
        pathname = indir + cfg + "_limits_" + self.sigTag + "_" + dataTag + ".root"
        files = glob.glob(pathname)

        if len(files)==0 or len(files)>1:
            print("<!> ERROR for", cfg, "signal", self.sigTag," !! --> nFiles = ",len(files))
            return
        
        self.expInfo[cfg] = ExpInfo()
        self.expInfo[cfg].ExtractLimitsFromFile(files[0],useData)

        return

    #..................................................................
    def FillInfo(self,dataTag,baseDir,drawExp,useData):

        self.theoryInfo.CalcTheory()

        if(drawExp and (self.theoryInfo.GM<=0.5)): 
            for cfg in self.cfgList:
                if(self.mass>2300 and cfg=='SPT_HTZT'):
                    continue
                self.ReadExpLimits(dataTag,baseDir,cfg,useData)
        return



##____________________________________________________________________________________________

class LimitPlotter:

    def __init__(self, inputDir, outputDir, configList, massList, kappaList, BRWList,
                 useData=True, drawTheory=True, drawExp=True, drawRatio=True, forceRanges=False,
                 addText='',signal='',dataTag=''):

        self.inputDir=inputDir
        self.outputDir=outputDir
        self.configList=configList
 
        self.massList=massList
        self.kappaList=kappaList
        self.BRWList=BRWList

        self.nConfigs=len(configList)
        self.nMasses=len(massList)
        self.nKappas=len(kappaList)
        self.nBRWs=len(BRWList)

        print('nConfigs:',self.nConfigs)
        print('nMasses:',self.nMasses)
        print('nKappas:',self.nKappas)
        print('nBRWs:',self.nBRWs)

        self.useData=useData
        self.drawTheory=drawTheory
        self.drawExp=drawExp
        self.drawRatio=drawRatio
        self.forceRanges=forceRanges

        self.addText=addText
        self.signal=signal
        self.signal_label = "T"
        if signal=="TSinglet":
            self.signal_label += " singlet"
        elif signal=="TDoublet":
            self.signal_label += " doublet"

        self.dataTag= ("data" if useData else "asimov_mu0") if dataTag=="" else dataTag

        #cfg,mass,kappa,BRW
        self.limitInfoDict={} 
        for BRW in BRWList:
            self.limitInfoDict[BRW] = {}
            for Kappa in kappaList:
                self.limitInfoDict[BRW][Kappa] = {}
                for Mass in massList:
                    #print('Mass:',Mass,' Kappa:',Kappa,' BRW:',BRW)
                    self.limitInfoDict[BRW][Kappa][Mass] = LimitPointInfo(Mass, Kappa, BRW, self.configList)
                    self.limitInfoDict[BRW][Kappa][Mass].FillInfo(
                        self.dataTag,self.inputDir,self.drawExp,self.useData)
                    #for attr, value in vars(self.limitInfoDict[BRW][Kappa][Mass]).items():
                    #    print(f"{attr}: {value}")
                    #print("----------------------------------------------------\n")
        return

    def Setup2DCanvas(self,canv_name,plot_mode):
        
        can = TCanvas(canv_name,canv_name,900,900)
        can.SetBottomMargin(0.15)
        can.SetLeftMargin(0.15)
        if plot_mode=="2DMKCONTOUR":
            can.SetRightMargin(0.05)
        else:
            can.SetRightMargin(0.14)
            
        can.SetTopMargin(0.05)
        can.cd()
        hframe=gPad.DrawFrame(self.massList[0],self.kappaList[0],self.massList[-1],self.kappaList[-1])
        hframe.GetXaxis().SetTitle("m_{T} [GeV]")
        hframe.GetYaxis().SetTitle("#kappa_{T} [GeV]")
        can.Update()
        
        return can

    def SetLegendStyle(self,leg,textsize):
        leg.SetFillColor(0)
        leg.SetFillStyle(0)
        leg.SetLineColor(0)
        leg.SetLineStyle(0)
        leg.SetBorderSize(0)
        leg.SetTextSize(textsize)

        return

    def SetATLASLabels(self, atl_x, atl_y, siglabel, worklabel="Internal"):

        tl_list = []
        tl_atlas = TLatex(atl_x,atl_y,"ATLAS")
        tl_atlas.SetNDC()
        tl_atlas.SetTextFont(72)
        tl_atlas.SetTextSize(tl_atlas.GetTextSize()*0.77)
        tl_list += [tl_atlas]

        tl_int = TLatex(atl_x+0.15,atl_y,worklabel)                                      
        tl_int.SetNDC()
        tl_int.SetTextFont(42)
        tl_int.SetTextSize(tl_int.GetTextSize()*0.77)
        tl_list += [tl_int]

        tl_energy = TLatex(atl_x,atl_y-0.045,"#sqrt{s} = 13 TeV, 139 fb^{-1}")
        tl_energy.SetNDC()
        tl_energy.SetTextFont(42)
        tl_energy.SetTextSize(tl_energy.GetTextSize()*0.77)
        tl_list += [tl_energy]
        
        tl_siglabel = TLatex(atl_x,atl_y-0.09,siglabel)
        tl_siglabel.SetNDC()
        tl_siglabel.SetTextSize(0.03)
        tl_siglabel.SetTextFont(42)
        tl_list += [tl_siglabel]

        return tl_list

    #............................................................
    def Make1DLimitPlot(self,_kappa,_BRW,outSuffix="",labels=None):

        _labels = self.configList if labels is None else labels
        limitList = self.limitInfoDict[_BRW][_kappa]
        #print(limitList)
        gr_cols = [kBlack,kBlue+1,kMagenta,kOrange+4,kRed] # max compare 5 configurations
        gr_fills = [3002,3004,3005,3007,3008]

        ###################### Make and fill all required TGraphs filled ###############
        
        tmg_main = TMultiGraph()
        tmg_ratio = TMultiGraph() if self.drawRatio else None
        
        leg = TLegend(0.57,0.6,0.82,0.9)
        leg.SetFillColor(0)
        leg.SetFillStyle(0)
        leg.SetBorderSize(0)
        

        if self.drawExp:

            tg_obs = [TGraph() for i in range(self.nConfigs)]
            tg_exp = [TGraph() for i in range(self.nConfigs)]
            tg_exp1s = [TGraph() for i in range(self.nConfigs)]
            tg_exp2s = [TGraph() for i in range(self.nConfigs)]
            
            tg_ratio = [TGraph() for i in range(self.nConfigs)] if self.drawRatio else None

            counter = -1
            for n,cfg in enumerate(self.configList):
                #number of points in this graph
                gr_len = sum( ((limitList[Mass].theoryInfo.GM<0.5) and \
                               (Mass<=2100 or cfg!='SPT_HTZT')) for Mass in self.massList)
                print(n,cfg,' : ',gr_len)
                    
                ###########################################################
                #Set graph styles and add to the multigraph
                if n==0:
                    tg_exp2s[n].SetLineColor(kYellow)
                    tg_exp2s[n].SetFillColor(kYellow)
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
        
                    if self.useData:
                        tg_obs[n].SetLineColor(kBlack)
                        tg_obs[n].SetLineWidth(3)
                        tg_obs[n].SetLineStyle(1)
                        tmg_main.Add(tg_obs[n], "l")
                        leg.AddEntry(tg_obs[n],"95% CL observed limit","l")

                else:
                    tg_exp[n].SetLineColor(gr_cols[n])
                    tg_exp[n].SetFillColor(gr_cols[n])
                    tg_exp[n].SetFillStyle(3005)
                    tg_exp[n].SetLineWidth(3)
                    tg_exp[n].SetLineStyle(2)
                    print("Adding exp line :",n)
                    tmg_main.Add(tg_exp[n], "l")
                    leg.AddEntry(tg_exp[n],_labels[n],"l")
                    

                if self.drawRatio:
                    tg_ratio[n].SetLineColor(gr_cols[n])
                    tg_ratio[n].SetLineWidth(3)
                    tg_ratio[n].SetLineStyle(2)
                    tmg_ratio.Add(tg_ratio[n], "l")
                ###########################################################


                ###########################################################
                ### Fill the graphs #####
                counter = -1
                for Mass in self.massList:
                    counter=counter+1
                    if((limitList[Mass].theoryInfo.GM>0.5) or \
                       (Mass>2100 and cfg=='SPT_HTZT')):
                        break

                    norm_xsec = limitList[Mass].norm_xsec
                    if cfg in limitList[Mass].expInfo:
                        expInfo = limitList[Mass].expInfo[cfg]
                        tg_obs[n].SetPoint(counter,Mass,(expInfo.expLim["obs"])*norm_xsec)
                        tg_exp[n].SetPoint(counter,Mass,(expInfo.expLim["exp"])*norm_xsec)
                        tg_exp1s[n].SetPoint(counter,Mass,(expInfo.expLim["exp_p1"])*norm_xsec)
                        tg_exp2s[n].SetPoint(counter,Mass,(expInfo.expLim["exp_p2"])*norm_xsec)
                        tg_exp1s[n].SetPoint(2*gr_len-counter-1,Mass,(expInfo.expLim["exp_m1"])*norm_xsec)
                        tg_exp2s[n].SetPoint(2*gr_len-counter-1,Mass,(expInfo.expLim["exp_m2"])*norm_xsec)
                        
                    if self.drawRatio:
                        tg_ratio[n].SetPoint(counter,Mass,tg_exp[n].Eval(Mass)
                                             /tg_exp[0].Eval(Mass))
            ###########################################################
        if self.drawTheory:
            tg_theory = TGraphAsymmErrors()
            tg_theory.SetLineColor(kRed)
            tg_theory.SetFillColor(kRed-9)
            tg_theory.SetLineWidth(2)
            print("Adding theory")
            tmg_main.Add(tg_theory, "4lx")
            leg.AddEntry(tg_theory,"Theory (NLO)","lf")

            wideM=-1
            max_mass = -1
            for iMass,Mass in enumerate(self.massList):
                if(limitList[Mass].theoryInfo.GM>0.5):
                    wideM=Mass
                    break
                max_mass = Mass
                tg_theory.SetPoint(iMass,Mass,limitList[Mass].theoryInfo.xsec)
                tg_theory.SetPointError(iMass,0,0,
                                        limitList[Mass].theoryInfo.xsecDown,
                                        limitList[Mass].theoryInfo.xsecUp)
            print('BRW:',_BRW,' Kappa:',_kappa,'==>wideM : ',wideM)
        
        #To remove all TGraph objects with no points from the TMultiGraph i
        graph_list = tmg_main.GetListOfGraphs()
        for graph in graph_list:
            if isinstance(graph, ROOT.TGraph) and graph.GetN() == 0:
                graph_list.Remove(graph)

        ###################### All required TGraphs made and filled ########################

        ###################### Make canvases and draw the graphs ###############

        ###
        # Creating the canvas
        ###
        if self.signal=="": self.signal_label = "T_K{}_BRW{}_{}".format(_kappa,_BRW,self.dataTag)
        canv_name = "1DXSecLimit_"+self.signal+"_{}".format(_kappa)
        if self.drawRatio:
            can = TCanvas(canv_name,canv_name,1000,1150)
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
            can = TCanvas(canv_name,canv_name,1000,800)
            can.SetBottomMargin(0.15)
            can.SetLeftMargin(0.15)
            can.SetRightMargin(0.05)
            can.SetTopMargin(0.05)
        ###
        # Limits
        ###
        if self.drawRatio:
            #first draw the ratio plots
            pad2.cd()
            tmg_ratio.Draw("a")
            tmg_ratio.GetHistogram().GetXaxis().SetLimits(1000., 2750.)
            pad1.cd()
        else:
            can.cd()
        tmg_main.Draw("a")
        #tmg_main.GetXaxis().SetNdivisions(406)
        tmg_main.SetTitle("")
        tmg_main.GetXaxis().SetTitle("m_{T} [GeV]")
        tmg_main.GetYaxis().SetTitle("#sigma(pp #rightarrow qb(T #rightarrow Ht/Zt)) [pb]")
        tmg_main.GetHistogram().GetXaxis().SetLabelSize(
            tmg_main.GetHistogram().GetXaxis().GetLabelSize()*1.3)
        tmg_main.GetHistogram().GetYaxis().SetLabelSize(
            tmg_main.GetHistogram().GetYaxis().GetLabelSize()*1.3)
        tmg_main.GetHistogram().GetXaxis().SetTitleSize(
            tmg_main.GetHistogram().GetXaxis().GetTitleSize()*1.6)
        tmg_main.GetHistogram().GetYaxis().SetTitleSize(
            tmg_main.GetHistogram().GetYaxis().GetTitleSize()*1.6)
        tmg_main.GetHistogram().GetXaxis().SetTitleOffset(1.32)
        tmg_main.GetHistogram().GetYaxis().SetTitleOffset(1.4)
        #tmg_main.GetHistogram().SetMaximum(3)

        if self.forceRanges:
            tmg_main.GetYaxis().SetRangeUser(0.005,3)
            tmg_main.GetHistogram().GetXaxis().SetLimits(1000., 2750.)

            # Add a vertical line at the last mass value
            if wideM != -1:
                if self.drawRatio:
                    #first draw the ratio plots
                    pad2.cd()
                    max_ratio = tmg_ratio.GetHistogram().GetMaximum()
                    min_ratio = tmg_ratio.GetHistogram().GetMinimum()
                    line_pad2 = TLine(max_mass,min_ratio,max_mass,max_ratio)
                    line_pad2.SetLineColor(kGray+2)
                    line_pad2.SetLineStyle(2)
                    line_pad2.SetLineWidth(2)
                    line_pad2.Draw()
                    pad1.cd()
    
                else:
                    can.cd()
            
                max_Y = tmg_main.GetHistogram().GetMaximum()
                min_Y = tmg_main.GetHistogram().GetMinimum()
                line_pad1 = TLine(max_mass,min_Y,max_mass,max_Y*0.04)
                line_pad1.SetLineColor(kGray+2)
                line_pad1.SetLineStyle(2)
                line_pad1.SetLineWidth(2)
                line_pad1.Draw()
        
        else: 
            tmg_main.GetHistogram().SetMinimum(0.0001)
            tmg_main.GetXaxis().SetRangeUser(self.massList[0], self.massList[-1])


        ROOT.gPad.Modified();ROOT.gPad.Update()

        leg.SetTextSize(0.028)
        leg.Draw()
        

        #Intersections
        intersx = FitFunctionAndDefineIntersection(tg_theory,tg_exp[0],isData=False )
        print("Expected mass limit [GeV]: %.1f" % intersx[0])
        print("Expected xsec limit [pb]: %.4f" % intersx[1])
        #intersx[2].Draw("lp")
        if(self.useData):
            intersxData=FitFunctionAndDefineIntersection(tg_theory,tg_obs[0],isData=True )
            print("Observed limit [GeV]: %.1f" % intersxData[0])
            print("Observed xsec limit [pb]: %.4f" % intersxData[1])
        
        atl_x = 0.19
        atl_y = 0.88
        tl_list = self.SetATLASLabels(atl_x, atl_y, "{}, #kappa={}".format(self.signal_label.replace("_", " "), _kappa), worklabel="Internal")
        for tl in tl_list:
            tl.Draw()

        

        gPad.SetLogy(1)
        gPad.RedrawAxis()
        can.SetTickx()
        can.SetTicky()
        ROOT.gPad.Modified();ROOT.gPad.Update()
        printName = self.outputDir + "/" + canv_name.upper()+outSuffix
        can.SaveAs(printName+".png")
        can.SaveAs(printName+".pdf")
        can.SaveAs(printName+".eps")
        return

    #............................................................
    def Make2DMassKappaPlot(self,_BRW,outSuffix="",labels=None):

        SetRootPalette()
        gr_cols = [kBlack,kBlue+1,kMagenta,kOrange+4,kRed] # max compare 5 configurations
        signal_label = self.signal_label+" #xi_{{W}}={}".format(_BRW)

        atl_x = 0.19
        atl_y = 0.88
        tl_list = self.SetATLASLabels(atl_x, atl_y, signal_label, worklabel="Internal")

        _labels = self.configList if labels is None else labels
        limitList = self.limitInfoDict[_BRW]

        tg_theory_xsec = TGraph2D()
        tg_theory_xsec.SetName("tg_theory_xsec")
        tg_theory_GammaM = TGraph2D()
        tg_theory_GammaM.SetName("tg_theory_GammaM")

        iPoint=0
        for Mass in self.massList:
            for Kappa in self.kappaList:
                if self.drawTheory:
                    tg_theory_xsec.SetPoint(iPoint,Mass,Kappa,limitList[Kappa][Mass].theoryInfo.xsec)
                    tg_theory_GammaM.SetPoint(iPoint,Mass,Kappa,limitList[Kappa][Mass].theoryInfo.GM)
                iPoint = iPoint+1
        
        print("Total calculated points", iPoint)
        ####### Get Gamma/M contours with associated labels #########
        GMLevels = [0.05,0.10,0.20,0.50]
        gm_contourset = GetGammaContours(GMLevels, tg_theory_GammaM)#, canv)
        #gm_border = GetGammaBorder(gm_contourset[0][-1])
        #gm_border.SetPoint(gm_border.GetN(),self.massList[0],self.kappaList[-1])
        #gm_border.SetPoint(gm_border.GetN(),self.massList[-1],self.kappaList[-1])
        #gm_border.SetFillColor(kGray)
        #gm_border.SetFillStyle(1)
        gammaMax = 0.5
        c = vlq()
        masses = list(range(1000,2700,10))
        gm_border = ROOT.TGraph(2*len(masses))
        Nmasses = len(masses)
        for ii in range(Nmasses):
            _m = masses[ii]*1.0
            c.setMVLQ(_m)
            c.setGammaBRs(_m*gammaMax, _BRW, (1-_BRW)/2.)
            cw = c.getc_Vals()[0]
            k = c.getKappa()
            gm_border.SetPoint(ii,_m,k-0.001)
            _m = masses[Nmasses-ii-1]*1.0
            c.setMVLQ(_m)
            c.setGammaBRs(_m*gammaMax, _BRW, (1-_BRW)/2.)
            cw = c.getc_Vals()[0]
            k = c.getKappa()
            gm_border.SetPoint(Nmasses + ii,masses[Nmasses-ii-1]*1.0,3.0)

        gm_border.SetLineColor(4)
        gm_border.SetLineWidth(2)
        gm_border.SetLineStyle(10)
        gm_border.SetFillColor(19)
        gm_border.SetFillStyle(1001)
        
        if self.drawExp:

            tg_types = ["exp", "exp_p2", "exp_p1", "exp_m1", "exp_m2"]
            if self.useData:
                tg_types += ["obs"]

            tg_list = {}
            tg_xsratio_list = {}
            for gtype in tg_types:
                if gtype=="exp":
                    tg_list[gtype] = []
                    tg_xsratio_list[gtype] = []
                    for i in range(self.nConfigs):
                        tg_list[gtype] += [ TGraph2D() ]
                        tg_list[gtype][i].SetName("tg_lim_{}_{}".format(gtype,i))

                        tg_xsratio_list[gtype] += [ TGraph2D() ]
                        tg_xsratio_list[gtype][i].SetName("tg_limratio_{}_{}".format(gtype,i))
                else:
                    tg_list[gtype] = TGraph2D()
                    tg_list[gtype].SetName("tg_lim_{}".format(gtype))

                    tg_xsratio_list[gtype] = TGraph2D()
                    tg_xsratio_list[gtype].SetName("tg_limratio_{}".format(gtype))

            ############# Fill graphs ############################
            iPoint = 0
            for Mass in self.massList:
                for Kappa in self.kappaList:
                    if(limitList[Kappa][Mass].theoryInfo.GM>0.5):
                        break

                    norm_xsec = 0.1
                    expInfoMap=limitList[Kappa][Mass].expInfo
                    theory_xsec=limitList[Kappa][Mass].theoryInfo.xsec

                    for n,cfg in enumerate(self.configList):
                        if not(cfg in expInfoMap):
                            continue
                        expLim = expInfoMap[cfg].expLim

                        for gtype in tg_types:
                            if gtype=="exp":
                                gr=tg_list[gtype][n]
                                gr_ratio=tg_xsratio_list[gtype][n]
                            else:
                                if n>0:
                                    continue
                                gr=tg_list[gtype]
                                gr_ratio=tg_xsratio_list[gtype]

                            xsecLim=expLim[gtype]*norm_xsec
                            gr.SetPoint(gr.GetN(),Mass,Kappa,xsecLim)
                            gr_ratio.SetPoint(gr_ratio.GetN(),Mass,Kappa,xsecLim/theory_xsec)

            ############# Graphs filled ############################

            ###### Make limit contours #############
            tg_cont_list = {}
            for gtype in tg_types: 
                #print('GETLIMITCONTOUR :',gtype)

                ##### COMPARE SMOOTHING #######
                
                #if gtype=="exp":
                #    DoSmoothingComparisons(tg_xsratio_list[gtype][n],0.5,1.5,doContours=True, smooth=1.0)
                #    DoSmoothingComparisons(tg_list[gtype][n],0.,0.2,doContours=False, smooth=1.0)
                #else:
                #    DoSmoothingComparisons(tg_xsratio_list[gtype],0.5,1.5,doContours=True)
                #    DoSmoothingComparisons(tg_list[gtype],0.,0.2,doContours=False)
                '''
                if gtype=="exp":
                    tg_cont_list[gtype] = [GetLimitContour(GetSmoothHist(tg_xsratio_list[gtype][n]),\
                                                           linecolor=gr_cols[n], linestyle=2)\
                                           for n in range(self.nConfigs)]
                else:
                    tg_cont_list[gtype] = GetLimitContour(GetSmoothHist(tg_xsratio_list[gtype]))
                '''
                if gtype=="exp":
                    tg_cont_list[gtype] = [GetLimitContour(tg_xsratio_list[gtype][n],\
                                                           linecolor=gr_cols[n], linestyle=2)\
                                           for n in range(self.nConfigs)]
                else:
                    tg_cont_list[gtype] = GetLimitContour(tg_xsratio_list[gtype])

            ####### Make 1sigma and 2sigma bands ####
            tg_fill_1sig = MakeErrorBand(tg_cont_list["exp_p1"],tg_cont_list["exp_m1"], fillcolor=kGreen)
            tg_fill_2sig = MakeErrorBand(tg_cont_list["exp_p2"],tg_cont_list["exp_m2"], 
                                         fillcolor=kYellow,setaxis=True)

        #############################################################
        ### DRAW PLOTS 
        #############################################################
        
        if self.drawTheory:
            ##### Draw Theory xsec plot #############################
            canv_name = "2DMKXSEC_THEORY_"+self.signal
            can = self.Setup2DCanvas(canv_name,"2DMKXSEC")
            can.cd()
            tg_theory_xsec.Draw("colz same")
            gm_border.Draw("f same")
            gm_contourset[1][-1].Draw()

            for tl in tl_list:
                tl.Draw()

            gPad.Update()
            gPad.RedrawAxis()
            can.SetTickx()
            can.SetTicky()
            printName = self.outputDir + "/" + canv_name.upper()+outSuffix+".png"
            can.SaveAs(printName)


            ##### Draw Theory Gamma/M plot ##########################
            canv_name = "2DMKGAMMA_THEORY_"+self.signal
            can = self.Setup2DCanvas(canv_name,"2DMKGAMMA")
            can.cd()
            tg_theory_GammaM.Draw("colz same")

            gm_border.Draw("f same")

            for i in range(len(GMLevels)):
                gm_contourset[0][i].Draw("cont3 same")
                    
            for i in range(len(GMLevels)):
                gm_contourset[1][i].Draw()

            for tl in tl_list:
                tl.Draw()

            gPad.Update()
            gPad.RedrawAxis()
            can.SetTickx()
            can.SetTicky()
            printName = self.outputDir + "/" + canv_name.upper()+outSuffix+".png"
            can.SaveAs(printName)

        if self.drawExp:
            ##### Draw MK contour plots #############################
            '''
            Draw curves in the order:
            - Error bands
            - Expected limit contour
            - Observed limit contour
            - Gamma/M contours
            '''
            canv_name = "2DMKContour_"+self.signal
            can = self.Setup2DCanvas(canv_name,"2DMKCONTOUR")
            can.cd()

            leg = TLegend(0.52,0.64,0.75,0.795)
            self.SetLegendStyle(leg,0.028)

            tg_fill_2sig.Draw("f same")
            tg_fill_1sig.Draw("f same")

            for n,tg in enumerate(tg_cont_list["exp"]):
                tg.Draw("c same")
                leg.AddEntry(tg,"95% CL Exp. "+_labels[n],"l")

            if self.useData:
                tg_xsratio_list["obs"].GetHistogram().GetZaxis().SetRangeUser(0.5,1.5)
                tg_cont_list["obs"].Draw("cont3 same")
                leg.AddEntry(tg_cont_list["obs"] ,"95% CL Obs.","l")

            leg.AddEntry(tg_fill_2sig,"Exp. #pm2#sigma","f")
            leg.AddEntry(tg_fill_1sig,"Exp. #pm1#sigma","f")

            gm_border.Draw("f same")
            for i in range(len(GMLevels)):
                gm_contourset[0][i].Draw("cont3 same")
            for i in range(len(GMLevels)):
                gm_contourset[1][i].Draw()

            leg.Draw()

            for tl in tl_list:
                tl.Draw()

            gPad.Update()
            gPad.RedrawAxis()
            can.SetTickx()
            can.SetTicky()
            printName = self.outputDir + "/" + canv_name.upper()+outSuffix+".png"
            can.SaveAs(printName)


            ##### Draw MK xsec lim plots #############################
            '''
            Draw curves in the order:
            - xsec limit plot
            - Limit contour
            - xsec limit contours (?)
            '''
            for n,cfg in enumerate(self.configList):
                typeList = ["exp", "obs"] if (n==0 and self.useData) else ["exp"] 

                for limtype in typeList:

                    if limtype=="exp":
                        tg_xsec=tg_list[limtype][n]
                        tg_xsratio=tg_xsratio_list[limtype][n]
                        tg_cont=tg_cont_list[limtype][n]
                    else: 
                        tg_xsec=tg_list[limtype]
                        tg_xsratio=tg_xsratio_list[limtype]
                        tg_cont=tg_cont_list[limtype]

                    ### Get xsec contour lines
                    contour_xs_levels = [0.01,0.02,0.04,0.08,0.1]
                    xsec_conts = GetLimitContourList(tg_xsec,contour_xs_levels,linecolor=kViolet-6)

                    contour_ratio_levels = [0.1,0.5,1.0,1.5]
                    xsratio_conts = GetLimitContourList(tg_xsratio,contour_ratio_levels,linecolor=kViolet-6)

                    leg = TLegend(0.52,0.64,0.75,0.795)
                    self.SetLegendStyle(leg,0.028)
                    leglabel = "95% CL Exp. " if limtype=="exp" else "95% CL Obs. "
                    leglabel +=_labels[n]
                    leg.AddEntry(tg_cont,leglabel,"l")

                    #### XS LIMIT #######
                    canv_xs_name = "2DMKXsecLim_"+self.signal+"_"+cfg+"_"+limtype
                    can_xs = self.Setup2DCanvas(canv_xs_name,"2DMKXSEC")
                    can_xs.cd()

                    tg_xsec.Draw("colz same")
                    tg_cont.Draw("c same")
                    #for cont in xsec_conts:
                    #    cont.Draw("c same")

                    gm_border.Draw("f same")
                    gm_contourset[1][-1].Draw()

                    leg.Draw()
                    for tl in tl_list:
                        tl.Draw()

                    gPad.Update()
                    gPad.RedrawAxis()
                    can_xs.SetTickx()
                    can_xs.SetTicky()
                    printName = self.outputDir + "/" + canv_xs_name.upper()+outSuffix+".png"
                    can_xs.SaveAs(printName)

                    #### XSRATIO LIMIT #######
                    canv_xsratio_name = "2DMKXSRATIOLim_"+self.signal+"_"+cfg+"_"+limtype
                    can_xsratio = self.Setup2DCanvas(canv_xsratio_name,"2DMKXSRATIO")
                    can_xsratio.cd()

                    tg_xsratio.Draw("colz same")
                    tg_cont.Draw("c same")
                    #for cont in xsratio_conts:
                    #    cont.Draw("c same")

                    gm_border.Draw("f same")
                    gm_contourset[1][-1].Draw()

                    leg.Draw()
                    for tl in tl_list:
                        tl.Draw()

                    gPad.Update()
                    gPad.RedrawAxis()
                    can_xsratio.SetTickx()
                    can_xsratio.SetTicky()
                    printName = self.outputDir + "/" + canv_xsratio_name.upper()+outSuffix+".png"
                    can_xsratio.SaveAs(printName)


        return

