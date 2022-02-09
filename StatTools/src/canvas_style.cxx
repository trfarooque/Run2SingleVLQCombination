#include "canvas_style.h"

#include "TGraphAsymmErrors.h"
#include "TCanvas.h"
#include "TGraph.h"
#include "TH1.h"
#include "TPad.h"
#include "THStack.h"
#include "TLegend.h"
#include "TStyle.h"
#include "TLine.h"
#include "TFile.h"

#include "RooPlot.h"

#include <iostream>


//________________________________________________________________________
//
canvas_style::canvas_style():
m_pad0(0),
m_pad1(0),
m_stack(0),
m_h_tot(0),
m_tot(0),
m_tot_err(0),
m_data(0),
m_xtitle(""), m_ytitle("Number of events"), 
m_lumiLabel(""), m_CME(""), 
m_useATLASLabel(true), m_ATLASLabel("")
{
    m_histograms.clear();
}

//________________________________________________________________________
//
canvas_style::canvas_style( const canvas_style& q )
{}

//________________________________________________________________________
//
canvas_style::~canvas_style()
{}

//________________________________________________________________________
//
void canvas_style::init(){
	//
	// Defining the two pads
	//
	m_pad0 = new TPad("m_pad0","m_pad0",0,0.20,1,1,0,0,0);
    m_pad0->SetTicks(1,1);
    m_pad0->SetTopMargin(0.05);
    m_pad0->SetBottomMargin(0.1);
    m_pad0->SetLeftMargin(0.14);
    m_pad0->SetRightMargin(0.05);
    m_pad0->SetFrameBorderMode(0);
    m_pad0->SetFillStyle(0);
    //
    m_pad1 = new TPad("m_pad1","m_pad1",0,0,1,0.28,0,0,0);
    m_pad1->SetTicks(1,1);
    m_pad1->SetTopMargin(0.0);
    m_pad1->SetBottomMargin(0.37);
    m_pad1->SetLeftMargin(0.14);
    m_pad1->SetRightMargin(0.05);
    m_pad1->SetFrameBorderMode(0);
    m_pad1->SetFillStyle(0);
    //
    m_pad1->Draw();
    m_pad0->Draw();
    m_pad0->cd();

    //
    // Plots
    //
    m_stack = new THStack("h_stack","h_stack");
    m_ratio = new TGraphAsymmErrors();

    //
    // Legend
    //
    m_lgd = new TLegend(0.6,0.6,0.93,0.93);
    m_lgd -> SetLineColor(0);
    m_lgd -> SetFillStyle(0);
}

//________________________________________________________________________
//
void canvas_style::AddStackedSample( TH1* hist, const std::string &legend ){
    //
    // If a histogram with the same legend already exists, just merge with
    // the previous one.
    //
    if( m_histograms.find(legend) != m_histograms.end() ){
        //The sample is already here ! Merge ! 
        m_histograms.at(legend) -> Add(hist);
    } else {
        //The sample is not yet here ! Let's add it in !
        TH1* temp = (TH1*)hist -> Clone();
        temp -> SetDirectory(0);
        m_histograms.insert( std::pair < std::string, TH1* > ( legend, temp ) );
    }

    if( m_h_tot == 0 ){
        m_h_tot = (TH1F*) hist -> Clone();
        m_h_tot -> SetDirectory(0);
    } else {
        m_h_tot -> Add(hist);
    }   

}

//________________________________________________________________________
//
void canvas_style::DrawAll(){

    //////////////////////////////////////////////////////////////////////
    //
    // Drawing the top pad
    //
    //////////////////////////////////////////////////////////////////////

    //
    // First, let build the stack
    //
    for( const auto &sample : m_histograms ){
        m_stack -> Add(sample.second);
        m_lgd -> AddEntry(sample.second, sample.first.c_str(), "f");     
    }

    //
    // Now draw ...
    //
	m_pad0 -> cd();
    m_h_tot -> Draw("hist"); 
	m_tot_err -> Draw("f");
	m_stack -> Draw("HISTsame");
	m_tot_err -> Draw("f");
	m_data -> Draw("ep");
    m_lgd -> Draw();
	this -> cd();

    //Sets the title of the first histograms
    m_h_tot -> SetLineColor(kWhite); 
    m_h_tot -> SetTitle(""); 
    m_h_tot -> SetFillColor(kWhite);
    m_h_tot -> SetFillStyle(kWhite); 

    //Sets the maximum 
    const double max = 1.3 * TMath::Max(m_data -> GetHistogram() -> GetMaximum(), m_stack -> GetHistogram() -> GetMaximum());
    m_h_tot -> SetMaximum( max );
    m_h_tot -> SetMinimum( 0.0001 );

    //Gets the X range properly
    double xmin = m_stack -> GetHistogram() -> GetBinLowEdge(1);
    double xmax = m_stack -> GetHistogram() -> GetBinLowEdge( m_stack -> GetHistogram() -> GetNbinsX() ) +
                    m_stack -> GetHistogram() -> GetBinWidth( m_stack -> GetHistogram() -> GetNbinsX() );
    m_h_tot -> GetXaxis() -> SetRangeUser( xmin, xmax );

    //Setting up the axis titles
    m_h_tot -> GetYaxis() -> SetTitle( m_ytitle.c_str() );

    //Hide the X axis labels ... since they will be in the bottom pad
    m_h_tot -> GetXaxis() -> SetLabelOffset(10);
    m_h_tot -> GetXaxis() -> SetTitleOffset(10);
    m_h_tot -> GetYaxis() -> SetTitleSize( m_tot_err -> GetHistogram() -> GetYaxis() -> GetTitleSize() * 1.2 );
    m_h_tot -> GetYaxis() -> SetLabelSize( m_tot_err -> GetHistogram() -> GetYaxis() -> GetLabelSize() * 1.2 );

    m_pad0 -> RedrawAxis();


    //////////////////////////////////////////////////////////////////////
    //
    // Drawing the bottom pad
    //
    //////////////////////////////////////////////////////////////////////

    m_pad1 -> cd();

    //Dummy plot to set the scales and the axes
    TH1F* dummy = new TH1F("dummyratio","", m_tot_err -> GetHistogram() -> GetNbinsX(), xmin, xmax ) ;
    dummy -> SetDirectory(0);
    dummy -> Draw();
    dummy -> SetMaximum(1.501);
    dummy -> SetMinimum(0.50001);
    gStyle -> SetOptStat(0);

    //Set titles
    dummy -> GetYaxis() -> SetTitle("Data / Pred.");
    dummy -> GetXaxis() -> SetTitle(m_xtitle.c_str());

    //Set title and label sizes
    dummy -> GetYaxis() -> SetTitleSize( m_tot_err -> GetHistogram() -> GetYaxis() -> GetTitleSize() * 3 );
    dummy -> GetYaxis() -> SetLabelSize( m_tot_err -> GetHistogram() -> GetYaxis() -> GetLabelSize() * 3 );
    dummy -> GetYaxis() -> SetNdivisions( 204 );
    dummy -> GetXaxis() -> SetTitleSize( m_tot_err -> GetHistogram() -> GetXaxis() -> GetTitleSize() * 4 );
    dummy -> GetXaxis() -> SetLabelSize( m_tot_err -> GetHistogram() -> GetXaxis() -> GetLabelSize() * 4 );
    dummy -> GetYaxis() -> SetTitleOffset( 0.4 );

    //Drawing an horizontal line
    TLine *line = new TLine(xmin, 1, xmax, 1);
    line -> SetLineColor(kBlack);
    line -> SetLineWidth(2);
    line -> SetLineStyle(2);
    line -> Draw();

    //Computing the uncertainty band
    TGraphAsymmErrors *error_band = new TGraphAsymmErrors(m_tot_err->GetN());
    for(unsigned int ipt = 0; ipt < m_tot_err -> GetN(); ++ipt){
        double x,y;
        m_tot_err -> GetPoint( ipt, x, y);
        double tot_pred = m_h_tot -> GetBinContent( m_h_tot -> FindBin( x ));
        error_band -> SetPoint( ipt, x, ((tot_pred==0) ? 0 : y/tot_pred) );
    }


    //Computing the ratio
    for(unsigned int ipt = 0; ipt < m_data -> GetN(); ++ipt){
        double x_data(0),y_data(0);
        m_data -> GetPoint(ipt,x_data,y_data);
        double data_err_up = m_data -> GetErrorYhigh(ipt);
        double data_err_down = m_data -> GetErrorYlow(ipt);
        double tot_pred = m_h_tot -> GetBinContent( m_h_tot -> FindBin( x_data ));
        m_ratio -> SetPoint( ipt, x_data, y_data/tot_pred );
        m_ratio -> SetPointError( ipt, 0, 0, data_err_down/tot_pred, data_err_up/tot_pred );
    }

    error_band -> SetFillStyle( m_tot_err -> GetFillStyle() );
    error_band -> SetFillColor( m_tot_err -> GetFillColor() );
    error_band -> Draw("f");

    m_ratio -> Draw("ep");
    m_ratio -> SetMarkerStyle( m_data -> GetMarkerStyle() );

	TString oName = this -> GetName();
	oName += ".pdf";

    this -> Print( oName );
    this -> cd();
}


//________________________________________________________________________
//
void canvas_style::SaveAllInfo(){
    /*
    Function to store all the ROOT objects so the plots can be made later on.
    */
    TString oName = this -> GetName();
    oName += ".root";
    TFile *f_out = TFile::Open( oName, "RECREATE" );
    for( const auto &sample : m_histograms ){
        sample.second -> Write();   
    }
    m_h_tot -> SetLineColor(1);
    m_h_tot -> Write("total_central");
    m_tot_err -> Write("total_err");
    m_data -> Write("data");
    f_out -> Close();
    delete f_out;
}


