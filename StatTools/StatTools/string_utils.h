#ifndef STRING_UTILS
#define STRING_UTILS

#include <string>
#include <vector>

namespace string_utils {
  void trim_string(std::string& str, const std::string& whitespace=" \t");
  std::string::size_type parse_string(std::string& base, std::string& piece, const std::string& delim);
  bool bool_value(std::string& arg_val, bool& bin_val);
  bool bool_value(std::string& arg_val, const std::string& arg_name="");
  bool file_exists(const std::string& filename);
  std::string replace_string(const std::string& inputStr, const std::string& orig, const std::string& replacement);
  bool contains_string(const std::string& inputStr, const std::string& search);
  int count_substring(const std::string& str, const std::string& sub);
  std::vector < std::string > split_string( const std::string& str, char delimiter );
}

#endif //STRING_UTILS
