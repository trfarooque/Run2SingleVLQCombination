#include "string_utils.h"

#include <sstream>
#include <iostream>
#include <sys/stat.h>
#include <algorithm>

using namespace string_utils;

//______________________________________________________________________________
//
void string_utils::trim_string(std::string& str, const std::string& whitespace){
  const auto strBegin = str.find_first_not_of(whitespace);
  if(strBegin == std::string::npos){ str = ""; }  // no content
  else{
    const auto strEnd = str.find_last_not_of(whitespace);
    const auto strRange = strEnd - strBegin + 1;
    str = str.substr(strBegin, strRange);
  }
  return;
}

//______________________________________________________________________________
//
std::string::size_type string_utils::parse_string(std::string& base, std::string& piece, const std::string& delim){
  std::string::size_type pos = base.find(delim);
  if(pos != std::string::npos ){
    piece = base.substr(0, pos);
    base = base.substr(pos + delim.size());
  }
  else {piece = base;}
  return pos;
}

//______________________________________________________________________________
//
std::string string_utils::replace_string(const std::string& inputStr, const std::string& orig, const std::string& replacement){
  std::string newStr = inputStr;
  for( std::string::size_type  pos = 0; ; pos += replacement.length() ){
    pos = newStr.find(orig, pos);
    if(pos == std::string::npos) break;
    newStr.erase( pos, orig.length() );
    newStr.insert( pos, replacement );
  }
  return newStr;
}

//______________________________________________________________________________
//
bool string_utils::contains_string(const std::string& inputStr, const std::string& search){
  return (inputStr.find(search) != std::string::npos);
}

//______________________________________________________________________________
//
int string_utils::count_substring(const std::string& str, const std::string& sub){
  if (sub.length() == 0) return 0;
  int count = 0;
  for (size_t offset = str.find(sub); offset != std::string::npos;
  offset = str.find(sub, offset + sub.length())){ ++count; }
  return count;
}

//______________________________________________________________________________
//
std::vector < std::string > string_utils::split_string( const std::string& str, char delimiter ){
  std::istringstream ss(str);
  std::string token;
  std::vector<std::string> result;
  while(std::getline(ss, token, delimiter)) {
    if(token=="") continue;
    result.push_back(token);
  }
  return result;
}

//______________________________________________________________________________
//
bool string_utils::bool_value(std::string& arg_val, bool& bin_val){
  std::transform(arg_val.begin(), arg_val.end(), arg_val.begin(), ::toupper);
  if( arg_val.find("TRUE") != std::string::npos ){ bin_val = true; return true; }
  else if( arg_val.find("FALSE") != std::string::npos ){ bin_val = false; return true; }
  else{std::cout<<"Error : Unknown value "<<arg_val<<" for binary option "<<std::endl; return false; }
}

//______________________________________________________________________________
//
bool string_utils::bool_value(std::string& arg_val, const std::string& arg_name){
  std::transform(arg_val.begin(), arg_val.end(), arg_val.begin(), ::toupper);
  if( arg_val.find("TRUE") != std::string::npos ){ return true; }
  else if( arg_val.find("FALSE") != std::string::npos ){ return false; }
  else{std::cout<<"Error : Unknown value "<<arg_val<<" for binary option "<<arg_name<<std::endl; return false; }
}

//______________________________________________________________________________
//
bool string_utils::file_exists(const std::string& filename){
  struct stat buf;
  if (stat(filename.c_str(), &buf) != -1){ return true; }
  return false;
}
