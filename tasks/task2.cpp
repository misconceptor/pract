#include <fstream>
#include <iostream>
#include <regex>
using namespace std;

void Temp(smatch s) {
    int deg = stoi(s.str(8));
    string sign = s.str(7);
    if (sign == "-")
        deg *= -1;
        // deg= -deg;
    if (deg< -20 || deg> 40 ) {
        cout << "Invalid temperature: " << deg<< '\n';
    }
}

int main() {
    setlocale(LC_ALL, "Russian");
    regex r(R"((.* +|)(весна|лето|осень|зима)( +.* +| +)(максимальная|макс\.)( средняя температура)( +.* +| +)(|-)(\d*)°( +.*|))");
    ifstream fin("input.txt");
    string str;
    int i=1;
    while (getline(fin, str)) {
        cout <<i++<<")-----------\n";
        getline(fin, str);
        cout << "Given string: \"" + str + "\"\n";
        smatch res;
        auto begin = str.cbegin();
        auto end = str.cend();
        if (regex_match(str, res, r)) {
            cout << "fits" << '\n';
            Temp(res);
        } else {
            cout << "doesn't fit" << '\n';
        }
        if (regex_search(str, res, r)) {
            cout << "substring: \"" + res.str() + "\" fits\n";
            Temp(res);
        } else {
            cout << "no matches\n";
        }
    }
    return 0;
}