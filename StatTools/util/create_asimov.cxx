#include "messages.h"
#include "string_utils.h"

#include "TFile.h"
#include "RooWorkspace.h"
#include "RooStats/ModelConfig.h"
#include "RooRealSumPdf.h"
#include "RooRealVar.h"
#include "RooSimultaneous.h"
#include "RooCategory.h"
#include "RooArgSet.h"
#include "RooDataSet.h"

#include <map>
#include <vector>
#include <iostream>

int main ( int argc, char **argv ){

  //
  // Getting default values for the parameters
  //
  double poi_value = 0.;
  std::string file_path = "";
  std::string workspace_name = "combined";
  std::string str_np_values = "";
  std::string asimov_name = "asimov0";
  bool debug = false;

  //
  // Get the user's command options
  //
  for( unsigned int iArg = 1; iArg < argc; ++iArg ){
    std::string value(argv[iArg]);
    std::string argument("");
    string_utils::parse_string(value, argument, "=");
    if(argument=="file_path") file_path = value;
    else if(argument=="workspace_name") workspace_name = value;
    else if(argument=="asimov_name") asimov_name = value;
    else if(argument=="np_values") str_np_values = value;
    else if(argument=="poi_value") poi_value = atof(value.c_str());
    else if(argument=="debug") debug = string_utils::bool_value(value);
    else {
      std::cout << "Argument *" << argument;
      std::cout << "* is unknown. Only file_path, workspace_name, do_checks and ";
      std::cout << "do_content_dump are supported. Aborting !" << std::endl;
      abort();
    }
  }

  //
  // Opening the rootfile
  //
  if(file_path==""){
      messages::print_error( __func__, __FILE__, __LINE__, "No input file provided. Aborting !" );
      abort();
  }
  TFile *f_in = TFile::Open( file_path.c_str(), "READ");
  //Getting the workspace
  RooWorkspace* ws = (RooWorkspace*)f_in->Get(workspace_name.c_str());
  ws -> loadSnapshot("NominalParamValues");
  //Getting a vector containing the desired values of the nuisance parameters
  std::map < std::string, double > np_values;
  for( auto np : string_utils::split_string(str_np_values,',') ){
    std::vector < std::string > splitted = string_utils::split_string(np,':');
    if(splitted.size()!=2){
      messages::print_warning( __func__, __FILE__, __LINE__, "Argument *"+np+"* cannot be decrypted." );
      continue;
    }
    np_values.insert( std::pair < std::string, double >( splitted[0], atof(splitted[1].c_str())) );
  }

  //
  // Some debug messages
  //
  if(debug){
    std::cout << "=> Dumping data with the following parameters" << std::endl;
    if(np_values.size()){
      std::cout << "    * Injected NP values " << std::endl;
      for ( const std::pair < std::string, double > npValue : np_values ){
        std::cout << "       - NP: " << npValue.first << "       Value: " << npValue.second << std::endl;
      }
    } else {
      std::cout << "    * No NP values injected " << std::endl;
    }
    std::cout << "    * POI value: " << poi_value << std::endl;
  }

  //############################################################################
  //
  // Creating the Asimov
  //
  //############################################################################
  //-- Getting the ModelConfig object
  RooStats::ModelConfig *mc = (RooStats::ModelConfig*)ws -> obj("ModelConfig");
  //-- Save the initial values of the NP
  ws->saveSnapshot("InitialStateModelGlob",   *mc->GetGlobalObservables());
  ws->loadSnapshot("InitialStateModelGlob");
  //-- Setting binned likelihood option
  RooFIter rfiter = ws->components().fwdIterator();
  RooAbsArg* arg;
  while ((arg = rfiter.next())) {
    if (arg->IsA() == RooRealSumPdf::Class()) {
      arg->setAttribute("BinnedLikelihood");
    }
  }
  //-- Creating a set
  const char* weightName="weightVar";
  RooArgSet obsAndWeight;
  obsAndWeight.add(*mc->GetObservables());
  RooRealVar* weightVar = NULL;
  if ( !(weightVar = ws->var(weightName)) ){
    ws->import(*(new RooRealVar(weightName, weightName, 1,0,10000000)));
    weightVar = ws->var(weightName);
  }
  obsAndWeight.add(*ws->var(weightName));
  ws->defineSet("obsAndWeight",obsAndWeight);
  //-- POI
  RooRealVar * poi = (RooRealVar*) mc->GetParametersOfInterest()->first();
  poi -> setVal(poi_value);
  //-- Nuisance parameters
  RooRealVar* var(nullptr);
  TIterator *npIterator = mc -> GetNuisanceParameters() -> createIterator();
  while( (var = (RooRealVar*) npIterator->Next()) ){
    std::map < std::string, double >::const_iterator it_npValue = np_values.find( var -> GetName() );
    if( it_npValue != np_values.end() ){
      var -> setVal(it_npValue -> second);
    }
  }
  //Looping over regions
  std::map< std::string, RooDataSet*> asimovDataMap;
  RooSimultaneous* simPdf = dynamic_cast<RooSimultaneous*>(mc->GetPdf());
  RooCategory* channelCat = (RooCategory*)&simPdf->indexCat();
  TIterator* iter = channelCat->typeIterator() ;
  RooCatType* tt = NULL;
  int nrIndices = 0;
  int iFrame = 0;
  int i = 0;
  while( (tt = (RooCatType*) iter -> Next()) ) {

    channelCat->setIndex(i);
    iFrame++;
    i++;

    // Get pdf associated with state from simpdf
    RooAbsPdf* pdftmp = simPdf->getPdf(channelCat->getLabel()) ;

    // Generate observables defined by the pdf associated with this state
    RooArgSet* obstmp = pdftmp->getObservables(*mc->GetObservables()) ;

    RooDataSet* obsDataUnbinned = new RooDataSet(Form("combAsimovData%d",iFrame),Form("combAsimovData%d",iFrame),RooArgSet(obsAndWeight,*channelCat),RooFit::WeightVar(*weightVar));
    RooRealVar* thisObs = ((RooRealVar*)obstmp->first());
    double expectedEvents = pdftmp->expectedEvents(*obstmp);
    double thisNorm = 0;

    for(int jj=0; jj<thisObs->numBins(); ++jj){
      thisObs->setBin(jj);
      thisNorm=pdftmp->getVal(obstmp)*thisObs->getBinWidth(jj);
      if (thisNorm*expectedEvents > 0 && thisNorm*expectedEvents < pow(10.0, 18)) obsDataUnbinned->add(*mc->GetObservables(), thisNorm*expectedEvents);
    }
    //Protection against nans
    if(obsDataUnbinned->sumEntries()!=obsDataUnbinned->sumEntries()){
      exit(1);
    }
    //Adding info in the map
    asimovDataMap[std::string(channelCat->getLabel())] = obsDataUnbinned;
  }

  RooDataSet *asimovData = new RooDataSet("newasimovData",
                                          "newasimovData",
                                          RooArgSet(obsAndWeight,*channelCat),
                                          RooFit::Index(*channelCat),
                                          RooFit::Import(asimovDataMap),
                                          RooFit::WeightVar(*weightVar));
  ws -> import(*asimovData,RooFit::Rename(asimov_name.c_str()));

  TFile *f_out = TFile::Open( string_utils::replace_string(file_path,".root","_ASIMOV.root").c_str(), "RECREATE");
  ws -> Write();
  f_out -> Close();
  f_in->Close();

  return 1;
}
