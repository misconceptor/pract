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
    regex date_regex(R"((\b\d{2}[./]\d{2}[./]\d{4}\b|\b\d{4}-\d{2}-\d{2}\b))");
    smatch date_match;
    if (!regex_search(text, date_match, date_regex)) {
        cerr << "Date not found." << endl;
        return 1;
    }
    size_t date_pos = date_match.position(0);
    string date_str = date_match.str(0);
    cout << "Date: " << date_str << endl;

    size_t date_end_pos = date_pos + date_str.length();

    regex number_regex(R"([-+]?(?:\d+/\d+|\d*\.\d+|\d+\.?\d*(?:[eE][-+]?\d+)?|\d+))");
    sregex_iterator it(text.begin(), text.end(), number_regex);
    sregex_iterator end;

    double sum_integers = 0;
    double sum_fractions = 0;
    for (; it != end; ++it) {
        string number_str = it->str();
        size_t number_pos = it->position();
        if (number_pos < date_end_pos && number_pos + number_str.length() > date_pos) {
            continue;
        }
        if (number_pos < date_pos) {
            cerr << "Error: number before the date: " << number_str << endl;
            return 1;
        }
        if (isFraction(number_str)) {
            sum_fractions += fractionToDouble(number_str);
        } else if (number_str.find('.') != string::npos || 
                number_str.find('e') != string::npos || 
                number_str.find('E') != string::npos) {
            sum_fractions += stod(number_str);
        } else {
            sum_integers += stoi(number_str);
        }
    } 
    cout << "Sum of integers: " << sum_integers << endl;
    cout << "Sum of non-integers: " << sum_fractions << endl;
    return 0;
}