def g(x,y):
    while(x>0 and y>0):
        if(x>y):
            x=x%y
        else:
            y=y%x
    return x+y

def pr(x):
    i=2
    while i*i<=x:
        while x%i==0:
            x//=i
            print(i)
        i+=1
    if x>1:
        print(x)


def sum(a,b,base):
    max_len = max(len(a), len(b))
    result = []
    carry = 0
    for i in range(max_len):
        da = a[i] if i<len(a) else 0
        db = b[i] if i<len(b) else 0
        d=da+db+carry
        carry = d//base
        result.append(d%base)
    if carry > 0:
        result.append(carry)
    return result

n = int(input())
a = list(map(int, input().split()))
a = a[:n]
b = list(map(int, input().split()))
b = b[:n]
base = int(input())

sum_vector = sum(a, b, base)
print(sum_vector) 