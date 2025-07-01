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
	// auto b=sregex_iterator(s.begin(),s.end(),r);
	// auto e=sregex_iterator();
	// string ans="";
	// for(auto i = b; i!=e; ++i){
	// 	ans+=i->str();
	// }
	// cout<<ans<<endl;
	string s="ere22ruioi4kkk200";
    smatch m;
    regex r("[0-9]+");
	string ans="";
	auto b=sregex_iterator(s.begin(),s.end(),r);
	auto e=sregex_iterator();
	for(auto i = b; i!=e; ++i){
		cout<<i->str();
	}
	cout<<endl;
	return 0;
}
