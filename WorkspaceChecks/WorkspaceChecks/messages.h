#ifndef MESSAGES
#define MESSAGES

#include <string>

namespace messages {
  void print_error( const std::string &function, const std::string &file, const int line, const std::string &msg );
  void print_warning( const std::string &function, const std::string &file, const int line, const std::string &msg );
}

#endif //MESSAGES
