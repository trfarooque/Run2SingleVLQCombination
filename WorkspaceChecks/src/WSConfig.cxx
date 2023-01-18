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
    if(vec_chan.size()>4){
      messages::print_error( __func__, __FILE__, __LINE__, "Line: "+line+" has more than 4 entries. Skipping it.");
      continue;
    }
    Channel ch;
    ch.channel_name = string_utils::replace_string(vec_chan[0]," ","");
    ch.workspace_path = string_utils::replace_string(vec_chan[1]," ","");
    if(vec_chan.size()>=3){
      ch.workspace_name = string_utils::replace_string(vec_chan[2]," ","");
    } else {
      ch.workspace_name = m_opt.ws_name;
    }

    if(vec_chan.size()==4){
      ch.np_naming_path = string_utils::replace_string(vec_chan[3]," ","");
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
  std::ofstream o_master_trexf_file;

  if(m_opt.do_trexf_dump){
    gSystem -> mkdir( m_opt.output_trexf_folder.c_str(), true );
    o_master_trexf_file.open ( m_opt.output_trexf_folder + "/configFile_multifit_" + m_opt.output_tag + ".txt" );
    o_master_trexf_file << "Multifit: Compare_" << m_opt.output_tag << std::endl; 
    o_master_trexf_file << "Label: Compare_" << m_opt.output_tag << std::endl; 
    o_master_trexf_file << "Combine: FALSE" << std::endl;
    o_master_trexf_file << "Compare: TRUE" << std::endl;
    o_master_trexf_file << "CmeLabel: \"13 TeV\"" << std::endl;
    o_master_trexf_file << "LumiLabel: \"139 fb^{-1}\"" << std::endl;
    o_master_trexf_file << "ComparePOI: FALSE" << std::endl;
    o_master_trexf_file << "ComparePulls: TRUE" << std::endl;
    o_master_trexf_file << "CompareLimits: FALSE" << std::endl;
    o_master_trexf_file << "POIName: \"mu_signal\"" << std::endl;
    o_master_trexf_file << "DebugLevel: 2" << std::endl;
  }

  if(m_opt.do_config_dump){
    gSystem -> mkdir( m_opt.output_xml_folder.c_str(), true );
    gSystem -> mkdir( m_opt.output_ws_folder.c_str(), true );
    o_master_file.open ( m_opt.output_xml_folder + "/" + m_opt.output_xml_name );

    //Writing the header of the master file
    o_master_file << "<!DOCTYPE Combination  SYSTEM 'Combination.dtd'> " << std::endl;
    o_master_file << std::endl;
    o_master_file << "<Combination WorkspaceName=\"combWS\" " << std::endl;
    o_master_file << "   ModelConfigName=\"ModelConfig\" " << std::endl;
    o_master_file << "   DataName=\"combData\"" << std::endl;
    o_master_file << "   OutputFile=\"" + m_opt.output_ws_folder + "/" +  m_opt.output_ws_name + "\">"<< std::endl;
    o_master_file << "   <POIList Combined=\"mu_signal[1~-100,100]\"/>" << std::endl;
    o_master_file << " " << std::endl;
  }

  for( const auto &ch : m_channels ){
    const std::string channel_name = string_utils::replace_string(ch.first," ","");
    const Channel channel_info = ch.second;
    std::ofstream o_channel_file;

    if(m_opt.do_config_dump){
      //Including the channel in the master file
      o_master_file << "  <Channel Name=\"" + channel_name + "_binned\"" << std::endl;
      //o_master_file << "     InputFile=\"" + m_opt.input_ws_folder + "/" + channel_info.workspace_path + ".root\"" << std::endl;
      o_master_file << "     InputFile=\"" + channel_info.workspace_path + "\"" << std::endl;
      o_master_file << "     WorkspaceName=\"" << channel_info.workspace_name << "\"" << std::endl;
      o_master_file << "     ModelConfigName=\"ModelConfig\"" << std::endl;
      o_master_file << "     DataName=\"" << m_opt.data_name << "\">" << std::endl;
      o_master_file << "    <POIList Input=\"mu_signal\"/>" << std::endl;

      o_master_file << "    <RenameMap>" << std::endl;

      //Writting the information in the channel files
      o_channel_file.open ( m_opt.output_xml_folder + "/" + channel_name + ".xml" );

      o_channel_file << "  <Channel Name=\"" + channel_name + "_binned\">" << std::endl;
      o_channel_file << "    <File Name=\"#" + channel_name + "#\"/>" << std::endl;
      o_channel_file << "     WorkspaceName=\"" << channel_info.workspace_name << "\"" << std::endl;
      o_channel_file << "    <ModelConfig Name=\"ModelConfig\"/>" << std::endl;
      o_channel_file << "    <ModelPOI Name=\"mu_signal\"/>" << std::endl;
      o_channel_file << "    <ModelData Name=\"#DATA#\"/>" << std::endl;
      o_channel_file << "    <RenameMap>" << std::endl;
    }

    //Getting all the necessary objects
    //TFile *f = TFile::Open( (m_opt.input_ws_folder + "/" + channel_info.workspace_path +".root").c_str(), "READ" );
    TFile *f = TFile::Open(channel_info.workspace_path.c_str(), "READ" );
    RooWorkspace *ws = (RooWorkspace*)(f -> Get( channel_info.workspace_name.c_str() ));
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

    std::ofstream o_channel_trexf_file;
    if(m_opt.do_trexf_dump){
      o_channel_trexf_file.open ( m_opt.output_trexf_folder + "/configFile_" + channel_name + "_" + m_opt.output_tag + ".txt" );
      o_channel_trexf_file << "Job: " << channel_info.workspace_path << std::endl; //this job name should be the same as the name of the workspace
      o_channel_trexf_file << "Label: " << m_opt.output_tag << std::endl;
      o_channel_trexf_file << "ReadFrom: HIST" << std::endl;
      o_channel_trexf_file << "ImageFormat: png" << std::endl;
      o_channel_trexf_file << "HistoChecks: NOCRASH" << std::endl;

      //Add channel to master multifit config
      o_master_trexf_file << "Fit: \"" << channel_name << "\"" << std::endl;
      o_master_trexf_file << "ConfigFile: \"" << m_opt.output_trexf_folder + "/configFile_" + channel_name + "_" + m_opt.output_tag + ".txt" << "\"" << std::endl;
      o_master_trexf_file << "Label: \"" << channel_name << "\"" << std::endl;

    }

    TIterator* it = mc -> GetNuisanceParameters() -> createIterator();
    RooRealVar* var = NULL;
    while( (var = (RooRealVar*) it->Next()) ){
      std::string varname = (std::string) var->GetName();
      std::string repname = varname;
      if(rn_map.find(varname) != rn_map.end()){
        repname = rn_map.at(varname);
      }
      if(m_opt.do_config_dump){
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
      if(m_opt.do_trexf_dump){
	if(string_utils::contains_string(varname,"alpha_")){
	  o_channel_trexf_file << "  Systematic:    " + string_utils::replace_string(varname,"alpha_","") << std::endl;
	}
      }
    }//real var

    if(m_opt.do_config_dump){
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
    }

    if(m_opt.do_trexf_dump){
      o_channel_trexf_file.close();
    }
    f->Close();

  }//channel loop

  if(m_opt.do_config_dump){
    o_master_file << "</Combination> " << std::endl;
    o_master_file.close();
  }

}

