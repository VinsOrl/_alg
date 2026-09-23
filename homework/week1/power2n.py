"""
Compare four ways of computing 2**n and measure how fast each one runs.

Method 1 : built-in exponentiation
Method 2a: double recursion            -> O(2**n), cannot finish at n=100
Method 2b: single (linear) recursion   -> O(n)
Method 3 : recursion + lookup table (memoization) -> O(n)

Run: python3 power2n.py
"""

import sys
import timeit
import unicodedata


# --------------------------------------------------------------------------
# Method 1: use the built-in exponentiation operator.
# --------------------------------------------------------------------------
def power2n_1(n):
    return 2 ** n


# --------------------------------------------------------------------------
# Method 2a: recursion, power2n(n-1) + power2n(n-1)
#   Every level calls itself twice -> about 2**n calls -> exponential, slow.
#   At n=100 this needs ~2**100 calls, so in practice it never finishes.
# --------------------------------------------------------------------------
def power2n_2a(n):
    if n == 0:
        return 1
    return power2n_2a(n - 1) + power2n_2a(n - 1)


# --------------------------------------------------------------------------
# Method 2b: recursion, 2 * power2n(n-1)
#   Every level calls itself once -> about n calls -> linear, feasible.
# --------------------------------------------------------------------------
def power2n_2b(n):
    if n == 0:
        return 1
    return 2 * power2n_2b(n - 1)


# --------------------------------------------------------------------------
# Method 3: recursion + lookup table (memoization)
#   Even written as power2n(n-1) + power2n(n-1), each n is computed only once
#   because results are cached -> collapses to O(n).
# --------------------------------------------------------------------------
_memo = {0: 1}


def power2n_3(n):
    if n in _memo:                      # lookup: if already computed, return it
        return _memo[n]
    _memo[n] = power2n_3(n - 1) + power2n_3(n - 1)
    return _memo[n]


# --------------------------------------------------------------------------
# Display helpers: pad by rendered width so wide glyphs (✓ ✗ etc.) still align.
# --------------------------------------------------------------------------
def display_width(text):
    """Number of terminal columns `text` occupies (wide chars count as 2)."""
    return sum(2 if unicodedata.east_asian_width(c) in ("W", "F") else 1
               for c in text)


def pad(text, width):
    """Left-justify `text` to `width` display columns."""
    return text + " " * max(0, width - display_width(text))


# --------------------------------------------------------------------------
# Main program: verify correctness + benchmark.
# --------------------------------------------------------------------------
def verify_correctness():
    """Check every method agrees with 2**n on small n."""
    print("=== Correctness check (n = 0..20) ===")
    ok = True
    for n in range(21):
        expected = 2 ** n
        results = {
            "Method 1 ": power2n_1(n),
            "Method 2a": power2n_2a(n),
            "Method 2b": power2n_2b(n),
            "Method 3 ": power2n_3(n),
        }
        for name, value in results.items():
            if value != expected:
                print(f"  x {name} wrong at n={n}: got {value}, expected {expected}")
                ok = False
    print("  ok: all four methods correct for n=0..20\n" if ok
          else "  some method computed a wrong value!\n")


def bench(func, n, repeat):
    """Return (average seconds per call, computed result) for func(n)."""
    total = timeit.timeit(lambda: func(n), number=repeat)
    return total / repeat, func(n)


def main():
    # The recursive methods reach depth ~100 at n=100; raise the limit to be safe.
    sys.setrecursionlimit(10_000)

    verify_correctness()

    N = 100
    expected = 2 ** N
    rows = []  # (name, correct?, seconds_per_call, big_o, note)

    # ---- Method 1: built-in ----
    t, val = bench(power2n_1, N, repeat=100_000)
    rows.append(("Method 1  built-in 2**n", val == expected, t, "O(1)*", ""))

    # ---- Method 2b: linear recursion ----
    t, val = bench(power2n_2b, N, repeat=10_000)
    rows.append(("Method 2b linear recursion", val == expected, t, "O(n)", ""))

    # ---- Method 3: recursion + lookup table ----
    # Clear the cache before each run so we fairly measure computing from scratch.
    def power2n_3_fresh(n):
        _memo.clear()
        _memo[0] = 1
        return power2n_3(n)

    t, val = bench(power2n_3_fresh, N, repeat=10_000)
    rows.append(("Method 3  recursion + memo", val == expected, t, "O(n)", ""))

    # ---- Method 2a: double recursion ----
    # n=100 needs ~2**100 ~= 1.3e30 calls: it never finishes, so we cannot time it.
    # Instead we show the cost exploding at a small, feasible n and extrapolate.
    small_n = 22
    t_small, val_small = bench(power2n_2a, small_n, repeat=3)
    est_seconds = t_small * (2 ** (N - small_n))   # extrapolate by O(2**n)
    est_years = est_seconds / (60 * 60 * 24 * 365)
    rows.append((
        "Method 2a double recursion", None, None, "O(2^n)",
        "cannot run at n=100 (~2^100 ~= 1.3e30 calls)",
    ))

    # ---- Print the results table ----
    print(f"=== Benchmark (n = {N}) ===")
    cols = (28, 8, 16, 8)  # display widths for: name, correct, time, big-O
    header = (pad("Method", cols[0]) + pad("OK", cols[1])
              + pad("Time/call", cols[2]) + pad("Big-O", cols[3]) + "Note")
    print(header)
    print("-" * display_width(header))
    # Feasible methods sorted by speed; the None-time row (2a) goes last.
    sortable = sorted(
        rows,
        key=lambda r: (r[2] is None, r[2] if r[2] is not None else 0),
    )
    for name, correct, t, bigo, note in sortable:
        if t is None:
            time_str, ok_str = "N/A", "-"
        else:
            time_str = f"{t * 1e6:,.3f} us"
            ok_str = "yes" if correct else "NO"
        print(pad(name, cols[0]) + pad(ok_str, cols[1])
              + pad(time_str, cols[2]) + pad(bigo, cols[3]) + note)

    print()
    print("Method 2a note:")
    print(f"  At n={small_n} each call took about {t_small * 1e3:.3f} ms "
          f"(result correct: {val_small == 2 ** small_n}).")
    print(f"  Because it is O(2^n), adding 1 to n doubles the time.")
    print(f"  Extrapolated to n=100: about {est_seconds:.2e} s ~= {est_years:.2e} "
          f"years -- far longer than the age of the universe,")
    print(f"  so Method 2a simply 'does not work' at n=100.")
    print()
    print("Conclusion (fast -> slow): "
          "Method 1 built-in  >  Method 2b/3 linear  >>>  Method 2a exponential (fails)")
    print("* Method 1's 2**n still does big-integer work under the hood, so it is not")
    print("  strictly O(1), but at this size it is far faster than the rest.")


if __name__ == "__main__":
    main()
