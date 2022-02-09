#include "messages.h"
#include "string_utils.h"
#include "FittingTool.h"

#include "TFile.h"
#include "RooWorkspace.h"
#include "RooStats/ModelConfig.h"
#include "RooSimultaneous.h"
#include "RooDataSet.h"
#include "RooRealSumPdf.h"
#include "TSystem.h"

#include <map>
#include <vector>
#include <iostream>

int main ( int argc, char **argv ){

  //
  // Getting default values for the parameters
  //
  std::string file_path = "";
  std::string workspace_name = "combined";
  std::string data_name = "obsData";
  std::string output_folder = "output_fit/";
  std::string output_suffix = "";
  bool debug = false;
  bool poi_fixed = true;
  double poi_value = 0.0;

  //
  // Get the user's command options
  //
  for( unsigned int iArg = 1; iArg < argc; ++iArg ){
    std::string value(argv[iArg]);
    std::string argument("");
    string_utils::parse_string(value, argument, "=");
    if(argument=="file_path") file_path = value;
    else if(argument=="workspace_name") workspace_name = value;
    else if(argument=="data_name") data_name = value;
    else if(argument=="output_folder") output_folder = value;
    else if(argument=="output_suffix") output_suffix = value;
    else if(argument=="debug") debug = string_utils::bool_value(value);
    else if(argument=="poi_fixed") poi_fixed = string_utils::bool_value(value);
    else if(argument=="poi_value") poi_value = atof(value.c_str());
    else {
      std::cout << "Argument *" << argument;
      std::cout << "* is unknown. Only file_path, workspace_name, data_name, output_folder, ";
      std::cout << "output_suffix, debug, poi_value and poi_fixed are supported. Aborting !" << std::endl;
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

  RooStats::ModelConfig* mc = (RooStats::ModelConfig*)ws->obj("ModelConfig");
  if(!mc){
    messages::print_error( __func__, __FILE__, __LINE__, "Cannot retrieve the ModelConfig. Aborting !" );
    abort();
  }
  RooSimultaneous *simPdf = (RooSimultaneous*)(mc->GetPdf());
  if(!simPdf){
    messages::print_error( __func__, __FILE__, __LINE__, "Cannot retrieve the Pdf. Aborting !" );
    abort();
  }
  RooDataSet* data = (RooDataSet*)ws->data(data_name.c_str());
  if(!data){
    messages::print_error( __func__, __FILE__, __LINE__, "Cannot retrieve the data. Aborting !" );
    abort();
  }
  

  //
  // Running the fit
  //
  FittingTool *fitTool = new FittingTool();
  fitTool -> ValPOI( poi_value );
  fitTool -> ConstPOI( poi_fixed );
  fitTool -> OutputFolder( output_folder );
  fitTool -> OutputSuffix( output_suffix );
  fitTool -> FitPDF( mc, simPdf, data );
  fitTool -> ExportFitResultInTextFile( output_folder + "/FitResult" + output_suffix + ".txt" );
  fitTool -> ExportFitResultInROOTFile( output_folder + "/FitResult" + output_suffix + ".root" );

  f_in -> Close();

  return 1;
}
