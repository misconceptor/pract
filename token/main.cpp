#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <regex>
#include <iterator>
using namespace std;
double fractionToDouble(const string& str) {
    stringstream ss(str);
    int num, denom;
    char slash;
    ss >> num >> slash >> denom;
    return static_cast<double>(num) / denom;
}
int main(){
    ifstream file("input.txt");
    if (!file) {
        cerr << "file not opened\n";
        return 1;
    }
    string text((istreambuf_iterator<char>(file)), istreambuf_iterator<char>());
    cout<<"text=\""<<text<<"\"\n";
    regex date_regex(R"(\b(\d{2}[./\/-]\d{2}[./\/-]\d{4}|\d{4}[./\/-]\d{2}[./\/-]\d{2})\b)");
    auto b=sregex_iterator(text.begin(), text.end(), date_regex);
    auto e=sregex_iterator();
    int date_pos=b->position(0);
    for(int i=0;i<date_pos;++i){
        // if(text[i] != ' ' && text[i] != '\t' && text[i] != '\n' && text[i] != '\r'){
        if(text[i]>='0' && text[i] <= '9'){
            cout<<"Error: something before the date!\n";
            return 1;
        }
    }
    int num=0;
    for(auto it=b;it!=e;++it,++num){}
    if(num!=1){
        cout<<"Error: number of dates = "<<num<<endl;
        return 1;
    }
    auto q=sregex_iterator(text.begin(), text.end(), date_regex);
    cout<<"Date: "<<q->str()<<endl;
    text =regex_replace(text,date_regex," ");

    regex doublereg(R"(([-+]?\d+/\d+)|([-+]?(\d+(\.\d*)?|\.\d+)[eE][+-]?\d+)|([-+]?\d*\.\d+))");
    auto bd=sregex_iterator(text.begin(), text.end(), doublereg);
    auto ed=sregex_iterator();
    double double_sum=0.0;
    cout<<"Non-integers: ";
    for(auto it=bd;it!=ed;++it){
        string token=it->str();
        if(token.find('/')!=token.npos){
            cout<<token<<' ';
            double_sum+=fractionToDouble(token);
        } else {
            double num=(double)stod((*it).str());
            cout<<num<<' ';
            double_sum+=num;
        }
    }
    
    text = regex_replace(text, doublereg, " ");
    cout<<"\nSum: "<<double_sum<<endl;

    regex intreg(R"(\b[+-]?\d+\b)");

    auto bi=sregex_iterator(text.begin(), text.end(), intreg);
    auto ei=sregex_iterator();
    int int_sum=0;
    cout<<"Integers: ";
    for(auto it=bi;it!=ei;++it){
        int num=stoi((*it).str());
        cout<<num<<' ';
        int_sum+=num;
    }
    cout<<"\nSum: "<<int_sum<<endl; 
    text =regex_replace(text,intreg," ");
    return 0;
}