#ifndef FILE_UTILS_H
#define FILE_UTILS_H

#include <vector>
#include <string>

namespace file_utils {
  std::vector < std::string > dump_file( const std::string &file );
  std::vector < std::string > read_file( const std::string &file, const std::vector < std::string > &skip_line_characters,
                                          const std::vector < std::string > &skipped_characters);
  std::vector < std::string > read_file_and_expand( const std::string &file, const std::vector < std::string > &skip_line_characters,
                                          const std::vector < std::string > &skipped_characters,
                                          const std::string &expand_character);
};

#endif //FILE_UTILS_H
