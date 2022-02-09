#include <iostream>
#include <string>
#include <vector>
#include <map>

#include "TFile.h"
#include "TCanvas.h"
#include "TH1F.h"
#include "TGraphAsymmErrors.h"
#include "TGraphErrors.h"
#include "TStyle.h"
#include "TLegend.h"
#include "TLine.h"

#include "AtlasLabels.h"
#include "AtlasStyle.h"
#include "AtlasUtils.h"
#include "AtlasLabels.C"
#include "AtlasStyle.C"
#include "AtlasUtils.C"

int compare_limits( const std::map < std::string, std::string > &components, const std::string &combination, bool showObs = false, const std::string &outDir = "outComp/", const std::string &signal_legend = "" ){
  float xmax = 2;
  SetAtlasStyle();
  gStyle->SetEndErrorSize(0.);

  // Titles
  vector<string> files;
  vector<string> titles;
  for( const auto &limit : components ){
    std::cout << "Adding limit: " << limit.first << std::endl;
    files.push_back( limit.second );
    titles.push_back( limit.first );
  }
  int N = files.size();
  if(combination!=""){
    files.push_back( combination );
    titles.push_back( "Combination" );
    N++;
  }

  float ymin = -0.5;
  float ymax = N-0.5;

  TCanvas *c = new TCanvas("c","c",700,500);

  TGraphErrors *g_obs = new TGraphErrors(N);
  TGraphErrors *g_exp = new TGraphErrors(N);
  TGraphAsymmErrors *g_1s = new TGraphAsymmErrors(N);
  TGraphAsymmErrors *g_2s = new TGraphAsymmErrors(N);

  int Ndiv = N+1;

  // get values
  int i = 0;
  for( const auto &limit : files ){
    TFile *f = TFile::Open( limit.c_str(), "READ");
    std::cout << "Reading file " << limit << std::endl;
    TH1F* h = (TH1F*)f->Get("limit");

    if(showObs) g_obs->SetPoint(N-i-1,h->GetBinContent(1),N-i-1);
    else g_obs->SetPoint(N-i-1,-1,N-i-1);
    g_exp->SetPoint(N-i-1,h->GetBinContent(2),N-i-1);
    g_1s->SetPoint(N-i-1,h->GetBinContent(2),N-i-1);
    g_2s->SetPoint(N-i-1,h->GetBinContent(2),N-i-1);
    g_obs->SetPointError(N-i-1,0,0.5);
    g_exp->SetPointError(N-i-1,0,0.5);
    g_1s->SetPointError(N-i-1,h->GetBinContent(2)-h->GetBinContent(5),h->GetBinContent(4)-h->GetBinContent(2),0.5,0.5);
    g_2s->SetPointError(N-i-1,h->GetBinContent(2)-h->GetBinContent(6),h->GetBinContent(3)-h->GetBinContent(2),0.5,0.5);

    if(h->GetBinContent(1)>xmax) xmax = h->GetBinContent(1);
    if(h->GetBinContent(2)>xmax) xmax = h->GetBinContent(2);
    if(h->GetBinContent(3)>xmax) xmax = h->GetBinContent(3);
    if(h->GetBinContent(4)>xmax) xmax = h->GetBinContent(4);
    if(h->GetBinContent(5)>xmax) xmax = h->GetBinContent(5);
    if(h->GetBinContent(6)>xmax) xmax = h->GetBinContent(6);
    i++;
  }

  g_obs->SetLineWidth(3);
  g_exp->SetLineWidth(3);
  g_exp->SetLineStyle(2);
  g_1s->SetFillColor(kGreen);
  g_1s->SetLineWidth(3);
  g_1s->SetLineStyle(2);
  g_2s->SetFillColor(kYellow);
  g_2s->SetLineWidth(3);
  g_2s->SetLineStyle(2);

  g_2s->SetMarkerSize(0);
  g_1s->SetMarkerSize(0);
  g_exp->SetMarkerSize(0);
  g_obs->SetMarkerSize(0);

  TH1F* h_dummy = new TH1F("h_dummy","h_dummy",1,0,xmax*1.2);
  h_dummy->Draw();
  h_dummy->SetMinimum(ymin);
  h_dummy->SetMaximum(ymax);
  h_dummy->SetLineColor(kWhite);
  h_dummy->GetYaxis()->Set(N,ymin,ymax);
  h_dummy->GetYaxis()->SetNdivisions(Ndiv);
  for(int i=0;i<N;i++){
    h_dummy->GetYaxis()->SetBinLabel(N-i,titles[i].c_str());
  }
  h_dummy->GetXaxis()->SetTitle("95% CL upper limit on signal strength");

  g_2s->Draw("E2 same");
  g_1s->Draw("E2 same");
  g_exp->Draw("E same");
  if(showObs) g_obs->Draw("E same");

  TLine *l_SM = new TLine(1,-0.5,1,N-0.5);
  l_SM->SetLineWidth(1);
  l_SM->SetLineColor(kRed);
  l_SM->SetLineStyle(2);
  l_SM->Draw("same");
  c->RedrawAxis();

  if(combination!=""){
    TLine *l_comb = new TLine(0,0.5,xmax*1.2,0.5);
    l_comb->SetLineWidth(2);
    l_comb->SetLineColor(kBlack);
    l_comb->SetLineStyle(1);
    l_comb->Draw("same");
    c->RedrawAxis();
  }

  ATLASLabel(0.63,0.86,"Internal",kBlack);
  myText(0.63,0.79,kBlack,"#font[42]{#sqrt{s} = 13 TeV, 36.1 fb^{-1}}");
  if(signal_legend!=""){
    myText(0.63,0.72,kBlack,("#font[52]{#scale[0.8]{"+signal_legend+"}}").c_str());
  }

  TLegend *leg;
  if(showObs) leg = new TLegend(0.65,0.2,0.95,0.40);
  else        leg = new TLegend(0.65,0.2,0.95,0.35);
  leg->SetTextSize(gStyle->GetTextSize());
  leg->SetTextFont(gStyle->GetTextFont());
  leg->SetFillStyle(0);
  leg->SetBorderSize(0);
  leg->AddEntry(g_1s,"Expected #pm 1#sigma","lf");
  leg->AddEntry(g_2s,"Expected #pm 2#sigma","lf");
  if(showObs) leg->AddEntry(g_obs,"Observed","l");
  leg->Draw();

  //
  // Applying ATLAS style
  //
  SetAtlasStyle();
  c->SetTicky(0);
  for(const std::string &format : {".png",".pdf"}){
    c->SaveAs( (outDir+"/Limits"+format).c_str() );
  }
  delete c;
  return 1.;
}
