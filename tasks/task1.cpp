#include <iostream>
#include <regex>
#include <string>
using namespace std;

void task1(){ //a(2 any symbols)a
    string s="a\nxa iuaooa     a\n\na";
    regex r(R"(a[\w\W]{2}a)"); //\W=non-alnum,\w=alnum
    auto b=sregex_iterator(s.begin(),s.end(),r);
    auto e=sregex_iterator();
    for(auto i=b;i!=e;++i){
        cout<<i->str()<<',';
    }
    cout<<endl;
}
void task2(){ //a(any, but not bc)a
    regex r(R"(a(?:(?!bc)..)a)");
    string s="sdf abca aabcba";
    auto b = sregex_iterator(s.begin(),s.end(),r);
    auto e = sregex_iterator();
    for(auto i = b; i!=e; ++i){
        cout<<i->str()<<' ';
    }
    cout<<endl;
}
void task3(){
    regex r(R"(ab*a)");
    string s="aa abba abbbba abbbcbbba";
    auto b = sregex_iterator(s.begin(),s.end(),r);
    auto e = sregex_iterator();
    for(auto i = b; i!=e; ++i){
        cout<<i->str()<<' ';
    }
    cout<<endl;
}
void task4(){
    string s="abab ybabo aa ";
    regex r(R"((ab)+)");
    auto b=sregex_iterator(s.begin(),s.end(),r);
    auto e=sregex_iterator();
    // string ans="";
    for(auto i=b;i!=e;++i){
        //ans+=(*i)[0].str();
        cout<<i->str()<<',';
    }
    // cout<<ans<<endl;
}
void task5(){
    string s="2+++3 23 2-3";
    regex r(R"(2[+]*3)");
    auto b=sregex_iterator(s.begin(),s.end(),r);
    auto e=sregex_iterator();
    string ans="";
    for(auto i=b;i!=e;++i){
        ans+=(*i)[0].str();
        //cout<<i->str()<<',';
    }
    cout<<ans<<endl;
}
void task6(){
    string s="abbbba abbbbb abbca abb";
    regex r(R"(ab{2,4}a)");
    auto b=sregex_iterator(s.begin(),s.end(),r);
    auto e=sregex_iterator();
    string ans="";
    for(auto i=b;i!=e;++i){
        ans+=(*i)[0].str();
        //cout<<i->str()<<',';
    }
    cout<<ans<<endl;
}
void task7(){
    string s="abbbb abbbbb acccd abb";
    regex r(R"(ab{5,})");
    auto b=sregex_iterator(s.begin(),s.end(),r);
    auto e=sregex_iterator();
    string ans="";
    for(auto i=b;i!=e;++i){
        ans+=(*i)[0].str();
        //cout<<i->str()<<',';
    }
    cout<<ans<<endl;
}
void task8(){
    string s="a9898a aiiia a7a";
    regex r(R"(a([0-9])a)");
    auto b=sregex_iterator(s.begin(),s.end(),r);
    auto e=sregex_iterator();
    string ans="";
    for(auto i=b;i!=e;++i){
        ans+=(*i)[1].str();
        //если надо саму подстроку то [0]
        //cout<<i->str()<<',';
    }
    cout<<ans<<endl;
}
void task9(){
    string s="a9898a aiiiia a\n\n\na";
    regex r(R"(a([^0-9]*)a)");
    auto b=sregex_iterator(s.begin(),s.end(),r);
    auto e=sregex_iterator();
    string ans="";
    for(auto i=b;i!=e;++i){
        ans+=(*i)[1].str();
        //cout<<i->str()<<',';
    }
    cout<<"("<<ans<<")"<<endl;
}
void task10(){
    string s="annna aa a\n\na a0909a apppa";
    regex r(R"(a([a-z]+)a)");
    auto b=sregex_iterator(s.begin(),s.end(),r);
    auto e=sregex_iterator();
    string ans="";
    for(auto i=b;i!=e;++i){
        ans+=(*i)[1].str();
        //cout<<i->str();
    }
    cout<<ans<<endl;
}
void task11(){
    string s="aaa8\n\n\naaa10aaa1";
    regex r(R"(([0-9]+))");
    auto b=sregex_iterator(s.begin(),s.end(),r);
    auto e=sregex_iterator();
    int sum=0;
    for(auto i=b;i!=e;++i){
        sum+=stoi((*i)[1].str());
        // cout<<(*i)[1].str()<<'+';
        // cout<<i->str()<<'+';
    }
    cout<<sum<<endl;
}
void task12(){
    string s="i<oioi>uu <> <144>ppp";
    regex r(R"(<([^<>]*)>)");
    string ans;
    auto b = sregex_iterator(s.begin(),s.end(),r);
    auto e = sregex_iterator();
    for(auto i = b; i!=e; ++i){
        cout<<(*i)[1].str();
    }
    cout<<endl;
}
int main(){
    task4();
    return 0;
}