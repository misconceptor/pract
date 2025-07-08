#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <regex>
#include <iterator>

using namespace std;

bool isFraction(const string& str) {
    return regex_match(str, regex(R"([-+]?\d+/\d+)"));
}

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
    cout<<"text="<<text<<"!\n";
    regex date_regex(R"(\d{2}[./\/-]\d{2}[./\/-]\d{4}|\d{4}[./\/-]\d{2}[./\/-]\d{2})");
    auto b=sregex_iterator(text.begin(), text.end(), date_regex);
    auto e=sregex_iterator();
    int date_pos=b->position();
    cout<<"pos="<<date_pos<<endl;
    int num=0;
    for(auto it=b;it!=e;++it,++num){}
    if(num!=1){
        cout<<"Error: not a single date\n";
        return 1;
    }
    if(date_pos!=0){
        cout<<"Error: position is not in the beginning\n";
        return 1;
    }

    // regex number_regex(R"([-+]?(?:\d+/\d+|\d*\.\d+|\d+\.?\d*(?:[eE][-+]?\d+)?|\d+))");
    // sregex_iterator it(text.begin(), text.end(), number_regex);
    // sregex_iterator end;

    // double sum_integers = 0;
    // double sum_fractions = 0;
    // for (; it != end; ++it) {
    //     string number_str = it->str();
    //     size_t number_pos = it->position();
    //     if (number_pos < date_end_pos && number_pos + number_str.length() > date_pos) {
    //         continue;
    //     }
    //     if (number_pos < date_pos) {
    //         cerr << "Error: number before the date: " << number_str << endl;
    //         return 1;
    //     }
    //     if (isFraction(number_str)) {
    //         sum_fractions += fractionToDouble(number_str);
    //     } else if (number_str.find('.') != string::npos || 
    //             number_str.find('e') != string::npos || 
    //             number_str.find('E') != string::npos) {
    //         sum_fractions += stod(number_str);
    //     } else {
    //         sum_integers += stoi(number_str);
    //     }
    // } 
    // cout << "Sum of integers: " << sum_integers << endl;
    // cout << "Sum of non-integers: " << sum_fractions << endl;
    return 0;
}


// int main()
// {
//     ifstream fin("input.txt");
//     if (!fin.is_open()) {
//         cout << "file not opened\n";
//         return 1;
//     }
//     string s;
//     regex str("\"[^\"]*\"");
//     regex integ("([^e\\.\\d-])-?\\d+([^e\\.\\d-])|(\\n)");
//     regex doub("([^e\\.\\d-])-?\\d+\\.\\d+([^e\\.\\d-])|(\\n)");
//     regex doub1("([^e\\.\\d-])-?\\d(\\.\\d+)?e-?\\d+([^e\\.\\d-])|(\\n)");
//     smatch mstr,mint,md,md1;
//     int sumint = 0;
//     double sumdouble = 0;
//     while (getline(fin, s)) {
//         cout << "string: ";
//         auto pos1 = s.cbegin();
//         auto end1 = s.cend();
//         for (; regex_search(pos1, end1, mstr, str); pos1 = mstr.suffix().first) {
//             cout << mstr.str() << endl;
//         }
//         s = regex_replace(s, str," ");
//         cout << s << endl;
//         auto pos2 = s.cbegin();
//         auto end2 = s.cend();
//         for (; regex_search(pos2, end2, mint, integ); pos2 = mint.suffix().first)
//         {
//             string str = mint.str();
//             str = str.substr(1,str.size()-2);
//             int result = stoi(str);
//             cout << "int=" << result << endl;
//             sumint += result;
//         }
//         auto pos3 = s.cbegin();
//         auto end3 = s.cend();
//         for (; regex_search(pos3, end3, md, doub); pos3 = md.suffix().first)
//         {
//             string str = md.str();
//             str = str.substr(1, str.size() - 2);
//             double result = stod(str);
//             cout << "double=" << result << endl;
//             sumdouble += result;
//         }
//         auto pos4 = s.cbegin();
//         auto end4 = s.cend();
//         for (; regex_search(pos4, end4, md1, doub1); pos4 = md1.suffix().first)
//         {
//             string str = md1.str();
//             str = str.substr(1, str.size() - 2);
//             double result = stod(str);
//             cout << "double1=" << result << endl;
//             sumdouble += result;
//         }
 
//     }
//     cout << endl;
//     cout << "sumint = " << sumint << endl;
//     cout << "sumdouble = " << sumdouble << endl;
//     return 0;
// }