
# def pr(x):
#     i=2
#     while i*i<=x:
#         while x%i==0:
#             x//=i
#             print(i)
#         i+=1
#     if x>1:
#         print(x)


# def sum(a,b,base):
#     max_len = max(len(a), len(b))
#     result = []
#     carry = 0
#     for i in range(max_len):
#         da = a[i] if i<len(a) else 0
#         db = b[i] if i<len(b) else 0
#         d=da+db+carry
#         carry = d//base
#         result.append(d%base)
#     if carry > 0:
#         result.append(carry)
#     return result

# n = int(input())
# a = list(map(int, input().split()))
# a = a[:n]
# b = list(map(int, input().split()))
# b = b[:n]
# base = int(input())

# sum_vector = sum(a, b, base)
# print(sum_vector) 
class Lion:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def bark(self):
        return f"{self.name}" 

    def birthday(self):
        self.age += 1
        return f"{self.name} is now {self.age} years old."

    def change_name(self, new_name):
        old_name = self.name
        self.name = new_name
        return f"{old_name} is now {self.name}."

    def info(self):
        return f"Lion's name: {self.name}, Age: {self.age}"

lion1 = Lion("leva", 5)
print(lion1.bark())            
print(lion1.birthday())       
print(lion1.change_name("Lev"))  
print(lion1.info())           
