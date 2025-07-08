#include <concepts>
#include <type_traits>
#include <iostream>      
#include <string>
#include <vector>
using namespace std;
template<typename T>
concept isbool=is_same_v<T,bool>;

template<typename T>
concept integral_not_bool = std::integral<T> && (!isbool<T>);

template<typename T>
requires isbool<T>
void f(T a) {
    cout << "boolean " << boolalpha << a << endl;
}

template<typename T>
requires integral_not_bool<T>
void f(T a) {
    cout << "integral " << a << endl;
}

template<typename T>
requires std::floating_point<T>
void f(T a) {
    cout << "float " << a << endl;
}

int main() {
    float d = 1.1f;
    bool b = false;
    int a = 55;
    f(d);
    f(b);
    f(a);
    return 0;
}