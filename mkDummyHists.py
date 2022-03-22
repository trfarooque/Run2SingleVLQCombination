import ROOT
import os

def DummyHistMaker(List_of_Real_Files, List_of_Dummy_Files): 
    ## List_of_Real_Files: A list of files with full path on the machine that needs to be copied. It should be a file containing histograms only
    ## List_of_Dummy_Files: A list of files with full path on the machine with the same hists as in the real files
    for ii, _f in enumerate(List_of_Files):
        if ii == 0:
            fbase = ROOT.TFile(_f)
            List_of_Hists = fbase.GetListOfKeys()
        fnew = ROOT.TFile(List_of_Dummy_Files[ii], "RECREATE")
        for ll in List_of_Hists:
            hname = ll.GetName()
            hist_new = fbase.Get(hname)
            for ii in range(hist_new.GetNbinsX()):
                hist_new.SetBinContent(ii, 1e-5)
                hist_new.SetBinError(ii, 1e-5)
            hist_new.SetBinContent(hist_new.GetNbinsX(), 1e-5)
            hist_new.SetBinError(hist_new.GetNbinsX(), 1e-5)
            hist_new.SetBinContent(hist_new.GetNbinsX()+1, 1e-5)
            hist_new.SetBinError(hist_new.GetNbinsX()+1, 1e-5)
            fnew.cd()
            hist_new.Write()
        print("New Dummy File {} created".format(_f))

