"""This program was written with Claude Code assistance.

Week 10: numerical derivatives/integrals and Monte Carlo integration (numpy only).

Functions take numpy arrays and are vectorised: f(x) works on a scalar/1D array
for the single-variable helpers, and f(points) with shape (..., n) -> (...) for
the n-variable ones.
"""
import time
import numpy as np


# --- single variable -------------------------------------------------------
def numeric_derivative(f, x, h=1e-5):
    return (f(x + h) - f(x - h)) / (2 * h)  # central difference


def numeric_integral(f, a, b, n=100000):
    h = (b - a) / n
    return np.sum(f(a + h * (np.arange(n) + 0.5))) * h  # midpoint sum


def mc_integral_1d(f, a, b, N):
    return (b - a) * np.mean(f(np.random.uniform(a, b, N)))


# --- n variables -----------------------------------------------------------
def gradient(f, x, h=1e-5):
    x = np.asarray(x, dtype=float)
    g = np.empty_like(x)
    for i in range(x.size):
        e = np.zeros_like(x)
        e[i] = h
        g[i] = (f(x + e) - f(x - e)) / (2 * h)
    return g


def mc_integral(f, low, high, N):
    low, high = np.asarray(low, float), np.asarray(high, float)
    pts = np.random.uniform(low, high, (N, low.size))  # (N, n)
    return np.prod(high - low) * np.mean(f(pts))


MAX_ELEMS = 50_000_000  # grid size guard: k^n * n floats (~400 MB)


def integral(f, low, high, k=20):
    """Riemann (midpoint) integral on a k-per-axis grid; needs k**n points."""
    low, high = np.asarray(low, float), np.asarray(high, float)
    n = low.size
    if low.shape != high.shape or k < 1:
        raise ValueError("low/high must have the same shape and k >= 1")
    if k ** n * n > MAX_ELEMS:
        raise ValueError(f"Riemann infeasible: k^n = {k}^{n} points")
    h = (high - low) / k
    axes = [low[i] + h[i] * (np.arange(k) + 0.5) for i in range(n)]
    pts = np.stack(np.meshgrid(*axes, indexing="ij"), axis=-1)  # (k,)*n + (n,)
    return np.prod(h) * np.sum(f(pts))


# --- demo ------------------------------------------------------------------
def f(x):
    return np.sum(x ** 2, axis=-1)  # x1^2 + ... + xn^2 (low=0, high=1, see REPORT)


def check(name, got, exact, tol):
    ok = abs(got - exact) < tol
    print(f"{'OK  ' if ok else 'FAIL'} {name}: {got:.6f} (exact {exact:.6f}, tol {tol:.0e})")
    assert ok, name


def demo():
    np.random.seed(0)
    N = 100_000
    se1 = lambda sd, scale=1.0: 3 * scale * sd / np.sqrt(N)  # 3 standard errors
    sq = lambda x: x ** 2
    # 1. numeric derivative / integral
    check("d/dx x^2 at 3", numeric_derivative(sq, 3.0), 6, 1e-3)
    check("int x^2 on [0,1]", numeric_integral(sq, 0, 1), 1 / 3, 1e-3)
    check("d/dx sin at 0", numeric_derivative(np.sin, 0.0), 1, 1e-3)
    check("int sin on [0,pi]", numeric_integral(np.sin, 0, np.pi), 2, 1e-3)
    # 2. MC single variable (sd of x^2 on [0,1] = sqrt(4/45); of pi*sin on [0,pi] ~ 0.3077*pi)
    check("MC int x^2 on [0,1]", mc_integral_1d(sq, 0, 1, N), 1 / 3, se1(np.sqrt(4 / 45)))
    check("MC int sin on [0,pi]", mc_integral_1d(np.sin, 0, np.pi, N), 2, se1(0.3077, np.pi))
    # 3. gradient
    g = gradient(f, [1, 2, 3])
    print("gradient at [1,2,3]:", g, "exact [2 4 6]")
    assert np.allclose(g, [2, 4, 6], atol=1e-3)
    # 4. MC 2D
    check("MC int x^2+y^2 on [0,1]^2", mc_integral(f, [0, 0], [1, 1], N), 2 / 3, se1(np.sqrt(8 / 45)))
    print("\nItems 5 and 6: Riemann and Monte Carlo by dimension")
    ks = {1: 100_000, 2: 1000, 5: 22, 100: 2}  # 5D: k=20 gives 1.04e-3 error (fails 1e-3 rule), k=22 gives 8.6e-4
    print(f"\n{'dim':>4} {'exact':>9} {'Riemann':>10} {'R err':>9} {'R time':>7} "
          f"{'MC':>10} {'MC err':>9} {'3*SE':>8} {'MC time':>8}")
    for n, k in ks.items():
        low, high = np.zeros(n), np.ones(n)
        exact = n / 3
        t = time.time()
        try:
            r = integral(f, low, high, k)
            r_s, re_s, rt = f"{r:10.5f}", f"{abs(r - exact):9.1e}", f"{time.time() - t:6.2f}s"
            assert abs(r - exact) < 1e-3, "Riemann error too large"
        except ValueError:
            r_s, re_s, rt = f"{'infeasible':>10}", f"{'-':>9}", f"{'-':>7}"
            print(f"Riemann infeasible in {n}D (k=2 -> 2^{n} points)")
        t = time.time()
        m = mc_integral(f, low, high, N)
        mt = time.time() - t
        se = np.sqrt(n * 4 / 45) / np.sqrt(N)  # Var[x^2] on [0,1] = 1/5 - 1/9 = 4/45
        print(f"{n:>4} {exact:9.4f} {r_s} {re_s} {rt:>7} {m:10.5f} {abs(m - exact):9.1e} "
              f"{3 * se:8.1e} {mt:7.2f}s")
        assert abs(m - exact) < 3 * se, "MC error > 3 standard errors: bug"


if __name__ == "__main__":
    demo()
