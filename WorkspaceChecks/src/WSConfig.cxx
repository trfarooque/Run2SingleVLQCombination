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
#include <map>

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

std::string WSConfig::simplify_name( const std::string &name ){
  std::string simplified_name = name;

    // Simplify NP names
    simplified_name = string_utils::replace_string(simplified_name,"SPT_MONOTOP_BKGNP_VJETS_weight_muR05_muF05_to_muR2_muF2_WJETS","MONO_VJETS_weight_muRmuF_WJETS");
    simplified_name = string_utils::replace_string(simplified_name,"SPT_MONOTOP_BKGNP_VJETS_weight_muR05_muF05_to_muR2_muF2_ZJETS","MONO_VJETS_weight_muRmuF_ZJETS");
    simplified_name = string_utils::replace_string(simplified_name,"SPT_MONOTOP_BKGNP_VV_weight_muR05_muF05_to_muR2_muF2","MONO_VV_weight_muRmuF");

    // Simplify NFs names
    simplified_name = string_utils::replace_string(simplified_name,"SPT_MONOTOP_BKGNF_TTBAR","MONO_ttbar");
    simplified_name = string_utils::replace_string(simplified_name,"SPT_MONOTOP_BKGNF_VJETS","MONO_Vjets");
    simplified_name = string_utils::replace_string(simplified_name,"SPT_OSML_BKGNF_2l_z_hf","OSML_2lZhf");
    simplified_name = string_utils::replace_string(simplified_name,"SPT_OSML_BKGNF_2l_z_lf","OSML_2lZlf");
    simplified_name = string_utils::replace_string(simplified_name,"SPT_OSML_BKGNF_3l_mu_VV","OSML_3lVV");
    simplified_name = string_utils::replace_string(simplified_name,"SPT_OSML_BKGNF_3l_mu_ttV","OSML_3lttV");

    // Simplify channel names
    simplified_name = string_utils::replace_string(simplified_name,"SPT_MONOTOP","MONO");
    simplified_name = string_utils::replace_string(simplified_name,"SPT_HTZT","HTZT");
    simplified_name = string_utils::replace_string(simplified_name,"SPT_OSML","OSML");
    simplified_name = string_utils::replace_string(simplified_name,"SPT_COMBINED","COMB");

    // Simplify general strings
    simplified_name = string_utils::replace_string(simplified_name,"BKGNF_","");
    simplified_name = string_utils::replace_string(simplified_name,"BKGNP_","");

  return simplified_name;
}

// Funciton to change name of JER systematics. Arguments: name and channel name
std::string WSConfig::change_JER_name( const std::string &name, const std::string &channel_name ){
  std::string new_name = name;

  // If channel is SPT_MONOTOP, JET_JER --> JET_FullJER
  // If other channel, JET_JER --> JET_simpleJER
  if(string_utils::contains_string(channel_name,"SPT_MONOTOP")){
    new_name = string_utils::replace_string(new_name,"JET_JER_EffectiveNP","JET_FullJER_EffectiveNP");
    new_name = string_utils::replace_string(new_name,"JET_JER_DataVsMC_MC16","JET_FullJER_DataVsMC_MC16");
  } else {
    new_name = string_utils::replace_string(new_name,"JET_JER_EffectiveNP","JET_SimpleJER_EffectiveNP");
    new_name = string_utils::replace_string(new_name,"JET_JER_DataVsMC_MC16","JET_SimpleJER_DataVsMC_MC16");
  }

  return new_name;
}

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
    o_master_trexf_file << "MultiFit: Compare_" << m_opt.output_tag << std::endl; 
    o_master_trexf_file << "Label: Compare_" << m_opt.output_tag << std::endl; 
    o_master_trexf_file << "Combine: FALSE" << std::endl;
    o_master_trexf_file << "Compare: TRUE" << std::endl;
    o_master_trexf_file << "CmeLabel: \"13 TeV\"" << std::endl;
    o_master_trexf_file << "LumiLabel: \"139 fb^{-1}\"" << std::endl;
    if(std::strcmp(m_opt.fittype.c_str(), "BONLY") == 0)
      o_master_trexf_file << "ComparePOI: FALSE" << std::endl;
    else
      o_master_trexf_file << "ComparePOI: TRUE" << std::endl;
    o_master_trexf_file << "ComparePulls: TRUE" << std::endl;
    o_master_trexf_file << "CompareLimits: FALSE" << std::endl;
    o_master_trexf_file << "POIName: \"mu_signal\"" << std::endl;
    o_master_trexf_file << "PlotCombCorrMatrix: TRUE" << std::endl;
    o_master_trexf_file << "DebugLevel: 2" << std::endl;
    o_master_trexf_file << "NPCategories: Jets,Electrons,Muons,b_tagging,SPT_ALLHAD_BKGNP,SPT_OSML_BKGNP,SPT_HTZT_BKGNP,SPT_TYWB_BKGNP,SPT_MONOTOP_BKGNP,Bkgd_norm,Others"<<std::endl;
    o_master_trexf_file << std::endl;
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
    RooAbsData *data;
    if((std::strcmp(channel_name.c_str(), "SPT_COMBINED") == 0) && (m_opt.data_name.find("asimov") == std::string::npos))
      data = ws -> data( "combData" );
    else
      data = ws -> data( m_opt.data_name.c_str() );
    if(!data){
      messages::print_error( __func__, __FILE__, __LINE__, "No "+m_opt.data_name+" (or combData)  object found in workspace ! Aborting !");
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
      std::vector < std::string > vec_path = string_utils::split_string( channel_info.workspace_path, '/' );
      //o_channel_trexf_file << "Job: " << channel_info.workspace_path << std::endl; //this job name should be the same as the name of the workspace
      o_channel_trexf_file << "Job: " << string_utils::replace_string(vec_path[vec_path.size() - 1], ".root", "") + "_" + m_opt.fittype << std::endl; //this job name should be the same as the name of the workspace
      o_channel_trexf_file << "Label: " << m_opt.output_tag << std::endl;
      o_channel_trexf_file << "ReadFrom: HIST" << std::endl;
      o_channel_trexf_file << "ImageFormat: png" << std::endl;
      o_channel_trexf_file << "HistoChecks: NOCRASH" << std::endl;
      o_channel_trexf_file << std::endl;

      //Add channel to master multifit config
      o_master_trexf_file << "Fit: \"" << channel_name << "\"" << std::endl;
      o_master_trexf_file << "ConfigFile: \"" << m_opt.output_trexf_folder + "/configFile_" + channel_name + "_" + m_opt.output_tag + ".txt" << "\"" << std::endl;

      // Simplify channel name 
      std::string simplified_channel_name = WSConfig::simplify_name(channel_name);
      o_master_trexf_file << "Label: \"" << simplified_channel_name << "\"" << std::endl;
      o_master_trexf_file << std::endl;

    }

    TIterator* it = mc -> GetNuisanceParameters() -> createIterator();
    RooRealVar* var = NULL;
    while( (var = (RooRealVar*) it->Next()) ){
      std::string varname = (std::string) var->GetName();
      std::string repname = varname;
      
      if(rn_map.find(varname) != rn_map.end()){
        messages::print_warning( __func__, __FILE__, __LINE__, "Found "+varname+" in the rename map. Replacing it with "+rn_map.at(varname));
        repname = rn_map.at(varname);
      }
      // Change names for JET JER systematics
      repname = WSConfig::change_JER_name(repname, channel_name);
      
      if(m_opt.do_config_dump){

	std::string oldname = "";
	if(string_utils::contains_string(varname,"alpha_")){
	  oldname = varname+"Constraint("+varname+", nom_"+varname+")";
	}
	else{ 
	  oldname = varname; 
	}

	//Master
	o_master_file << "      <Syst OldName = \"" + oldname;
	if(m_opt.decorr_all){
	  o_master_file << "\"     NewName =       \"" + channel_name << "_" << varname;
	} else {
	  o_master_file << "\"     NewName =       \"" + repname; 
	}
	o_master_file << "\" />" << std::endl;

	//Channel
	o_channel_file << "      <Syst OldName = \"" + oldname;
	if(m_opt.decorr_all){
	  o_channel_file << "\"     NewName =       \"" + channel_name << "_" << varname;
	} else {
	  o_channel_file << "\"     NewName =       \"" + repname;        
	}
	o_channel_file << "\" />" << std::endl;

      }
      if(m_opt.do_trexf_dump){
	if(string_utils::contains_string(varname,"alpha_")){
	  std::string varname_NP = string_utils::replace_string(varname,"alpha_","");

    o_channel_trexf_file << "  Systematic:    " + varname_NP << std::endl;
    
    // Simplify NPs name for title in the plots
    std::string simplified_varname_NP = WSConfig::simplify_name(varname_NP);

    // If simplified name is different from the original name, add the original name to the title
    if(simplified_varname_NP != varname_NP){
      o_channel_trexf_file << "  Title:         " + simplified_varname_NP << std::endl;
    }

  	  if(string_utils::contains_string(varname_NP,"JET_") || string_utils::contains_string(varname_NP,"COMB_")){
	    o_channel_trexf_file << "  Category: Jets" << std::endl;
	  }
  	  else if(string_utils::contains_string(varname_NP,"EL_") || string_utils::contains_string(varname_NP,"EG_")){
	    o_channel_trexf_file << "  Category: Electrons" << std::endl;
	  }
  	  else if(string_utils::contains_string(varname_NP,"MU_") || string_utils::contains_string(varname_NP,"MUON_")){
	    o_channel_trexf_file << "  Category: Muons" << std::endl;
	  }
  	  else if(string_utils::contains_string(varname_NP,"FT_EFF_")){
	    o_channel_trexf_file << "  Category: b_tagging" << std::endl;
	  }
  	  else if(string_utils::contains_string(varname_NP,"BKGNP_")){

	    if(string_utils::contains_string(varname_NP,"SPT_ALLHAD")){
	      o_channel_trexf_file << "  Category: SPT_ALLHAD_BKGNP" << std::endl;
	    }
	    else if(string_utils::contains_string(varname_NP,"SPT_OSML")){
	      o_channel_trexf_file << "  Category: SPT_OSML_BKGNP" << std::endl;
	    }
	    if(string_utils::contains_string(varname_NP,"SPT_HTZT")){
	      o_channel_trexf_file << "  Category: SPT_HTZT_BKGNP" << std::endl;
	    }
	    if(string_utils::contains_string(varname_NP,"SPT_TYWB")){
	      o_channel_trexf_file << "  Category: SPT_TYWB_BKGNP" << std::endl;
	    }
	    if(string_utils::contains_string(varname_NP,"SPT_MONOTOP")){
	      o_channel_trexf_file << "  Category: SPT_MONOTOP_BKGNP" << std::endl;
	    }

	  }//Channel-specific
	  else{
	    o_channel_trexf_file << "  Category: Others" << std::endl;
	  }

	}//Nuisance parameters
	else if(string_utils::contains_string(varname,"BKGNF_")){
	  o_channel_trexf_file << "  NormFactor:    " + varname << std::endl;

    // Simplify NFs name for title in the plots
    std::string simplified_varname = WSConfig::simplify_name(varname);
    o_channel_trexf_file << "  Title:         " + simplified_varname << std::endl;
	}//Background norm factors

	o_channel_trexf_file << std::endl;

      }//trex dump

    }//real var

    if(m_opt.do_config_dump){
      RooAbsCategoryLValue* cat = ( RooAbsCategoryLValue* ) &simPdf->indexCat();
      std::string catName = (std::string)cat->GetName();
      messages::print_warning( __func__, __FILE__, __LINE__, "catName: "+catName);
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

