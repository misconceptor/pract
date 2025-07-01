def matr():
    print("a")
r,c=map(int,input().split())
arr = [[],[]]
for i in range(r):
    row=[]
    for j in range(c):
        row=list(map(int,input().split()))
    arr.append(row)

for i in range(r):
    for j in range(c):
        print(arr[i][j],' ','\n')
