#include "messages.h"
#include "string_utils.h"
#include "RooExpandedFitResult.h"
#include "draw_utils.h"

#include "TFile.h"
#include "TCanvas.h"
#include "TH2.h"
#include "THStack.h"
#include "TSystem.h"
#include "RooHist.h"

#include "RooPlot.h"
#include "RooWorkspace.h"
#include "RooStats/ModelConfig.h"
#include "RooSimultaneous.h"
#include "RooDataSet.h"
#include "RooRealSumPdf.h"
#include "RooCategory.h"
#include "RooProduct.h"
#include "RooRealVar.h"

#include <map>
#include <vector>
#include <iostream>

using namespace RooFit;


//___________________________________________________________________________________________
//
int main ( int argc, char **argv ){

  //
  // Getting default values for the parameters
  //
  //input workspace
  std::string file_path = "";
  std::string workspace_name = "combined";
  std::string data_name = "obsData";
  //fit result
  std::string fr_file_path = "";
  std::string fr_name = "nll_simPdf_obsData_with_constr";
  //pre-fit conditions
  double mu_val = 0.;
  //output
  std::string output_folder = "output_fit/";
  std::string output_suffix = "";
  //signal name pattern
  std::string signal_name = "SIGNAL";
  //prefit/postfit
  bool do_postfit = false;
  bool do_prefit = false;
  //samples file
  std::string sample_file = "";
  std::map < std::string, draw_utils::Sample > sample_vector;
  //region file
  std::string region_file = "";
  std::map < std::string, draw_utils::Region > region_vector;
  //debug
  bool debug = false;

  RooMsgService::instance().setGlobalKillBelow(RooFit::ERROR);
  if(debug){
    RooMsgService::instance().setGlobalKillBelow(RooFit::INFO);
  }

  //
  // Get the user's command options
  //
  for( unsigned int iArg = 1; iArg < argc; ++iArg ){
    std::string value(argv[iArg]);
    std::string argument("");
    string_utils::parse_string(value, argument, "=");
    //
    if(argument=="file_path") file_path = value;
    else if(argument=="workspace_name") workspace_name = value;
    else if(argument=="data_name") data_name = value;
    //
    else if(argument=="fr_file_path") fr_file_path = value;
    else if(argument=="fr_name") fr_name = value;
    //
    else if(argument=="mu_val") mu_val = atof(value.c_str());
    //
    else if(argument=="output_folder") output_folder = value;
    else if(argument=="output_suffix") output_suffix = value;
    //
    else if(argument=="do_postfit") do_postfit = string_utils::bool_value(value);
    else if(argument=="do_prefit") do_prefit = string_utils::bool_value(value);
    //
    else if(argument=="signal_name") signal_name = value;
    //
    else if(argument=="region_file"){
      region_file = value;
      draw_utils::ExtractRegionConfigFileInfo(region_vector, region_file);
    }
    //
    else if(argument=="sample_file"){
      sample_file = value;
      draw_utils::ExtractSampleConfigFileInfo(sample_vector, sample_file);
    }
    //
    else if(argument=="debug") debug = string_utils::bool_value(value);
    else {
      std::cout << "Argument *" << argument;
      std::cout << "* is unknown. Only file_path, workspace_name, data_name, output_folder, ";
      std::cout << "output_suffix and debug are supported. Aborting !" << std::endl;
      abort();
    }
  }

  gSystem -> mkdir( output_folder.c_str(), true );

  //
  // Opening the rootfile
  //
  if(file_path==""){
    messages::print_error( __func__, __FILE__, __LINE__, "No input file provided. Aborting !" );
    abort();
  }
  TFile *f_in = TFile::Open( file_path.c_str(), "READ");

  //
  // Getting all the needed information
  //
  RooWorkspace* ws = (RooWorkspace*)f_in->Get(workspace_name.c_str());
  if(!ws){
    messages::print_error( __func__, __FILE__, __LINE__, "Cannot retrieve the workspace. Aborting !" );
    abort();
  }
  RooFIter rfiter = ws->components().fwdIterator();
  RooAbsArg* arg;
  while ((arg = rfiter.next())) {
    if (arg->IsA() == RooRealSumPdf::Class()) {
      arg->setAttribute("BinnedLikelihood");
    }
  }
  //
  //
  RooStats::ModelConfig* mc = (RooStats::ModelConfig*)ws->obj("ModelConfig");
  if(!mc){
    messages::print_error( __func__, __FILE__, __LINE__, "Cannot retrieve the ModelConfig. Aborting !" );
    abort();
  }
  //
  //
  RooSimultaneous *simPdf = (RooSimultaneous*)(mc->GetPdf());
  if(!simPdf){
    messages::print_error( __func__, __FILE__, __LINE__, "Cannot retrieve the Pdf. Aborting !" );
    abort();
  }
  //
  //
  RooDataSet* data = (RooDataSet*)ws->data(data_name.c_str());
  if(!data){
    messages::print_error( __func__, __FILE__, __LINE__, "Cannot retrieve the data. Aborting !" );
    abort();
  }
  //
  //
  if(!do_prefit && !do_postfit){
    messages::print_warning( __func__, __FILE__, __LINE__, "Not prefit, nor postfit ... Quitting..." );
    return 1;
  }


  int counter = 0;
  for( const bool to_do : {do_prefit,do_postfit} ){
    if(to_do){
      //
      // Getting the fit results
      //
      bool postfit = (counter==1);
      RooFitResult* re = draw_utils::GetFitResults( mc, mu_val, fr_file_path, fr_name, postfit );
      //
      // Will keep track of the histograms here
      //
      std::map < std::string, draw_utils::RegionHists > map_regions;
      draw_utils::GetAllROOTObjects( mc, simPdf, data, re, map_regions );
      //
      // Draw all objects in a nice canvas 
      //
      for( const auto &reg : map_regions ){
        draw_utils::DrawCanvas( output_folder, reg, region_vector, sample_vector, postfit );
      }

      delete re;
    }
    counter++;
  }

  return 1;
}
