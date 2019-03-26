def maxChain(p):
    # n = len(p) - 1
    n = len(p)
    m = [[0 for i in range(n)] for j in range(n)]
    s = [[0 for i in range(n)] for j in range(n)]
    # for i in range(n):
    #     m[i][i] = 0
    for l in range(2,n):
        for i in range(1,n-l+1):
            j = i+l-1;
            m[i][j] = 9999999999;
            for k in range(i,j):
                q = m[i][k] + m[k+1][j] + p[i-1] * p[k] * p[j]
                if q < m[i][j]:
                    m[i][j] = q;
                    s[i][j] = k
    return m, s


# 输出矩阵链的最优括号化方法
def printOpt(s, i, j):
    if i == j:
        print("A", i, end='')
    else:
        # print("(", end="")
        print("(", end='')
        printOpt(s, i, s[i][j])
        printOpt(s, s[i][j]+1, j)
        print(")", end='')
print("------Start Testing Here-------")
p = [30, 35, 15, 5, 10, 20, 25]
m, s = maxChain(p)

print(m)
print(s)
print("最优括号化方案为：")
printOpt(s, 1, 6)
print("")
print("其标量乘法次数为：", m[1][6])

print("-----End Testing Here-----")