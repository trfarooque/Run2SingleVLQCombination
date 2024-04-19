import ROOT
import numpy as np
from VLQCouplingCalculator import VLQCouplingCalculator as vlq

def myText(x,y,color,text,size):
    l=ROOT.TLatex()
    l.SetNDC()
    l.SetTextFont(42)
    l.SetTextSize(size)
    l.SetTextColor(color)
    l.DrawLatex(x,y,text)

def ATLAS_LABEL(x,y,color):
    l=ROOT.TLatex()
    l.SetNDC()
    l.SetTextFont(72)
    l.SetTextColor(color)
    l.DrawLatex(x,y,"ATLAS Internal")

def Draw_ATLAS(x, y, mode):
    ATLAS_LABEL(x,y,1)
    myText(x+0.14,y,1,mode,0.05)
    myText(x,y-0.05,1,"#sqrt{s} = 13 TeV, 139 fb^{-1}",0.035)



def oneDLimitCouplingPlotter(yup2, yup1, ydown1, ydown2, ymed, yobs, do_log, brw = 0.5, plotname="limits_1D.png"):# _y2l=None, _y3l=None):
    ROOT.gROOT.SetBatch(1)
    gammaMax = 0.5
    _min = min(list(ydown2.values()))
    _max = max(list(yup2.values()))

    if do_log:
        _min = _min/10.
        _max = _max*10.
    else:
        _min = 0.1 if brw == 0.5 else 0.3
        _max = 1.0
    
    # x = np.asarray(_x)
    # yup2 = np.asarray(_yup2)
    # yup1 = np.asarray(_yup1)
    # ydown1 = np.asarray(_ydown1)
    # ydown2 = np.asarray(_ydown2)
    # yobs = np.asarray(_yobs)
    # ymed = np.asarray(_ymed)
    # ytheory = np.asarray(_ytheory)

    # print x
    # print ymed
    
    do_n = len(ymed.keys())
    grmedian = ROOT.TGraph(do_n)
    for ii,x in enumerate(sorted(ymed.keys())): 
        # print x, ymed[x]
        grmedian.SetPoint(ii, x, ymed[x])

    do_n = len(yobs.keys())
    grobs = ROOT.TGraph(do_n)
    for ii,x in enumerate(sorted(yobs.keys())): 
        # print x, yobs[x]
        grobs.SetPoint(ii, x, yobs[x])

    
    #if ytype == "xs": grtheory = ROOT.TGraph(do_n,x,ytheory)
    #grshade1 = ROOT.TGraph(2*do_n)
    #grshade2 = ROOT.TGraph(2*do_n)
    #grshade3 = ROOT.TGraph(2*do_n)
    leg = ROOT.TLegend(0.60,0.63,0.80,0.83)
    leg.SetFillColor(0)
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.SetTextFont(42)
    leg.SetTextSize(0.035)
    
    do_n = len(yup2.keys())
    grshade1 = ROOT.TGraph(2*do_n)
    #grshade2 = ROOT.TGraph(2*do_n)
    grshade3 = ROOT.TGraph(2*do_n)

    for i,x in enumerate(sorted(yup2.keys())):
        grshade1.SetPoint(i,x,ydown2[x])
        grshade1.SetPoint(do_n+i,sorted(yup2.keys())[do_n-i-1],ydown1[sorted(yup2.keys())[do_n-i-1]])
        #grshade2.SetPoint(i,x[i],ydown1[i])
        #grshade2.SetPoint(do_n+i,x[do_n-i-1],yup1[do_n-i-1])
        grshade3.SetPoint(i,x,yup1[x])
        grshade3.SetPoint(do_n+i,sorted(yup2.keys())[do_n-i-1],yup2[sorted(yup2.keys())[do_n-i-1]])
    
    do_n = len(yup1.keys())
    grshade2 = ROOT.TGraph(2*do_n)
    for i,x in enumerate(sorted(yup1.keys())):
        #grshade1.SetPoint(i,x[i],ydown2[i])
        #grshade1.SetPoint(do_n+i,x[do_n-i-1],ydown1[do_n-i-1])
        grshade2.SetPoint(i,x,ydown1[x])
        grshade2.SetPoint(do_n+i,sorted(yup1.keys())[do_n-i-1],yup1[sorted(yup1.keys())[do_n-i-1]])
        #grshade3.SetPoint(i,x[i],yup1[i])
        #grshade3.SetPoint(do_n+i,x[do_n-i-1],yup2[do_n-i-1])

    leg.AddEntry(grobs,"95% CL Obs. Limit","l")
    leg.AddEntry(grmedian,"95% CL Exp. Limit","l")
    leg.AddEntry(grshade2,"Exp. Limit #pm 1#sigma","f")
    leg.AddEntry(grshade1,"Exp. Limit #pm 2#sigma","f")
    leg.AddEntry(0, " ", "")
    #leg.AddEntry(0, "T-{}".format('singlet' if brw == 0.5 else 'doublet'), "")
    #leg.AddEntry(0, "BR(T #rightarrow Zt/Ht) = {0:.2f}".format((1-brw)/2.), "")
    leg.AddEntry(0, "BRW = {0:.2f}".format(brw), "")

    grmedian.SetLineColor(1)
    grmedian.SetLineWidth(4)
    grmedian.SetLineStyle(2)
    grobs.SetLineColor(1)
    grobs.SetLineWidth(3)
    grobs.SetLineStyle(1)
    grshade1.SetLineColor(5)
    grshade1.SetFillColor(5)
    grshade1.SetFillStyle(1001)
    grshade3.SetLineColor(5)
    grshade3.SetFillColor(5)
    grshade3.SetFillStyle(1001)
    grshade2.SetLineColor(3)
    grshade2.SetFillColor(3)
    grshade2.SetFillStyle(1001)

    c = vlq()
    masses = list(range(1000,2700,10))
    grmax = ROOT.TGraph(2*len(masses))
    Nmasses = len(masses)
    for ii in range(Nmasses):
        _m = masses[ii]*1.0
        c.setMVLQ(_m)
        c.setGammaBRs(_m*gammaMax, brw, (1-brw)/2.)
        cw = c.getc_Vals()[0]
        k = c.getKappa()
        grmax.SetPoint(ii,_m,k-0.001)
        _m = masses[Nmasses-ii-1]*1.0
        c.setMVLQ(_m)
        c.setGammaBRs(_m*gammaMax, brw, (1-brw)/2.)
        cw = c.getc_Vals()[0]
        k = c.getKappa()
        grmax.SetPoint(Nmasses + ii,masses[Nmasses-ii-1]*1.0,3.0)
    
    grmax.SetLineColor(4)
    grmax.SetLineWidth(2)
    grmax.SetLineStyle(10)
    grmax.SetFillColor(19)
    grmax.SetFillStyle(1001)
    #grmax.SetLineWidth(9999)


    ## Drawing Iso-Gamma lines

    gr10 = ROOT.TGraph(len(masses))
    gr30 = ROOT.TGraph(len(masses))
    gr50 = ROOT.TGraph(len(masses))
    Nmasses = len(masses)
    for ii in range(Nmasses):
        _m = masses[ii]*1.0
        c.setMVLQ(_m)
        c.setGammaBRs(_m*0.15, brw, (1-brw)/2.)
        cw = c.getc_Vals()[0]
        k = c.getKappa()
        gr10.SetPoint(ii,_m,k-0.001)
        c.setGammaBRs(_m*0.25, brw, (1-brw)/2.)
        cw = c.getc_Vals()[0]
        k = c.getKappa()
        gr30.SetPoint(ii,_m,k-0.001)
        c.setGammaBRs(_m*0.5, brw, (1-brw)/2.)
        cw = c.getc_Vals()[0]
        k = c.getKappa()
        gr50.SetPoint(ii,_m,k-0.001)
    
    gr10.SetLineColor(4)
    gr10.SetLineStyle(4)
    gr10.SetLineWidth(4)

    gr30.SetLineColor(4)
    gr30.SetLineStyle(4)
    gr30.SetLineWidth(4)

    gr50.SetLineColor(4)
    gr50.SetLineStyle(4)
    gr50.SetLineWidth(4)        
    
    c_1DLimit = ROOT.TCanvas("c_1DLimit","c_1DLimit",1000,800)
    c_1DLimit.cd()
    c_1DLimit.SetLeftMargin(0.13)
    c_1DLimit.SetBottomMargin(0.13)
    c_1DLimit.SetTopMargin(0.15)
    #ROOT.gPad.DrawFrame(min(masses),_min,max(masses),_max," ;M_{T}[GeV];#sqrt{c_{W,L}^{2} + c_{W,R}^{2}}")
    #frame = ROOT.gPad.DrawFrame(min(masses),_min,max(masses),1.0," ;M_{T}[GeV];#kappa")
    if brw == 0.5:
        mmax = 2400.
    else:
        mmax = 2400.
    frame = ROOT.gPad.DrawFrame(min(masses),_min,mmax,1.0," ;M_{T} [GeV]; #kappa  ")
    ROOT.gPad.SetLogy(do_log)
    ROOT.gStyle.SetPadTickY(1)
    frame.GetXaxis().SetTitleSize(0.042)
    frame.GetXaxis().SetTitleOffset(1.3)
    frame.GetXaxis().SetLabelOffset(0.01)
    frame.GetXaxis().SetLabelSize(0.04)
    frame.GetYaxis().SetTitleSize(0.05)
    frame.GetYaxis().SetTitleOffset(1.1)
    frame.GetYaxis().SetLabelSize(0.04)

    grshade1.Draw("f")
    grshade2.Draw("f same")
    grshade3.Draw("f same")
    grmedian.Draw("same")
    grobs.Draw("l same")
    grmax.Draw("f same")

    gr10.Draw("l same")
    gr30.Draw("l same")
    gr50.Draw("l same")


    mlabel = 2200. if brw == 0.5 else 1700.
    locs = []
    for gm in [0.15, 0.25, 0.5]:
        c.setMVLQ(mlabel)
        c.setGammaBRs(mlabel*gm, brw, (1-brw)/2.)
        cw = c.getc_Vals()[0]
        k = c.getKappa()
        locs.append(k)

    tl = ROOT.TLatex()
    tl.SetTextColor(4)
    tl.SetTextSize(0.035)

    if brw == 0.5:
        tl.DrawLatex(mlabel-20, locs[0] - 0.065, "#frac{#Gamma_{T}}{M_{T}} = 0.15")
        tl.DrawLatex(mlabel-20, locs[1] - 0.065, "#frac{#Gamma_{T}}{M_{T}} = 0.25")
        tl.DrawLatex(mlabel-20, locs[2] + 0.035, "#frac{#Gamma_{T}}{M_{T}} = 0.5")
    else:
        tl.DrawLatex(mlabel-20, locs[0] + 0.03, "#frac{#Gamma_{T}}{M_{T}} = 0.15")
        tl.DrawLatex(mlabel-20, locs[1] - 0.005, "#frac{#Gamma_{T}}{M_{T}} = 0.25")
        tl.DrawLatex(mlabel-20, locs[2] - 0.065, "#frac{#Gamma_{T}}{M_{T}} = 0.5")
        

    

    box = ROOT.TBox(min(masses)-1,_min,mmax+1,_max+0.002)
    box.SetLineColor(1)
    box.SetLineWidth(3)
    box.SetFillColor(0)
    box.SetFillStyle(0)
    box.Draw("same")
    
    # if _y2l is not None: 
    #     y2l = np.asarray(_y2l)
    #     gr2l = ROOT.TGraph(do_n,x,y2l)
    #     gr2l.SetLineColor(2)
    #     gr2l.SetLineWidth(3)
    #     gr2l.SetLineStyle(4)
    #     leg.AddEntry(gr2l, "SP2l", "l")
    #     gr2l.Draw("same")
    # if _y3l is not None: 
    #     y3l = np.asarray(_y3l)
    #     gr3l = ROOT.TGraph(do_n,x,y3l)
    #     gr3l.SetLineColor(4)
    #     gr3l.SetLineWidth(3)
    #     gr3l.SetLineStyle(4)
    #     leg.AddEntry(gr3l, "SP3l", "l")
    #     gr3l.Draw("same")

    leg.Draw("same")
    Draw_ATLAS(0.12,0.93," ")

    ROOT.gStyle.SetPadTickY(1)
    ROOT.gStyle.SetPadTickX(1)
    ROOT.gPad.Update()
    ROOT.gPad.RedrawAxis()
    #ROOT.gPad.RedrawAxis("G F")
    ROOT.gPad.RedrawAxis("F")
    ROOT.gPad.Update()
    c_1DLimit.SaveAs(plotname)
    #c_1DLimit.SaveAs(plotname.replace(".png",".pdf"))
    del c_1DLimit



def oneDLimitPlotter(_x, _yup2, _yup1, _ydown1, _ydown2, _ymed, _yobs, _ytheory, do_log = False, k = 1.0, brw = 0.5, ytype = "xs", 
                     plotname="limits_1D.png", signal_benchmark = 'singlet'):
    ROOT.gROOT.SetBatch(1)
    ROOT.gStyle.SetPadTickY(1)
    ROOT.gStyle.SetPadTickX(1)
    do_n = len(_x)
    if ytype == 'xs':
        _min = min(min(_ydown2), min(_ytheory))
        _max = max(max(_yup2), max(_ytheory))
    else:
        _min = min(_ydown2)
        _max = max(_yup2)

    if do_log:
        _min = 1.e-4
        _max = 3
    else:
        _min = 0.
        _max = 1.5
    
    x = np.asarray(_x)*1.0
    yup2 = np.asarray(_yup2)
    yup1 = np.asarray(_yup1)
    ydown1 = np.asarray(_ydown1)
    ydown2 = np.asarray(_ydown2)
    yobs = np.asarray(_yobs)
    ymed = np.array(_ymed)
    ytheory = np.asarray(_ytheory)

    #if _ytheoryUnc is not None:
    #    ytheoryunc = np.asarray(_ytheoryUnc)
    #else:
    ytheoryunc = np.asarray([0.]*do_n)

    m_max = x[-1]
    for m in np.arange(x[0], x[-1], 5.):
        c = vlq(m)
        c.setKappaxi(k, brw, (1.-brw)/2.)
        gm = c.getGamma()/m
        if gm > 0.5:
            m_max = m
            break

    #print(x)
    #print(ymed)

    grmedian = ROOT.TGraph(do_n, x, ymed)
        
    #for ii in range(do_n): print(grmedian.GetX()[ii], grmedian.GetY()[ii])
    grobs = ROOT.TGraph(do_n,x,yobs)
    
    # grtheory = ROOT.TGraphErrors(n=do_n,x=x,y=ytheory,ey=ytheoryunc)
    grtheory = ROOT.TGraphErrors(do_n)
    for ii in range(do_n):
        grtheory.SetPoint(ii, x[ii], ytheory[ii])
        grtheory.SetPointError(ii, 0.0, ytheoryunc[ii])
        #print(x[ii], ytheory[ii], ytheoryunc[ii])
    grshade1 = ROOT.TGraph(2*do_n)
    grshade2 = ROOT.TGraph(2*do_n)
    grshade3 = ROOT.TGraph(2*do_n)
    leg = ROOT.TLegend(0.58,0.61,0.80,0.88)
    leg.SetFillColor(0)
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.SetTextFont(42)
    leg.SetTextSize(0.035)

    for i in range(do_n):
        grshade1.SetPoint(i,x[i],ydown2[i])
        grshade1.SetPoint(do_n+i,x[do_n-i-1],ydown1[do_n-i-1])
        grshade2.SetPoint(i,x[i],ydown1[i])
        grshade2.SetPoint(do_n+i,x[do_n-i-1],yup1[do_n-i-1])
        grshade3.SetPoint(i,x[i],yup1[i])
        grshade3.SetPoint(do_n+i,x[do_n-i-1],yup2[do_n-i-1])


    if ytype == "xs":
        leg.AddEntry(grtheory,"Theory (NLO)")
        # leg.AddEntry(grtheory,"Theory Prediction (#kappa = " + str(k) +  ")")
    
    leg.AddEntry(grobs,"95% CL Obs. Limit","l")
    leg.AddEntry(grmedian,"95% CL Exp. Limit","l")
    leg.AddEntry(grshade2,"Exp. Limit #pm 1#sigma","f")
    leg.AddEntry(grshade1,"Exp. Limit #pm 2#sigma","f")
    leg.AddEntry(0, "", "")

   

    grmedian.SetLineColor(1)
    grmedian.SetLineWidth(4)
    grmedian.SetLineStyle(2)
    grobs.SetLineColor(1)
    grobs.SetLineWidth(3)
    grobs.SetLineStyle(1)
    grshade1.SetLineColor(5)
    grshade1.SetFillColor(5)
    grshade1.SetFillStyle(1001)
    grshade3.SetLineColor(5)
    grshade3.SetFillColor(5)
    grshade3.SetFillStyle(1001)
    grshade2.SetLineColor(3)
    grshade2.SetFillColor(3)
    grshade2.SetFillStyle(1001)
    if ytype == "xs":
        grtheory.SetLineColor(2)
        grtheory.SetLineWidth(2)
        grtheory.SetLineStyle(1)
        grtheory.SetFillColor(2)
        grtheory.SetFillStyle(3002)
    
    c_1DLimit = ROOT.TCanvas("c_1DLimit","c_1DLimit",1000,800)
    c_1DLimit.cd()
    c_1DLimit.SetLeftMargin(0.13)
    c_1DLimit.SetBottomMargin(0.13)
    # if ytype == "xs" and signal_benchmark != 'doublet': frame = ROOT.gPad.DrawFrame(x[0],_min,x[do_n-1],_max," ;M_{T}[GeV];#sigma(WTZt + ZTZt) [pb]")
    # if ytype == "xs" and signal_benchmark == 'doublet': frame = ROOT.gPad.DrawFrame(x[0],_min,x[do_n-1],_max," ;M_{T}[GeV];#sigma(ZTZt) [pb]")
    if ytype == "xs" and signal_benchmark != 'doublet': frame = ROOT.gPad.DrawFrame(x[0],_min,m_max,_max," ;M_{T} [GeV];#sigma(WTZt + ZTZt) [pb]")
    if ytype == "xs" and signal_benchmark == 'doublet': frame = ROOT.gPad.DrawFrame(x[0],_min,m_max,_max," ;M_{T} [GeV];#sigma(ZTZt) [pb]")
    if ytype == "coupling": ROOT.gPad.DrawFrame(x[0],_min,x[do_n-1],_max," ;M_{T} [GeV];#sqrt{c_{W,L}^{2} + c_{W,R}^{2}}")
    ROOT.gPad.SetLogy(do_log)
    #ROOT.gStyle.SetPadTickY(1)
    #ROOT.gStyle.SetPadTickX(1)
    frame.GetXaxis().SetTitleSize(0.042)
    frame.GetXaxis().SetTitleOffset(1.3)
    frame.GetXaxis().SetLabelSize(0.04)
    frame.GetYaxis().SetTitleSize(0.042)
    frame.GetYaxis().SetTitleOffset(1.3)
    frame.GetYaxis().SetLabelSize(0.04)
    grshade1.Draw("f")
    grshade2.Draw("f same")
    grshade3.Draw("f same")
    grmedian.Draw("same")
    grtheory.Draw("c3 Z same")
    grobs.Draw("l same")
    
    #sif _y2l is not None: 
    #    y2l = np.asarray(_y2l)
    #    gr2l = ROOT.TGraph(do_n,x,y2l)
    #    gr2l.SetLineColor(908) #kPink + 8
    #    gr2l.SetLineWidth(4)
    #    gr2l.SetLineStyle(2)
    #    leg.AddEntry(gr2l, "Exp. Limits from 2#font[12]{l}", "l")
    #    gr2l.Draw("same")
    #if _y3l is not None: 
    #    y3l = np.asarray(_y3l)
    #    gr3l = ROOT.TGraph(do_n,x,y3l)
    #    gr3l.SetLineColor(600)  #kBlue
    #    gr3l.SetLineWidth(4)
    #    gr3l.SetLineStyle(2)
    #    leg.AddEntry(gr3l, "Exp. Limits from 3#font[12]{l}", "l")
    #    gr3l.Draw("same")

    # if m_max != x[-1]:
    #     l = ROOT.TLine(m_max, ROOT.gPad.GetUymin(), m_max, 5.e-2)
    #     l.SetLineColor(13)
    #     l.SetLineStyle(4)
    #     l.SetLineWidth(2)
    #     l.Draw("Same")

    #     b = ROOT.TBox(m_max,
    #                   ROOT.gPad.GetUymin(),
    #                   ROOT.gPad.GetUxmax(),
    #                   ROOT.gPad.GetUymax())
    #     b.SetLineColor(0)
    #     b.SetFillColor(0)
    #     b.Draw("Same")

    #leg.AddEntry(0, "", "")
    #leg.AddEntry(0, "", "")

    leg.Draw("same")
        
    ktag = "#kappa = {}".format(k)
    
    stag = ROOT.TLatex()
    stag.SetTextFont(42)
    stag.SetTextSize(0.035)

    l = ROOT.TLatex()
    l.SetNDC()
    l.SetTextFont(42)
    l.SetTextSize(0.035)
    if signal_benchmark == 'singlet':
        l.DrawLatex(0.16, 0.3, "T-singlet ({})".format(ktag))
    elif signal_benchmark == 'doublet':
        l.DrawLatex(0.16, 0.3, "T-doublet ({})".format(ktag))
        # leg.AddEntry(0, "T-doublet ({})".format(ktag), "")


    Draw_ATLAS(0.16,0.22," ")

    bx = ROOT.TBox(ROOT.gPad.GetUxmin()*0.9998,
                   ROOT.gPad.GetUymin(),
                   ROOT.gPad.GetUxmax()*1.0002,
                   ROOT.gPad.GetUymax())
    bx.SetLineColor(1)
    bx.SetLineWidth(3)
    bx.SetFillStyle(0)
    bx.Draw("Same")

            
    ROOT.gPad.RedrawAxis()
    ROOT.gPad.RedrawAxis("G")
    
    c_1DLimit.SaveAs(plotname)