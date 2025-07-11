#include <iostream>
#include <fstream>
#include <regex>
#include <string>
using namespace std;

int main()
{
    std::ifstream fin("input.txt");
    if (!fin.is_open()) {
        cout << "file not opened." << std::endl;
        return 1;
    }
    string s;
    regex str("\"[^\"]*\"");
    regex integ("([^e\\.\\d-])-?\\d+([^e\\.\\d-])|(\\n)");
    regex doub("([^e\\.\\d-])-?\\d+\\.\\d+([^e\\.\\d-])|(\\n)");
    regex doub1("([^e\\.\\d-])-?\\d(\\.\\d+)?e-?\\d+([^e\\.\\d-])|(\\n)");
    smatch mstr;
    smatch mint;
    smatch md;
    smatch md1;
    int sumint = 0;
    double sumdouble = 0;
    while (getline(fin, s)) {
        cout << "string: ";
        auto pos1 = s.cbegin();
        auto end1 = s.cend();
        for (; regex_search(pos1, end1, mstr, str); pos1 = mstr.suffix().first) {
            cout << mstr.str() << endl;
        }
        s = regex_replace(s, str," ");
        cout << s << endl;
        auto pos2 = s.cbegin();
        auto end2 = s.cend();
        for (; regex_search(pos2, end2, mint, integ); pos2 = mint.suffix().first)
        {
            string str = mint.str();
            str = str.substr(1,str.size()-2);
            int result = stoi(str);
            cout << "int=" << result << endl;
            sumint += result;
        }
        auto pos3 = s.cbegin();
        auto end3 = s.cend();
        for (; regex_search(pos3, end3, md, doub); pos3 = md.suffix().first)
        {
            string str = md.str();
            str = str.substr(1, str.size() - 2);
            double result = stod(str);
            cout << "double=" << result << endl;
            sumdouble += result;
        }
        auto pos4 = s.cbegin();
        auto end4 = s.cend();
        for (; regex_search(pos4, end4, md1, doub1); pos4 = md1.suffix().first)
        {
            string str = md1.str();
            str = str.substr(1, str.size() - 2);
            double result = stod(str);
            cout << "double1=" << result << endl;
            sumdouble += result;
        }
 
    }
    cout << endl;
    cout << "sumint = " << sumint << endl;
    cout << "sumdouble = " << sumdouble << endl;
}
