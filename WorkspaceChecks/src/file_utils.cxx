#include "file_utils.h"
#include "string_utils.h"
#include "messages.h"

#include <iostream>
#include <fstream>

//______________________________________________________________________________
// Stupid utility to dump the content of a text file in a vector
std::vector < std::string > file_utils::dump_file( const std::string &file ){
  if(!string_utils::file_exists(file)){
    messages::print_error( __func__, __FILE__, __LINE__, "File " + file + " doesn't exist. Crashing.");
    abort();
  }
  std::string line;
  std::ifstream myfile ( file );
  std::vector < std::string > out_vector;
  if (myfile.is_open()){
    while ( getline (myfile,line) ){
      out_vector.push_back( line );
    }
    myfile.close();
  }
  return out_vector;
};

//______________________________________________________________________________
// Utility to dump the content of a text file in a vector skipping some lines
// and/or some characters
std::vector < std::string > file_utils::read_file( const std::string &file,
                                                  const std::vector < std::string > &skip_line_characters,
                                                  const std::vector < std::string > &skipped_characters ){
  std::vector< std::string > temp_vector = dump_file(file);
  std::vector< std::string > final_vector;
  for( const std::string &line : temp_vector ){
    //Skipping the entries with forbidden characters
    bool skip_line = false;
    for( const std::string &skip : skip_line_characters ){
      if( line.find(skip) != std::string::npos ){
        skip_line = true;
        break;
      }
    }
    if(skip_line) continue;
    //Removing the skipped characters
    std::string new_line = line;
    for( const std::string &skip : skipped_characters ){
      if( line.find(skip) != std::string::npos ){
        new_line = string_utils::replace_string( new_line, skip, "" );
      }
    }
    //skips empty lines
    if(new_line=="") continue;
    final_vector.push_back(new_line);
  }
  return final_vector;
}

//______________________________________________________________________________
// Utility to expand some loops based on text files (avoid manual copy ...)
// The structure of the lines is expected to be:
// foooooo_=expand_character= (expand_character=init,...,end)
std::vector < std::string > file_utils::read_file_and_expand( const std::string &file,
                                                              const std::vector < std::string > &skip_line_characters,
                                                              const std::vector < std::string > &skipped_characters,
                                                              const std::string &expand_character){
  std::vector< std::string > temp_vector = read_file(file, skip_line_characters, skipped_characters);
  std::vector< std::string > final_vector;
  for( const std::string &line : temp_vector ){
    //Skipping the entries with forbidden characters
    if( line.find("="+expand_character+"=") == std::string::npos ){
      //this line doesn't contain a sign to expand ... leaving the line as is
      final_vector.push_back(line);
      continue;
    }
    //Getting the range to expand
    std::string temp_line = line;
    std::string expansion = "";
    string_utils::parse_string( temp_line, expansion, "("+expand_character+"=");
    temp_line = string_utils::replace_string( temp_line, ")", "" );
    temp_line = string_utils::replace_string( temp_line, "...,", "" );
    std::string str_min(""), str_max(temp_line);
    string_utils::parse_string( str_max, str_min, ",");
    int min = atoi(str_min.c_str());
    int max = atoi(str_max.c_str());
    for( unsigned int i = min; i<=max; ++i){
      std::string temp_np = string_utils::replace_string(expansion, "="+expand_character+"=", std::to_string(i));
      final_vector.push_back(temp_np);
    }
  }
  return final_vector;
}
