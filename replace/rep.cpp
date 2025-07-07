#include <iostream>
#include <regex>
#include <string>
using namespace std;

int main(){
    //task1:
    string s1="My phone is 123-456-7890";
    regex r1(R"([0-9])");
    cout<<regex_replace(s1,r1,"#")<<endl;
    
    //task2:
    string s2="<p>Hello, <b>world</b>!</p>";
    regex r2(R"(<.*?>)");
    cout<<regex_replace(s2,r2,"")<<endl;

    //task3:
    string s3="Too     many     spaces";
    regex r3(R"(\s{2,})");
    cout<<regex_replace(s3,r3," ")<<endl; 

    //task4:
    string s4="today is 2025-07-01";
    regex r4(R"((\d{4})-(\d{2})-(\d{2}))");
    cout<<regex_replace(s4,r4,"$3.$2.$1")<<endl;

    //task5:
    string s5="Hi! My ID is #123_ABC.";
    regex r55(R"([^a-zA-Z]+)");
    regex r5(R"([\s]+)");
    cout<<regex_replace(s5,r5,"")<<endl;
    
    //task6:
    string s6="Write to me at test@example.com or admin@site.org.";
    regex r6(R"([\w.+-]+@[\w.-]+\.[a-zA-Z]{2,})");
    cout<<regex_replace(s6,r6,"<email>$&</email>")<<endl;
	return 0;
}