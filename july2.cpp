#include <iostream>
#include <regex>
#include <string>
using namespace std;
int main() {
    regex r1("(.|\n)*let(.|\n)*");
    string s= R"(sdfsdf
    sfsdfletsdf
    sdfsdf)";
    bool b = regex_match(s, r1);
    cout<<b<<endl;

    //regex rg1(".*let.*");
    regex rg1(R"([\s\S]*let[\s\S]*)");
    string data = R"(sdfsdf
    sfsdfletsdf
    sdfsdf)";
    bool b = regex_match(data, rg1);
    cout << "found = " << b << endl;
    return 0;
}