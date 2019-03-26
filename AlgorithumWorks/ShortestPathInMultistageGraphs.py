import numpy as np
def Sove(N, M, map):

    minStep = float('inf')  # 定义一个中间变量，用于保存每对顶点M步的最短距离

    def dfs(start, end, N, M, dis, steps):
        nonlocal minStep  # 使用外界变量
        if steps == M:  # 更新最优值，并设置递归出口
            if start == end:
                minStep = min(minStep, dis)
            return

        for next in range(N):  # 深度搜索
            if next == start:continue  # 如果自己那么一定为0，也就没必要进行了。
            rdis = dis + map[start][next]
            dfs(next, end, N, M, rdis, steps + 1)

    res = [[None] * N for _ in range(N)]
    for i in range(N):
        for j in range(i, N):
            dfs(i, j, N, M, 0, 0)
            res[i][j] = res[j][i] = minStep
            minStep = float('inf')  # 恢复到最大值
    return res


if __name__ == '__main__':
    N, M = 3, 2
    map = np.zeros((16,16))
    map = np.uint8(map)
    map[0,1] = 5
    map[0,2] = 3
    map[1,3] = 1
    map[1,4] = 3
    map[1,5] = 6
    map[2,4] = 8
    map[2,5] = 7
    map[2,6] = 6
    map[3,7] = 6
    map[3,8] = 8
    map[4,7] = 3
    map[4,8] = 5
    map[5,8] = 3
    map[5,9] = 3
    map[6,8] = 8
    map[6,9] = 4
    map[7,10] = 2
    map[7,11] = 2
    map[8,11] = 1
    map[8,12] = 2
    map[9,11] = 3
    map[9,12] = 3
    map[10,13] = 3
    map[10,14] = 5
    map[11,13] = 5
    map[11,14] = 2
    map[12,13] = 6
    map[12,14] = 6
    map[13,15] = 4
    map[14,15] = 3

    map2 = np.zeros((5,5))
    map2[0,1] = -1
    map2[0,2] = 3
    map2[1,2] = 3
    map2[1,3] = 2
    map2[1,4] = 2
    map2[3,1] = 1
    map2[3,2] = 5
    map2[4,3] = -3
    res = Sove(N, M, map2)
    for v in res:
        print(v)
