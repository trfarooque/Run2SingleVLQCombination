#include "WSConfig.h"
#include "messages.h"
#include "file_utils.h"
#include "string_utils.h"

#include "TSystem.h"
#include "RooSimultaneous.h"
#include "RooCategory.h"
#include "RooCatType.h"
#include "RooRealVar.h"
#include "TFile.h"
#include "RooWorkspace.h"
#include "RooAbsData.h"
#include "RooStats/ModelConfig.h"

#include <fstream>
#include <iostream>

//______________________________________________________________________________
//
WSConfig::WSConfig( const Options &opt ):
m_opt(opt)
{}

//______________________________________________________________________________
//
WSConfig::WSConfig( const WSConfig& ){}

//______________________________________________________________________________
//
WSConfig::~WSConfig(){}

//______________________________________________________________________________
//
void WSConfig::init(){

  //Getting the list of channels and of files to get 
  std::vector < std::string > file_content = file_utils::read_file( m_opt.file_name,
                                      {}/*characters that make skipped lines*/,
                                      {}/*ignored characters*/);
  for( const std::string &line : file_content ){
    std::vector < std::string > vec_chan = string_utils::split_string( line, ':' );
    if(vec_chan.size()<2){
      messages::print_error( __func__, __FILE__, __LINE__, "Line: "+line+" has less than two entries. Skipping it.");
      continue;
    }
    if(vec_chan.size()>3){
      messages::print_error( __func__, __FILE__, __LINE__, "Line: "+line+" has more than 3 entries. Skipping it.");
      continue;
    }
    Channel ch;
    ch.channel_name = string_utils::replace_string(vec_chan[0]," ","");
    ch.workspace_path = string_utils::replace_string(vec_chan[1]," ","");
    if(vec_chan.size()==3){
      ch.np_naming_path = string_utils::replace_string(vec_chan[2]," ","");
    } else {
      ch.np_naming_path = "";
    }
    m_channels.insert( std::pair < std::string, Channel >( vec_chan[0], ch) );
  }

}

//______________________________________________________________________________
//
void WSConfig::dump_files(){
  //Master file (contains all)
  std::ofstream o_master_file;
  gSystem -> mkdir( m_opt.output_folder.c_str(), true );
  o_master_file.open ( m_opt.output_folder + "/combination.xml" );

  //Writing the header of the master file
  o_master_file << "<!DOCTYPE Combination  SYSTEM 'Combination.dtd'> " << std::endl;
  o_master_file << std::endl;
  o_master_file << "<Combination> " << std::endl;
  o_master_file << "  <Channel Name=\"combined\" IsCombined=\"true\" Mass=\"125.09\"> " << std::endl;
  o_master_file << "    <File Name=\"./combined.root\"/> " << std::endl;
  o_master_file << "    <Workspace Name=\"combWS\"/>" << std::endl;
  o_master_file << "    <ModelConfig  Name=\"ModelConfig\"/>" << std::endl;
  o_master_file << "    <ModelData Name=\"combData\"/>" << std::endl;
  o_master_file << "    <ModelPOI Name=\"mu_signal\"/>" << std::endl;
  o_master_file << "  </Channel>" << std::endl;
  o_master_file << " " << std::endl;

  for( const auto &ch : m_channels ){
    const std::string channel_name = string_utils::replace_string(ch.first," ","");
    const Channel channel_info = ch.second;

    std::ofstream o_channel_file;
    o_channel_file.open ( m_opt.output_folder + "/" + channel_name + ".xml" );

    //Including the channel in the master file
    o_master_file << "  <Channel Name=\"" + channel_name + "_binned\">" << std::endl;
    o_master_file << "    <File Name=\"" + channel_info.workspace_path + "\"/>" << std::endl;
    o_master_file << "    <Workspace Name=\"combined\"/>" << std::endl;
    o_master_file << "    <ModelConfig Name=\"ModelConfig\"/>" << std::endl;
    o_master_file << "    <ModelPOI Name=\"mu_signal\"/>" << std::endl;
    o_master_file << "    <ModelData Name=\"" << m_opt.data_name << "\"/>" << std::endl;
    o_master_file << "    <RenameMap>" << std::endl;

    //Writting the information in the channel files
    o_channel_file << "  <Channel Name=\"" + channel_name + "_binned\">" << std::endl;
    o_channel_file << "    <File Name=\"#" + channel_name + "#\"/>" << std::endl;
    o_channel_file << "    <Workspace Name=\"combined\"/>" << std::endl;
    o_channel_file << "    <ModelConfig Name=\"ModelConfig\"/>" << std::endl;
    o_channel_file << "    <ModelPOI Name=\"mu_signal\"/>" << std::endl;
    o_channel_file << "    <ModelData Name=\"#DATA#\"/>" << std::endl;
    o_channel_file << "    <RenameMap>" << std::endl;

    //Getting all the necessary objects
    TFile *f = TFile::Open( channel_info.workspace_path.c_str(), "READ" );
    RooWorkspace *ws = (RooWorkspace*)(f -> Get( m_opt.ws_name.c_str() ));
    if(!ws){
      messages::print_error( __func__, __FILE__, __LINE__, "No workspace found in file ! Aborting !");
      abort();
    }
    RooStats::ModelConfig *mc = (RooStats::ModelConfig*)ws -> obj("ModelConfig");
    if(!mc){
      messages::print_error( __func__, __FILE__, __LINE__, "No ModelConfig object found in workspace ! Aborting !");
      abort();
    }
    RooAbsData *data = ws -> data( m_opt.data_name.c_str() );
    if(!data){
      messages::print_error( __func__, __FILE__, __LINE__, "No "+m_opt.data_name+" object found in workspace ! Aborting !");
      abort();
    }
    RooSimultaneous *simPdf = (RooSimultaneous*)(mc->GetPdf());
    if(!simPdf){
      messages::print_error( __func__, __FILE__, __LINE__, "Problem retrieving RooSimultaneous object ! Aborting !");
      abort();
    }
    //Getting the rename map if needed 
    std::map < std::string, std::string > rn_map;
    if(ch.second.np_naming_path!=""){
      std::vector < std::string > rn_map_file_content;
      for( const std::string &file_name : string_utils::split_string( ch.second.np_naming_path, ',' ) ){
        rn_map_file_content = file_utils::read_file( ch.second.np_naming_path,
                                        {}/*characters that make skipped lines*/,
                                        {}/*ignored characters*/);
        for( const std::string &line : rn_map_file_content ){
          std::vector < std::string > vec_np = string_utils::split_string( line, ':' );
          if(vec_np.size()==0){
            messages::print_warning( __func__, __FILE__, __LINE__, "Could not find the separator ':' in a line of the NP map file ('"+ch.second.np_naming_path+"') ... Please check.)");
            continue;
          } else if (vec_np.size()!=2){
            messages::print_warning( __func__, __FILE__, __LINE__, "Found more than two ':' in a line of the NP map file ('"+ch.second.np_naming_path+"') ... Please check.)");
            continue;          
          } else {
            rn_map.insert( std::pair < std::string, std::string > ( string_utils::replace_string(vec_np[0]," ",""), string_utils::replace_string(vec_np[1]," ","") ) );
          }
        }
      }
    }


    TIterator* it = mc -> GetNuisanceParameters() -> createIterator();
    RooRealVar* var = NULL;
    while( (var = (RooRealVar*) it->Next()) ){
      std::string varname = (std::string) var->GetName();
      std::string repname = varname;
      if(rn_map.find(varname) != rn_map.end()){
        repname = rn_map.at(varname);
      }
      //Master
      o_master_file << "      <Syst OldName = \"" + varname;
      if(m_opt.decorr_all){
        o_master_file << "\"     NewName =       \"" + channel_name << "_" << varname;
      } else {
        o_master_file << "\"     NewName =       \"" + repname; 
      }
      o_master_file << "\" />" << std::endl;

      //Channel
      o_channel_file << "      <Syst OldName = \"" + varname;
      if(m_opt.decorr_all){
        o_channel_file << "\"     NewName =       \"" + channel_name << "_" << varname;
      } else {
        o_channel_file << "\"     NewName =       \"" + repname;        
      }
      o_channel_file << "\" />" << std::endl;
    }

    RooAbsCategoryLValue* cat = ( RooAbsCategoryLValue* ) &simPdf->indexCat();
    std::string catName = (std::string)cat->GetName();
    //Master
    o_master_file << "      <Syst OldName = \"" + catName;
    o_master_file << "\"     NewName =       \"" + channel_name + "_" + catName;
    o_master_file << "\" />" << std::endl;
    o_master_file << "    </RenameMap>" << std::endl;
    o_master_file << "  </Channel>" << std::endl;
    //Channel
    o_channel_file << "      <Syst OldName = \"" + catName;
    o_channel_file << "\"     NewName =       \"" + channel_name + "_" + catName;
    o_channel_file << "\" />" << std::endl;
    o_channel_file << "    </RenameMap>" << std::endl;
    o_channel_file << "  </Channel>" << std::endl;
    o_channel_file.close();

    f->Close();
  }
  o_master_file << "</Combination> " << std::endl;
  o_master_file.close();
}
