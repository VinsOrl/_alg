"""Closed forms for the week2 recurrences; run to verify against brute force.

1. T(n)=T(n-1)+8,  T(1)=1  -> 8n-7          O(n)
2. T(n)=2T(n-1)+9, T(1)=1  -> 5*2^n-9       O(2^n)
3. T(n)=2T(n/2)+1, T(1)=1  -> 2n-1          O(n)      (n=2^k)
4. T(n)=T(n/2)+1,  T(1)=1  -> log2(n)+1     O(log n)  (n=2^k)
"""
def a(n): return 1 if n == 1 else a(n - 1) + 8
def b(n): return 1 if n == 1 else 2 * b(n - 1) + 9
def c(n): return 1 if n == 1 else 2 * c(n // 2) + 1
def d(n): return 1 if n == 1 else d(n // 2) + 1

if __name__ == "__main__":
    for n in range(1, 20):
        assert a(n) == 8 * n - 7 and b(n) == 5 * 2**n - 9
    for k in range(12):
        assert c(2**k) == 2 * 2**k - 1 and d(2**k) == k + 1
    print("ok")
