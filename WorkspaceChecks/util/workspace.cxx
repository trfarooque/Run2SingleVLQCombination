#include <iostream>
#include <string>

#include "string_utils.h"
#include "messages.h"
#include "WSChecker.h"
#include "WSConfig.h"

int main( int argc, char **argv ){

  //
  // Getting default values for the parameters
  //
  bool do_checks = false;
  bool do_config_dump = false;
  bool do_trexf_dump = false;
  bool abort_on_error = true;
  bool decorr_all = false;
  std::string file_path = "";
  std::string workspace_name = "combined";
  std::string data_name = "obsData";
  std::string input_ws_folder = "";
  std::string output_trexf_folder = "data/trexf/";
  std::string output_xml_folder = "data/xml/combination/";
  std::string output_ws_folder = "data/workspaces/combination/";
  std::string output_xml_name = "combination.xml";
  std::string output_ws_name = "combined.root";
  std::string output_tag = "";

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
    else if(argument=="input_ws_folder") input_ws_folder = value;
    else if(argument=="output_trexf_folder") output_trexf_folder = value;
    else if(argument=="output_xml_folder") output_xml_folder = value;
    else if(argument=="output_ws_folder") output_ws_folder = value;
    else if(argument=="output_xml_name") output_xml_name = value;
    else if(argument=="output_ws_name") output_ws_name = value;
    else if(argument=="output_tag") output_tag = value;
    else if(argument=="do_checks") do_checks = string_utils::bool_value(value);
    else if(argument=="do_config_dump") do_config_dump = string_utils::bool_value(value);
    else if(argument=="do_trexf_dump") do_trexf_dump = string_utils::bool_value(value);
    else if(argument=="abort_on_error") abort_on_error = string_utils::bool_value(value);
    else if(argument=="decorr_all") decorr_all = string_utils::bool_value(value);
    else {
      std::cout << "Argument *" << argument;
      std::cout << "* is unknown. Only file_path, workspace_name and do_checks ";
      std::cout << "are supported. Aborting !" << std::endl;
      abort();
    }
  }

  //
  // Basic checks !
  //
  if(!string_utils::file_exists(file_path)){
    messages::print_error( __func__, __FILE__, __LINE__, "The file doesn't seem to exist. Please check.");
    abort();
  }
  //if(workspace_name!="combined"){
  //  messages::print_error( __func__, __FILE__, __LINE__, "The workspace name is required to be \"combined\".");
  //  if(abort_on_error)abort();
  //}

  if(do_checks){
    WSChecker::Options checker_options;
    checker_options.file_name = file_path;
    checker_options.ws_name = workspace_name;
    checker_options.data_name = data_name;
    checker_options.abort_on_error = abort_on_error;
    WSChecker checker( checker_options );
    checker.init();
    const bool ok = checker.perform_checks();
    if(ok){
      std::cout << "\033[42;1;37m==> Checks on your workspaces look OK !\033[0m" << std::endl;
      return 0;
    }
    return 1;
  }

  if(do_config_dump || do_trexf_dump){
    WSConfig::Options config_options;
    config_options.file_name = file_path;
    config_options.ws_name = workspace_name;
    config_options.data_name = data_name;
    config_options.abort_on_error = abort_on_error;
    config_options.do_config_dump = do_config_dump;
    config_options.do_trexf_dump = do_trexf_dump;
    config_options.input_ws_folder = input_ws_folder;
    config_options.output_trexf_folder = output_trexf_folder;
    config_options.output_xml_folder = output_xml_folder;
    config_options.output_ws_folder = output_ws_folder;
    config_options.output_xml_name = output_xml_name;
    config_options.output_ws_name = output_ws_name;
    config_options.output_tag = output_tag;
    config_options.decorr_all = decorr_all;
    WSConfig config( config_options );
    config.init();
    config.dump_files();
    return 0;
  }
  return 0;
}
