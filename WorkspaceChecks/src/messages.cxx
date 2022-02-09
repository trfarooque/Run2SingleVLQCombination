#include <iostream>
#include "messages.h"

//______________________________________________________________________________
//
void messages::print_error( const std::string &function, const std::string &file, const int line, const std::string &msg ){
  std::cout << "\033[41;1;37m ";
  std::cout << function << " (" << file << ", L" << line << ") :: ERROR :: ";
  std::cout << msg;
  std::cout << "\033[0m" << std::endl;
}

//______________________________________________________________________________
//
void messages::print_warning( const std::string &function, const std::string &file, const int line, const std::string &msg ){
  std::cout << "\033[43;1;37m ";
  std::cout << function << " (" << file << ", L" << line << ") :: WARNING :: ";
  std::cout << msg;
  std::cout << "\033[0m" << std::endl;
}
