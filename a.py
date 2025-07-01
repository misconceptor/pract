def matr():
    print("a")
r,c=map(int,input().split())
arr = [[],[]]
for i in range(r):
    row=list(map(int,input().split()))
    arr.append(row)
for row in arr:
    print(' '.join(map(str,row)))
