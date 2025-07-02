#include <iostream>
#include <regex>
#include <string>
using namespace std;

int main(){
	// string s="qqq123 _p999";
	// smatch m;
	// regex r (R"(\b[a-zA-Z_]+(?=\d+))");
	// string ans;
    // while (regex_search(s, m, r)) {
    //     cout << m.str() << endl;         
	// 	ans += m.str();
    //     s = m.suffix().str();
    // }
	//^\S+\s(spring|summer)\s\S+\s(max|middle)\s\S+\s([1-9]|[1-4][0-9]|50)\s\S+$
	// auto b=sregex_iterator(s.begin(),s.end(),r);
	// auto e=sregex_iterator();[˚°][
	// string ans="";
	// for(auto i = b; i!=e; ++i){
	// 	ans+=i->str();
	// }
	// cout<<ans<<endl;
	string s="text summer sometext max sometext temperature +40 sometext";
	string s1="text summer some text";
	regex r1(R"([\s\S]*?(summer|spring)\s[\S\s])");
	regex r(R"([\s\S]*?(summer|spring)\s[\s\S]
		*?(max|maximal(\.?)|average)\s[\s\S]*?
		temperature\s[\s\S]*?([-+]?\d+)\s\S]*?)");

    bool b=regex_match(s1, r1);
	cout<<b<<endl;
	return 0;
}
