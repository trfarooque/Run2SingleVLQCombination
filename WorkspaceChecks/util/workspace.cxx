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
  bool abort_on_error = true;
  bool decorr_all = false;
  std::string file_path = "";
  std::string workspace_name = "combined";
  std::string data_name = "obsData";
  std::string output_folder = "output/";

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
    else if(argument=="do_checks") do_checks = string_utils::bool_value(value);
    else if(argument=="do_config_dump") do_config_dump = string_utils::bool_value(value);
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
  if(workspace_name!="combined"){
    messages::print_error( __func__, __FILE__, __LINE__, "The workspace name is required to be \"combined\".");
    if(abort_on_error)abort();
  }

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

  if(do_config_dump){
    WSConfig::Options config_options;
    config_options.file_name = file_path;
    config_options.ws_name = workspace_name;
    config_options.data_name = data_name;
    config_options.abort_on_error = abort_on_error;
    config_options.output_folder = output_folder;
    config_options.decorr_all = decorr_all;
    WSConfig config( config_options );
    config.init();
    config.dump_files();
    return 1;
  }
  return 1;
}
