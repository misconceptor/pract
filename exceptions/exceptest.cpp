#include "regexexception.hpp"
#include <iostream>
#include <regex>
using namespace std;
int main(){
  try {
    regex r("[abc){10,1}",regex_constants::grep | regex_constants::icase);
  }
  catch (const regex_error& err) {
    cerr << "error: \n"<< "what: " << err.what() << "\n"<< "code: " << regexCode(err.code()) << endl;
  }
  try {
    regex r("*",regex_constants::grep | regex_constants::icase);
  }
  catch (const regex_error& err) {
    cerr << "error: \n"<< "what: " << err.what() << "\n"<< "code: " << regexCode(err.code()) << endl;
  }
  return 0;
}
