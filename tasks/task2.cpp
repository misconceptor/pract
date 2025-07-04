#include <iostream>
#include <regex>
#include <string>
using namespace std;
// Напишите регулярное выражение
// для поиска в заданной строке всех подстрок,
// удовлетворяющих шаблону:
// буква 'a', 2 любых символа, буква 'a',
// но пропускающих подстроку abca.

int main(){
    regex r(R"(a(?:(?!bc)..)a)");
    string s="sdf abca aabcba";
    auto b = sregex_iterator(s.begin(),s.end(),r);
    auto e = sregex_iterator();
    for(auto i = b; i!=e; ++i){
        cout<<i->str()<<' ';
    }
    cout<<endl;

    // smatch m;
    // while(regex_search(s,m,r)){
    //     cout<<m.str()<<' ';
    //     s=m.suffix().str();
    // }
    // cout<<endl;
    return 0;
}