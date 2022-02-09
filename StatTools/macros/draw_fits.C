#include <iostream>
#include <string>
#include <vector>
#include <map>

#include "TFile.h"
#include "TCanvas.h"
#include "TH1F.h"
#include "TH2F.h"
#include "TGraphAsymmErrors.h"
#include "TGraphErrors.h"
#include "TStyle.h"
#include "TLegend.h"
#include "TLine.h"
#include "TDirectory.h"
#include "TClass.h"
#include "RooFitResult.h"
#include "RooRealVar.h"
#include "TBox.h"
#include "TString.h"

#include "AtlasLabels.h"
#include "AtlasStyle.h"
#include "AtlasUtils.h"
#include "AtlasLabels.C"
#include "AtlasStyle.C"
#include "AtlasUtils.C"

//______________________________________________________________________________
//
struct Ana {
  std::string file;
  std::string title;
};

//______________________________________________________________________________
//
struct NP {
  std::string name;
  double central;
  double errHi;
  double errLo;
};


// Analyses
vector< Ana > analyses;

//______________________________________________________________________________
//
int build_canvas( TCanvas &c, std::vector < TGraphAsymmErrors* > tgs,
                  const std::map < std::string, int > &map_syst ){

  //
  // Utility to build a pull plot once a vector of TGraphAsymErrors is provided.
  //
  const std::string name = (std::string)c.GetName();

  //
  // Detect which kind of canvas is needed
  //
  enum cType{
    PULL = 0,
    PULLREF = 1,
    ERRREF = 2
  };
  cType type = PULL;
  if(name.find("PullChange") != std::string::npos)  type = PULLREF;
  if(name.find("ErrChange") != std::string::npos)  type = ERRREF;

  //
  // Get the dimensions of the canvas
  //
  const double width = (c.GetWw());
  const double height = (c.GetWh());

  //
  // Dummy histogram
  //    Needed to define the labels and the ranges
  //
  double x_max = 3;
  double x_min = -3;
  if( type==PULLREF ){
    x_max = 3;
    x_min = -3;
  }
  else if ( type==ERRREF ){
    x_max = 60;
    x_min = 0.;    
  }
  TH2F* dummy = new TH2F( ("h2"+name).c_str(),"",12,x_min,x_max,map_syst.size(),0.001,map_syst.size());
  for( const auto &np : map_syst ){
    dummy->GetYaxis()->SetBinLabel( np.second+1, np.first.c_str() );
  }
  dummy->GetYaxis()->SetLabelSize( dummy->GetYaxis()->GetLabelSize() * 0.7 * ( 1.7 * ( (700.+height)/(2*height) ) ) );
  dummy->GetXaxis()->SetLabelSize( dummy->GetXaxis()->GetLabelSize() * 0.7 * ( 1.7 * ( (700.+height)/(2*height) ) ) );
  dummy->Draw();



  //
  // Standard pull plot
  //
  TString text_latex;

  if(type==PULL){
    //
    // Canvas style
    //    Defines the content of the canvas
    //
    TLine *l0 = new TLine(0,0,0,map_syst.size());
    l0 -> SetLineStyle(7);
    l0 -> SetLineColor(kBlack);
    TBox *b1 = new TBox(-1,0,1,map_syst.size());
    TBox *b2 = new TBox(-2,0,2,map_syst.size());
    b1 -> SetFillColor(kGreen);
    b2 -> SetFillColor(kYellow);
    b2 ->Draw("same");
    b1 -> Draw("same");
    l0 -> Draw("same");

    //
    // Looping over the TGraph vector to fill in the pull plot
    //
    for( const auto tg : tgs ){
      tg -> SetMarkerStyle(20);
      tg -> SetLineWidth(1);
      tg -> Draw("p");
    }
  }
  //
  // Drawing the relative difference of the pulls
  //
  if(type==PULLREF){
    TLine *l0 = new TLine(0,0,0,map_syst.size());
    l0 -> SetLineStyle(7);
    l0 -> SetLineColor(kBlack);
    TBox *b1 = new TBox(-1,0,1,map_syst.size());
    TBox *b2 = new TBox(-2,0,2,map_syst.size());
    b1 -> SetFillColor(kGreen);
    b2 -> SetFillColor(kYellow);
    b2 ->Draw("same");
    b1 -> Draw("same");
    l0 -> Draw("same");
    //
    // Looping over the TGraph vector to fill in the pull plot
    //
    for( const auto tg : tgs ){
      tg -> SetMarkerStyle(20);
      tg -> SetLineWidth(1);
      tg -> Draw("p");
    }
    text_latex = "#hat{#theta}_{ana}-#hat{#theta}_{ref}";
  } 
  //
  // Drawing the relative difference of the error
  //
  if(type==ERRREF){
    //
    // Looping over the TGraph vector to fill in the pull plot
    //
    for( const auto tg : tgs ){
      tg -> SetMarkerStyle(20);
      tg -> SetLineWidth(1);
      tg -> Draw("p");
    }
    text_latex = "(#Delta#hat{#theta}_{ana}-#Delta#hat{#theta}_{ref})/#Delta#hat{#theta}_{ref}";
  } 

  TLatex l;
  l.SetNDC();
  l.SetTextColor(kBlue);
  l.SetTextSize(l.GetTextSize()*1.7);
  l.DrawLatex( (type==PULLREF) ? 0.48 : 0.45,0.04,text_latex);

  //
  // Overall plot style adjustments
  //
  gPad -> SetTopMargin(0.05);
  gPad -> SetBottomMargin(0.1);
  gPad -> SetLeftMargin(0.6);
  gPad -> SetRightMargin(0.05);
  gPad -> RedrawAxis();
  gStyle -> SetOptStat(0);
  c.SetTickx();

  //
  // Legend making (only if there is more than 1 TGraph in the vector)
  //
  if(tgs.size()>1){
    TLegend *leg = new TLegend(0.,0.5,0.5,0.99,"","NDC");
    leg->SetLineColor(0);
    leg->SetFillStyle(0);
    for( const auto tg : tgs ){
      leg -> AddEntry( tg, tg->GetName(), "pl");
    }
    leg->Draw();
  }

  c.Print( (name+".pdf").c_str() );
  return 1;
}

//______________________________________________________________________________
//
int build_plot( const std::string &canvas_name,
                const std::map < std::string, int > &map_syst,
                const std::map < std::string, std::map < std::string, NP > > &map_NPs,
                const std::string &ref = "" ){

  //
  // Getting the reference fit result
  //
  std::map < std::string, NP > map_ref;
  if(ref!=""){
    map_ref = map_NPs.at(ref);
  }

  //
  // Looping over the fits
  //
  std::vector < TGraphAsymmErrors* > g;
  std::vector < TGraphAsymmErrors* > g_pull_ref;
  std::vector < TGraphAsymmErrors* > g_err_ref;
  int lineHeight = 20;
  int offsetUp = 50;
  int offsetDown = 40;
  int offset = offsetUp + offsetDown;
  int newHeight = offset + map_syst.size()*lineHeight;
  int index = 0;
  std::vector < int > colors = {kBlack, kRed, kBlue, kGreen+2, kOrange, kPink+9,kCyan};
  for( const auto &fit : map_NPs ){
    g.push_back(new TGraphAsymmErrors(map_syst.size()));
    g_pull_ref.push_back(new TGraphAsymmErrors(map_syst.size()));
    g_err_ref.push_back(new TGraphAsymmErrors(map_syst.size()));
    TGraphAsymmErrors *current_g = g[g.size()-1];
    TGraphAsymmErrors *current_g_pull_ref = g_pull_ref[g.size()-1];
    TGraphAsymmErrors *current_g_err_ref = g_err_ref[g.size()-1];
    current_g -> SetLineColor(colors[index]);
    current_g -> SetMarkerColor(colors[index]);
    current_g -> SetName(fit.first.c_str());
    current_g_pull_ref -> SetName(fit.first.c_str());
    current_g_err_ref -> SetName(fit.first.c_str());
    current_g_pull_ref -> SetLineColor(colors[index]);
    current_g_err_ref -> SetLineColor(colors[index]);
    current_g_pull_ref -> SetMarkerColor(colors[index]);
    current_g_err_ref -> SetMarkerColor(colors[index]);
    index++;
    int counter_ana = 0;
    for( const auto &np : fit.second ){
      if(map_syst.find(np.second.name)==map_syst.end()) continue;
      counter_ana++;
      double offset = 0.1*index;
      const double pull = np.second.central;
      const double errHi = np.second.errHi;
      const double errLo = -np.second.errLo;
      current_g -> SetPoint( map_syst.at(np.second.name), pull, map_syst.at(np.second.name)+0.1+offset );
      current_g -> SetPointError( map_syst.at(np.second.name), errLo, errHi, 0., 0. );
      if(ref!=""){
        const double pull_ref = map_ref.at(np.second.name).central;
        const double err_ref = map_ref.at(np.second.name).errHi;
        current_g_pull_ref -> SetPoint( map_syst.at(np.second.name), pull-pull_ref, map_syst.at(np.second.name)+0.1+offset );
        current_g_err_ref -> SetPoint( map_syst.at(np.second.name), 100.*(errHi-err_ref)/err_ref, map_syst.at(np.second.name)+0.1+offset );
      }
    }
  }
  TCanvas c(("Overlay_"+canvas_name).c_str(),("Overlay_"+canvas_name).c_str(),1000,newHeight);
  build_canvas( c, g, map_syst);

  if(ref != ""){
    TCanvas c_pull(("Overlay_PullChange_"+canvas_name).c_str(),("Overlay_PullChange_"+canvas_name).c_str(),1000,newHeight);
    build_canvas( c_pull, g_pull_ref, map_syst );
    TCanvas c_err(("Overlay_ErrChange_"+canvas_name).c_str(),("Overlay_ErrChange_"+canvas_name).c_str(),1000,newHeight);
    build_canvas( c_err, g_err_ref, map_syst );
  }

  return 1;
}
//..............................................................................
//

//______________________________________________________________________________
//
int draw_pull_plots( const std::map < std::string, std::map < std::string, NP > > &map_NPs, const std::string &ref = "" ){

  //
  // First, getting a list of all the nuisance parameters
  //
  std::set < std::string > set_all_systs;
  for( const auto &fit : map_NPs ){
    for( const auto &np : fit.second ){
      set_all_systs.insert( np.second.name );
    }
  }

  //
  // Creating a canvas for the NPs that are only affecting one analysis. To do
  // that looping over all the analyses for get the corresponding nuisance
  // parameters.
  //
  for( const auto &ana : analyses ){
    std::map < std::string, int > map_syst;
    for( const auto &np : set_all_systs ){
      if(np.find(ana.title)!=std::string::npos){
        //this NP is here for one particular analysis !
        map_syst.insert( std::pair < std::string, int >( np, map_syst.size() ) );
      }
    }
    if(map_syst.size()==0) continue;
    build_plot( ana.title+"_only_NPs", map_syst, map_NPs, ref);
    //Removing the NPs that have been already drawns
    for( const auto &np : map_syst ){
      set_all_systs.erase(np.first);
    }
  }

  //
  // Removing the analysis specific NPs and plot the remaining NPs
  //
  std::map < std::string, int > map_syst;
  for( const auto &np : set_all_systs ){
    map_syst.insert( std::pair < std::string, int >( np, map_syst.size() ) );
  }
  build_plot( "shared_NPs", map_syst, map_NPs, ref);


  return true;
}
//..............................................................................
//

//______________________________________________________________________________
//
void draw_correlation_matrices( const std::string &legend, RooFitResult* result,
                                const double threshold = 0.30, const RooFitResult* ref_result = nullptr ){
  //
  // Getting the list of parameters in the considered fit
  //
  std::vector < std::string > np_names_init;
  RooRealVar* var(0);
  TIterator *param = result -> floatParsFinal().createIterator();
  while( (var = (RooRealVar*) param->Next()) ){
    TString varname = var->GetName();
    if(varname.Contains("gamma_stat")) continue;
    np_names_init.push_back((std::string)varname);
  }

  //
  // Getting the NPs with correlations above a given threshold
  //
  std::vector < std::string > np_names;
  for( unsigned int np1 = 0; np1 < np_names_init.size(); ++np1 ){
    const std::string str_np1 = np_names_init[np1];
    for( unsigned int np2 = 0; np2 < np_names_init.size(); ++np2 ){
      if(np1==np2) continue;
      const std::string str_np2 = np_names_init[np2];
      double corr = result -> correlation( str_np1.c_str(), str_np2.c_str() );
      if( abs(corr) > threshold ){
        np_names.push_back(str_np1);
        break;
      }
    }
  }

  //
  // Making the plot
  //
  const unsigned int N = np_names.size();
  TH2F *h_corr = new TH2F("h_corr","",N,0,N,N,0,N);
  TH2F *h_ref_change = new TH2F("h_corr_ref_change","",N,0,N,N,0,N);
  h_corr->SetDirectory(0);
  h_ref_change->SetDirectory(0);
  for( unsigned int np1 = 0; np1 < np_names.size(); ++np1 ){
    const std::string str_np1 = np_names[np1];
    h_corr->GetXaxis()->SetBinLabel(np1+1,str_np1.c_str());
    h_corr->GetYaxis()->SetBinLabel(N-np1,str_np1.c_str());
    for( unsigned int np2 = 0; np2 < np_names.size(); ++np2 ){
      const std::string str_np2 = np_names[np2];
      double corr = result -> correlation( str_np1.c_str(), str_np2.c_str() );
      double corr_ref(0.),corr_rel_change(0.);
      if(ref_result){
        corr_ref = ref_result -> correlation( str_np1.c_str(), str_np2.c_str() );
        corr_rel_change = corr - corr_ref;
      }
      h_corr -> SetBinContent(np1+1,N-np2,100.*corr);
      if(ref_result){
        if(fabs(corr_rel_change)>0){
          h_ref_change -> SetBinContent(np1+1,N-np2,100.*corr_rel_change);
        }
      }
    }
  }
  h_corr -> SetMaximum(100);
  h_corr -> SetMinimum(-100);
  h_ref_change -> SetMaximum(100);
  h_ref_change -> SetMinimum(-100);

  //
  // Setting the style
  //
  int size = 500;
  if(np_names.size()>10){
    size = np_names.size()*70;
  }
  TCanvas *c1 = new TCanvas("","",0.,0.,size+500,size+500);
  gStyle->SetPalette(1);
  gStyle->SetPaintTextFormat(".0f");
  gPad->SetLeftMargin(0.3);
  gPad->SetBottomMargin(0.3);
  gPad->SetRightMargin(0.1);
  gPad->SetTopMargin(0.01);
  gStyle -> SetOptStat(0);
  h_corr->SetMarkerSize(h_corr->GetMarkerSize()*0.4);
  h_corr->GetXaxis()->LabelsOption("v");
  h_corr->GetXaxis()->SetLabelSize( h_corr->GetXaxis()->GetLabelSize()*0.5 );
  h_corr->GetYaxis()->SetLabelSize( h_corr->GetYaxis()->GetLabelSize()*0.5 );
  h_corr->GetZaxis()->SetLabelSize( h_corr->GetZaxis()->GetLabelSize()*0.5 );
  c1->SetTickx(0);
  c1->SetTicky(0);
  h_corr->GetYaxis()->SetTickLength(0);
  h_corr->GetXaxis()->SetTickLength(0);
  c1->SetGrid();
  h_corr->Draw("colz TEXT");
  c1->RedrawAxis("g");
  c1->SaveAs(("Corr_"+legend+".pdf").c_str());
  if(ref_result){
    TH2F* h_ref_change_style = (TH2F*)h_corr -> Clone();
    h_ref_change_style -> SetDirectory(0);
    for( unsigned int ibinx = 1; ibinx <= h_ref_change_style -> GetNbinsX(); ++ibinx ){
      for( unsigned int ibiny = 1; ibiny <= h_ref_change_style -> GetNbinsY(); ++ibiny ){
        h_ref_change_style -> SetBinContent( ibinx, ibiny, h_ref_change -> GetBinContent( ibinx, ibiny) );
      }
    }
    gPad->SetRightMargin(0.15);
    h_ref_change_style->GetZaxis()->SetLabelSize(h_ref_change_style->GetZaxis()->GetLabelSize()/2.);
    h_ref_change_style->GetZaxis()->SetTitleSize(h_ref_change_style->GetZaxis()->GetTitleSize()/1.5);
    h_ref_change_style->GetZaxis()->SetTitle("Change in correlation");
    gPad->SetLeftMargin(0.7*600/(size+300)-0.2);
    h_ref_change_style->Draw("colz TEXT");
    c1->SaveAs(("CorrChange_Ref_"+legend+".pdf").c_str());    
  }

}
//..............................................................................
//

//______________________________________________________________________________
//
int draw_fits( const std::map < std::string, std::string > &components,
                const std::string &outDir = "outComp/",
                const std::string &ref = "" ){

  float xmax = 2;
  gStyle->SetEndErrorSize(0.);

  for( const auto &limit : components ){
    Ana ana;
    ana.file = limit.second;
    ana.title = limit.first;
    analyses.push_back(ana);
  }

  //
  // Filling a map containing all the needed information about the nuisance
  // parameters for each fit configuration
  //
  std::map < std::string, std::map < std::string, NP > > map_NPs;
  std::map < std::string, RooFitResult* > map_RFR;
  for ( const auto &channel : analyses ){
    std::map < std::string, NP > temp_map;
    TFile *f = TFile::Open( (channel.file).c_str(), "READ" );
    RooFitResult* fit_result = 0;
    for ( const auto key : *(gDirectory -> GetListOfKeys()) ){
      if(((TString)key->GetName()).Contains("nll_")){
        fit_result = (RooFitResult*)f->Get(key->GetName());
        break;
      }
    }
    RooRealVar* var(0);
    TIterator *param = fit_result -> floatParsFinal().createIterator();
    while( (var = (RooRealVar*) param->Next()) ){
      TString varname = var->GetName();
      if(varname.Contains("gamma_stat")) continue;
      varname.ReplaceAll("alpha_","");
      double pull  = var->getVal() / 1.0 ; // GetValue() return value in unit of sigma
      double errorHi = var->getErrorHi() / 1.0;
      double errorLo = var->getErrorLo() / 1.0;
      NP temp;
      temp.name = (std::string) varname;
      temp.central = pull;
      temp.errHi = errorHi;
      temp.errLo = errorLo;
      temp_map.insert( std::pair < std::string, NP >( temp.name, temp ) );
    }
    map_NPs.insert( std::pair < std::string, std::map < std::string, NP > >( channel.title, temp_map) );
    map_RFR.insert( std::pair < std::string, RooFitResult* >( channel.title, fit_result) );
  }

  //Drawing the correlation matrix and the change wrt reference (if needed)
  RooFitResult *fit_result_ref = nullptr;
  for ( const auto &ana : map_RFR ){
    if(ana.first==ref){
      fit_result_ref = ana.second;
      break;
    }
  }
  for ( const auto &ana : map_RFR ){
    draw_correlation_matrices( ana.first, ana.second, 0.3, fit_result_ref );
  }

  //Drawing the pull plots
  draw_pull_plots( map_NPs, ref );
  return 1;
}
//..............................................................................
//
