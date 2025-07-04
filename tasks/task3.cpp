#include <iostream>
#include <regex>
#include <string>
using namespace std;

int main(){
    // regex r(R"(ab*a)");
    // string s="abbbba aa abu abbbu";
    // auto b=sregex_iterator(s.begin(),s.end(),r);
    // auto e=sregex_iterator();
    // for(auto i=b; i!=e;++i){
    //     cout<<i->str()<<' ';
    // }
    // cout<<endl;
	string s1="text summer some text average some text temperature +47 ";
	string s2="Massive heatwave has been reached this summer updating maximal year temperature +85 degrees";
	regex r1(R"([\s\S]*?(summer|spring)\s+[\S\s]*?\s+(max|maximal|average)\s+[\S\s]*\s+temperature\s[+-][0-9]{2}\s+[\S\s]*)");

    cout<<regex_match(s1, r1);
    cout<<regex_match(s2, r1);
    return 0;
}