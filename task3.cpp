#include <iostream>
#include <regex>
#include <string>
using namespace std;

int main(){
    regex r(R"(ab*a)");
    string s="abbbba aa abu abbbu";
    auto b=sregex_iterator(s.begin(),s.end(),r);
    auto e=sregex_iterator();
    for(auto i=b; i!=e;++i){
        cout<<i->str()<<' ';
    }
    cout<<endl;
    return 0;
}