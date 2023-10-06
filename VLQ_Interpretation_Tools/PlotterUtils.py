import ROOT
import numpy as np

def ATLAS_LABEL(x,y,color):
    l=ROOT.TLatex()
    l.SetNDC()
    l.SetTextFont(72)
    l.SetTextColor(color)
    l.DrawLatex(x,y,"ATLAS")

def myText(x,y,color,text,size):
    l=ROOT.TLatex()
    l.SetNDC()
    l.SetTextSize(size)
    l.SetTextColor(color)
    l.DrawLatex(x,y,text)

def Draw_ATLAS(x, y, mode):
    ATLAS_LABEL(x,y,1)
    myText(x+0.14,y,1,mode,0.05)
    myText(x,y-0.05,1,"#sqrt{s} = 13 TeV, 139 fb^{-1}",0.035)

def oneDLimitPlotter(_x, _yup2, _yup1, _ydown1, _ydown2, _ymed, _yobs, _ytheory, do_log, k = 1.0, ytype = "xs", plotname="limits_1D.png", _y2l=None, _y3l=None):
    do_n = len(_x)
    _min = min(_ydown2)
    _max = max(_yup2)

    if do_log:
        _min = _min/100.
        _max = _max*1000.
    else:
        _min = 0.
        _max = 2.0
    
    x = np.asarray(_x)
    yup2 = np.asarray(_yup2)
    yup1 = np.asarray(_yup1)
    ydown1 = np.asarray(_ydown1)
    ydown2 = np.asarray(_ydown2)
    yobs = np.asarray(_yobs)
    ymed = np.asarray(_ymed)
    ytheory = np.asarray(_ytheory)

    print(x)
    print(ymed)

    grmedian = ROOT.TGraph(do_n,x,ymed)
    for ii in range(do_n): print(grmedian.GetX()[ii], grmedian.GetY()[ii])
    grobs = ROOT.TGraph(do_n,x,yobs)
    
    if ytype == "xs": grtheory = ROOT.TGraph(do_n,x,ytheory)
    grshade1 = ROOT.TGraph(2*do_n)
    grshade2 = ROOT.TGraph(2*do_n)
    grshade3 = ROOT.TGraph(2*do_n)
    leg = ROOT.TLegend(0.52,0.65,0.70,0.85)
    leg.SetFillColor(0)
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.SetTextFont(42)
    leg.SetTextSize(0.027)

    for i in range(do_n):
        grshade1.SetPoint(i,x[i],ydown2[i])
        grshade1.SetPoint(do_n+i,x[do_n-i-1],ydown1[do_n-i-1])
        grshade2.SetPoint(i,x[i],ydown1[i])
        grshade2.SetPoint(do_n+i,x[do_n-i-1],yup1[do_n-i-1])
        grshade3.SetPoint(i,x[i],yup1[i])
        grshade3.SetPoint(do_n+i,x[do_n-i-1],yup2[do_n-i-1])
    
    leg.AddEntry(grshade1,"95% CL Exp. #pm 2#sigma","f")
    leg.AddEntry(grshade2,"95% CL Exp. #pm 1#sigma","f")
    leg.AddEntry(grmedian,"95% CL Exp. Limit","l")
    if ytype == "xs": leg.AddEntry(grtheory,"Theory Prediction (#kappa = " + str(k) +  ")")
    #leg.AddEntry(grobs,"Observed Limit","lp")
    leg.AddEntry(0, "BR(T #rightarrow Zt) = 0.25", "")

    grmedian.SetLineColor(1)
    grmedian.SetLineWidth(4)
    grmedian.SetLineStyle(2)
    grobs.SetLineColor(1)
    grobs.SetLineWidth(2)
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
    
    c_1DLimit = ROOT.TCanvas("c_1DLimit","c_1DLimit",1000,800)
    c_1DLimit.cd()
    if ytype == "xs": ROOT.gPad.DrawFrame(x[0],_min,x[do_n-1],_max," ;m_{T}[GeV];#sigma(pp #rightarrow T #rightarrow Zt) [pb]")
    if ytype == "coupling": ROOT.gPad.DrawFrame(x[0],_min,x[do_n-1],_max," ;m_{T}[GeV];#sqrt{c_{W,L}^{2} + c_{W,R}^{2}}")
    ROOT.gPad.SetLogy(do_log)
    grshade1.Draw("f")
    grshade2.Draw("f same")
    grshade3.Draw("f same")
    grmedian.Draw("same")
    if ytype == "xs": grtheory.Draw("same")
    #grobs.Draw("l same")
    
    if _y2l is not None: 
        y2l = np.asarray(_y2l)
        gr2l = ROOT.TGraph(do_n,x,y2l)
        gr2l.SetLineColor(2)
        gr2l.SetLineWidth(3)
        gr2l.SetLineStyle(4)
        leg.AddEntry(gr2l, "SP2l", "l")
        gr2l.Draw("same")
    if _y3l is not None: 
        y3l = np.asarray(_y3l)
        gr3l = ROOT.TGraph(do_n,x,y3l)
        gr3l.SetLineColor(4)
        gr3l.SetLineWidth(3)
        gr3l.SetLineStyle(4)
        leg.AddEntry(gr3l, "SP3l", "l")
        gr3l.Draw("same")

    leg.Draw("same")
    Draw_ATLAS(0.14,0.85,"Internal");
    ROOT.gPad.RedrawAxis()
    c_1DLimit.SaveAs(plotname)

    #return c_1DLimit
    
