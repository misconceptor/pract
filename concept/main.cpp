#include <concepts>
#include <type_traits>
#include <iostream>      
using namespace std;
template<typename T>                                  
requires integral<T>
T gcd(T a, T b) {
    if(b==0) return a;
    else return gcd(b, a % b);
}
template<typename T>                                  
T gcd1(T a, T b) requires integral<T> {
    if(b==0) return a; 
    else return gcd1(b, a % b);
}
template<integral T>                                  
T gcd2(T a, T b) {
    if( b == 0 ) return a; 
    else return gcd2(b, a % b);
}
integral auto gcd3(integral auto a, integral auto b) { 
    if( b == 0 ) return a; 
    else return gcd3(b, a % b);
}
int main(){
    cout << '\n';
    cout << "gcd(100, 10)= "  <<  gcd(100, 10)  << '\n';
    cout << "gcd1(100, 10)= " <<  gcd1(100, 10)  << '\n';
    cout << "gcd2(100, 10)= " <<  gcd2(100, 10)  << '\n';
    cout << "gcd3(100, 10)= " <<  gcd3(100, 10)  << '\n';
    return 0;
}
