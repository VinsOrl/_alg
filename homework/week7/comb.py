"""C(n, k): choose k out of n, two ways.

Non-DP: plain recursion on Pascal's rule C(n,k) = C(n-1,k-1) + C(n-1,k).
Each call branches in two, and the same (n,k) pair gets recomputed many
times along different branches -> O(C(n,k)) calls, exponential in n.

DP: bottom-up table built from the same recurrence, but each (n,k) is
computed once and reused -> O(n*k) time and space.
"""


def c_recursive(n: int, k: int) -> int:
    if k == 0 or k == n:
        return 1
    return c_recursive(n - 1, k - 1) + c_recursive(n - 1, k)


def c_dp(n: int, k: int) -> int:
    table = [[0] * (k + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        for j in range(min(i, k) + 1):
            table[i][j] = 1 if j == 0 or j == i else table[i - 1][j - 1] + table[i - 1][j]
    return table[n][k]


def demo() -> None:
    import math

    for n in range(0, 15):
        for k in range(0, n + 1):
            expected = math.comb(n, k)
            assert c_recursive(n, k) == expected
            assert c_dp(n, k) == expected
    print("ok: c_recursive and c_dp agree with math.comb for n in 0..14")


if __name__ == "__main__":
    demo()
