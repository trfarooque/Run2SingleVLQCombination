#ifndef WSCHECKER_H
#define WSCHECKER_H

#include <string>
#include <vector>
#include <map>

#include "RooWorkspace.h"
#include "RooAbsData.h"
#include "RooStats/ModelConfig.h"

class WSChecker {

public:
  struct Options {
    std::string file_name;
    std::string ws_name;
    std::string data_name;
    bool abort_on_error;
  };

  WSChecker( const Options &opt );
  WSChecker( const WSChecker& );
  ~WSChecker();

  void init();
  bool perform_checks();
  bool check_regions();
  bool check_parameters();
  bool check_poi();
  bool check_sample_names();

private:
  Options m_opt;
  RooWorkspace* m_ws;
  RooStats::ModelConfig* m_mc;
  RooAbsData* m_data;
  std::vector < std::string > m_analyses;
  std::vector < std::string > m_nps;
  std::vector < std::string > m_backs;
  std::map < std::string, std::string > m_templates;
};

#endif //WSCHECKER_H
