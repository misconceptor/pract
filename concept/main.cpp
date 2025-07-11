#include <concepts>
#include <type_traits>
#include <iostream>      
#include <string>
#include <vector>
using namespace std;

template<typename T> //task 1a
// requires std::integral<T>
void print_if_integer(T a){
    static_assert(integral<T>,"not an integral");
    cout<<a<<endl;
}

template<typename T>//task 1b
requires std::is_floating_point_v<T>
void print_if_floating_point(T a){
    cout<<a<<endl;
}

template<typename T>//task 1c
concept numeric=integral<T>||floating_point<T>;
template<numeric T>
void print_if_numeric(T a){
    cout<<a<<endl;
}

template<integral T> //task2
T double_if_integral(T a){
    return a*2;
}

template<typename T> //task 3ab
T double_if_integral2(T a){
    static_assert(integral<T>,"not an integral");
    return a*2;
}

template<integral T>//task4a
T task4(T a){
    cout<<a*2<<endl;
    return a*2;
}
template<typename T>//task4b
concept not_int=!std::integral<T>;
template<not_int T>
void task4(T a){
    cout<<"Error: not an integral\n";
}

// template <typename T> //task5a
// enable_if_t<is_integral_v<T>, T>
// doubleValue(T value) {
//     return value * 2;
// }
// template <typename T>//task5b
// enable_if_t<!is_integral_v<T>, void>
// doubleValue(T) {
//     // static_assert(std::is_integral_v<T>, "not an integral");
//     cout<<"doubleValue error: not an integral\n";
// }

struct st{};
template<typename T> //task6
concept Printable = requires(ostream& os, T const& t) {
    // { os << t } -> std::same_as<std::ostream&>;
    os<<t;
};
template<Printable T>
void print(const T& value) {
    cout << value << endl;
}

template<typename T> //task7
concept Addable=requires(T a, T b){
    a+b;
};
template<Addable T>
T sum(T a, T b){
    return a+b;
}

template<typename T> //task 5
concept Integral = is_integral_v<T>;
template<typename T>
struct X {
    static T func(T) {
        cout << "not an integer\n"<< std::endl;
        return T{};
    }
};
template<Integral T>
struct X<T> {
    static T func(T a) {
        return a*2;
    }
};

template<typename T>
T function(T a){
    X<T>::func(a);
}

int main(){
    // cout<<(X<int>::func(5))<<endl; 
    // X<string>::func("ooo"); 
    int k=1;
    string s="iuiu";
    function(k);
    return 0;
}