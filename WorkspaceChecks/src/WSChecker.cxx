#include "WSChecker.h"
#include "messages.h"
#include "file_utils.h"
#include "string_utils.h"

#include "TFile.h"
#include "TEnv.h"
#include "TRegexp.h"
#include "RooSimultaneous.h"
#include "RooCategory.h"
#include "RooCatType.h"
#include "RooRealVar.h"
#include "RooRealSumPdf.h"
#include "RooProduct.h"

#include <iostream>

//______________________________________________________________________________
//
WSChecker::WSChecker( const Options &opt ):
m_opt(opt),
m_ws(0),
m_mc(0),
m_data(0)
{}

//______________________________________________________________________________
//
WSChecker::WSChecker( const WSChecker& ){}

//______________________________________________________________________________
//
WSChecker::~WSChecker(){

}

//______________________________________________________________________________
//
void WSChecker::init(){
  //
  // Getting all RooFit/RooStats objects
  //
  TFile *f = TFile::Open( m_opt.file_name.c_str(), "READ" );
  m_ws = (RooWorkspace*)(f -> Get( m_opt.ws_name.c_str() ));
  if(!m_ws){
    messages::print_error( __func__, __FILE__, __LINE__, "No workspace found in file ! Aborting !");
    abort();
  }
  m_mc = (RooStats::ModelConfig*)m_ws -> obj("ModelConfig");
  if(!m_mc){
    messages::print_error( __func__, __FILE__, __LINE__, "No ModelConfig object found in workspace ! Aborting !");
    abort();
  }
  m_data = m_ws -> data( m_opt.data_name.c_str() );
  if(!m_data){
    messages::print_error( __func__, __FILE__, __LINE__, "No "+m_opt.data_name+" object found in workspace ! Aborting !");
    abort();
  }
  //
  // Getting all analyses
  //
  m_analyses = file_utils::read_file("data/NAMING_analyses.dat",
                                      {}/*characters that make skipped lines*/,
                                      {}/*ignored characters*/);
  //
  // Getting all nuisance parameters
  //
  m_nps = file_utils::read_file_and_expand("data/NAMING_NPs.dat",
                                            {"*"}/*characters that make skipped lines*/,
                                            {"|"," "}/*ignored characters*/,
                                            "index"/*expansion key*/);
  //
  // Getting all backgrounds
  //
  std::vector < std::string > temps_backs = file_utils::read_file("data/NAMING_backs.dat",
                                                                  {"*"}/*characters that make skipped lines*/,
                                                                  {"|"}/*ignored characters*/);
  for( const std::string &back : temps_backs ){
    std::vector < std::string > vec_back = string_utils::split_string( back, ' ' );
    if(vec_back.size()==2){
      m_backs.push_back(vec_back[1]);
    }
  }
  //
  // Getting the templates
  //
  TEnv rEnv;
  rEnv.ReadFile( "data/NAMING_other_conventions.dat", kEnvAll);
  for( const std::string &name : {"Back.NP","Back.Norm","Param.Default","Region.Name","POI.Name"}){
    m_templates.insert( std::pair < std::string, std::string >( name, rEnv.GetValue(name.c_str(), "") ) );
  }
}

//______________________________________________________________________________
//
bool WSChecker::perform_checks(){
  bool ok = true;
  if(!check_regions()){
    if(m_opt.abort_on_error) abort();
    else ok = false;
  }
  if(!check_parameters()){
    if(m_opt.abort_on_error) abort();
    else ok = false;
  }
  if(!check_poi()){
    if(m_opt.abort_on_error) abort();
    else ok = false;
  }
  if(!check_sample_names()){
    if(m_opt.abort_on_error) abort();
    else ok = false;
  }
  return ok;
}

//______________________________________________________________________________
// Checking if the region naming follows the convention
bool WSChecker::check_regions(){
  RooSimultaneous *simPdf = (RooSimultaneous*)(m_mc->GetPdf());
  RooCategory* channelCat = (RooCategory*) (&simPdf->indexCat());
  TIterator* iter = channelCat->typeIterator() ;
  RooCatType* tt = nullptr;
  while( (tt=(RooCatType*) iter->Next()) ){
    bool isOK = false;
    for( const auto &analysis : m_analyses ){
      if(((TString)tt->GetName()).BeginsWith(analysis.c_str())){
        isOK = true; break;
      }
    }
    if(!isOK){
      messages::print_error( __func__, __FILE__, __LINE__, "Region " + (std::string)tt->GetName() + " doesn't follow the standard.");
      if(m_opt.abort_on_error) return false;
    }
  }
  return true;
}

//______________________________________________________________________________
//
bool WSChecker::check_parameters(){
  std::set < std::string > parameter_lists;
  TIterator* it = m_mc -> GetNuisanceParameters() -> createIterator();
  RooRealVar* var = NULL;
  while( (var = (RooRealVar*) it->Next()) ){
    std::string varname = (std::string) var->GetName();
    //std::cout<< varname << std::endl;
    varname = string_utils::replace_string( varname, "alpha_", "" );
    if ( varname.find("gamma_stat") != std::string::npos ){
      continue;
    }
    if ( varname.find("gamma_shape_stat") != std::string::npos ){
      continue;
    }
    bool isOK = false;
    // First checking if the NP is part of the object NP list
    for( const std::string &np : m_nps ){
      if(np==varname){
        isOK = true; break;
      }
    }
    // If this is not part of the previous list, check if this follows
    // the background modeling NP/NF convention
    std::vector < std::string > vec_keys;
    // if(var->getVal() == 0){
    //   // NP
    //   vec_keys.push_back("Back.NP");
    // } else if(var->getVal() == 1){
    //   // NF
    //   vec_keys.push_back("Back.Norm");
    // }
    // If this is still not ok, checking the format of the default uncorelated
    // nuisance parameter
    vec_keys.push_back("Back.NP");
    vec_keys.push_back("Back.NF");
    vec_keys.push_back("Param.Default");
    // vec_keys.push_back("Sig.NF");
    for ( const std::string &key : vec_keys ){
      for( const std::string &ana : m_analyses ){
        //for ( const std::string &back : m_backs ){
          std::string temp = string_utils::replace_string(m_templates[key],"CODE",ana);
          // temp = string_utils::replace_string(temp,"NAME",back);
          temp = string_utils::replace_string(temp,"explicit_name","");
          if( varname.find(temp) == 0 ){
            isOK = true; break;
          }
	  //}
	  //if(isOK) break;
      }
      if(isOK) break;
    }
    // if still not okay, check if it is a signal mu
    if(!isOK){
      if(((TString)varname).Contains((TRegexp)"mu_[WZ][TB][WZH][tb]"))
	isOK = true;
    }
    if(!isOK){
      messages::print_error( __func__, __FILE__, __LINE__, "Variable " + (std::string)varname + " doesn't follow the standard.");
      if(m_opt.abort_on_error) return false;
    }
  }
  return true;
}

//______________________________________________________________________________
// Checking if the POI naming follows the convention
bool WSChecker::check_poi(){
  RooRealVar * firstPOI = dynamic_cast<RooRealVar*>(m_mc->GetParametersOfInterest()->first());
  TString poi_name = firstPOI->GetName();
  bool isOK = false;
  if(((std::string)poi_name)==m_templates["POI.Name"]){
    isOK = true;
  }
  
  if(!isOK){
    if(((TString)poi_name).Contains((TRegexp)"mu_[WZ][TB][WZH][tb]")){
      isOK = true;
      messages::print_warning( __func__, __FILE__, __LINE__, "POI " + (std::string)poi_name + " is not 'mu_signal'. Make Sure this is not a post-combination WS");
    }
  }

  if(!isOK){
    messages::print_error( __func__, __FILE__, __LINE__, "POI " + (std::string)poi_name + " doesn't follow the standard.");
    if(m_opt.abort_on_error) return false;
  }
  return isOK;
}

//______________________________________________________________________________
// Checking if the sample naming follows the convention
bool WSChecker::check_sample_names(){

  //
  // Getting the names of the samples in the workspace
  //
  std::set < std::string > set_samples;

  RooSimultaneous *simPdf = (RooSimultaneous*)(m_mc->GetPdf());
  RooCategory* channelCat = (RooCategory*) (&simPdf->indexCat());
  TString chanName = channelCat -> GetName();
  TIterator *iter = channelCat->typeIterator() ;
  RooCatType *tt  = NULL;
  std::string sigex("[WZ][TB][WZH][tb]-M[0-9][0-9]K[0-9][0-9][0-9]");

  while((tt=(RooCatType*) iter->Next()) ){

    TString chanName(tt->GetName());
    auto *pdftmp  = simPdf -> getPdf( chanName );

    TString modelName1(chanName);
    modelName1.Append("_model");
    RooRealSumPdf *pdfmodel1 = (RooRealSumPdf*) (pdftmp->getComponents())->find(modelName1);
    RooArgList funcList1 =  pdfmodel1->funcList();
    RooLinkedListIter funcIter1 = funcList1.iterator() ;
    RooProduct* comp1 = 0;

    while( (comp1 = (RooProduct*) funcIter1.Next()) ) {
      TString compname(comp1->GetName());
      // std::cout<<compname<<std::endl;
      compname.ReplaceAll("L_x_","").ReplaceAll(tt->GetName(),"").ReplaceAll("_overallSyst_x_StatUncert","");
      compname.ReplaceAll("_overallSyst_x_HistSyst","").ReplaceAll("_overallSyst_x_Exp","").ReplaceAll("_","");
      if(compname.Contains((TRegexp)sigex))
	compname = compname(compname.Index((TRegexp)sigex), 12);
      set_samples.insert( (std::string) compname );
    }
  }

  //
  // Comparing with the allowed sample names
  //
  bool isOK = true;
  for ( const std::string &contained : set_samples ){
    bool is_allowed = false;
    //std::cout << contained << std::endl;
    for ( const std::string &allowed : m_backs ){
      if( allowed==contained ){
        is_allowed = true;
        break;
      }
    }
    // Check if it is a signal
    if(!is_allowed){
      if(((TString)contained).Contains((TRegexp)sigex))
	 is_allowed = true;
    }
    if(!is_allowed){
      isOK = false;
      messages::print_error( __func__, __FILE__, __LINE__, "Sample: " + contained + " doesn't follow the standard.");
    }
  } 
  if(!isOK){
    messages::print_error( __func__, __FILE__, __LINE__, "==> Error found in the sample names. Please check.");
    if(m_opt.abort_on_error) abort();
  } 
  return isOK;
}
