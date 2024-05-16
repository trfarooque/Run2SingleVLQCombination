#ifndef WSCONFIG_H
#define WSCONFIG_H

#include <string>
#include <map>

class WSConfig {

public:
  struct Options {
    std::string file_name;
    std::string ws_name;
    std::string data_name;
    bool do_config_dump;
    bool do_trexf_dump;
    std::string input_ws_folder;
    std::string output_trexf_folder;
    std::string output_xml_folder;
    std::string output_ws_folder;
    std::string output_xml_name;
    std::string output_ws_name;
    std::string output_tag;
    std::string fittype;
    bool abort_on_error;
    bool decorr_all;
  };
  struct Channel {
    std::string channel_name;
    std::string workspace_path;
    std::string workspace_name;
    std::string np_naming_path;
  };

  WSConfig( const Options &opt );
  WSConfig( const WSConfig& );
  ~WSConfig();

  void init();
  void dump_files();

  // Function to simplify parameter names
  //std::ifstream yaml_file (const std::string &file);
  //std::map < std::string, std::string > read_mapping( const std::ifstream &yaml_file);
  std::string simplify_name( const std::string &name );

private:
  Options m_opt;
  std::map < std::string, Channel > m_channels;
};

#endif //WSCONFIG_H
