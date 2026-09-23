# Week 1 — Four Ways to Compute 2ⁿ

Compare four ways of writing `2**n` and measure which is fast, which is slow, and
which cannot finish at all. Test value: **n = 100**.

## How to run

```bash
python3 power2n.py
```

The program first checks correctness (n = 0..20), then benchmarks each method at n = 100.

## The four methods

| Method | Code | Complexity | Works at n=100? |
|--------|------|------------|-----------------|
| Method 1  | `return 2 ** n` (built-in) | O(1)* | ✅ fastest |
| Method 2a | `power2n(n-1) + power2n(n-1)` (double recursion) | **O(2ⁿ)** | ❌ never finishes |
| Method 2b | `2 * power2n(n-1)` (single recursion) | O(n) | ✅ feasible |
| Method 3  | recursion + lookup table (memoization) | O(n) | ✅ feasible |

\* Method 1's `2**n` still does big-integer work under the hood, so it is not strictly
O(1), but at this size it is far faster than everything else.

## Key point: why does Method 2a "fail"?

Method 2a calls itself **twice** at every level:

```
power2n(n)
├── power2n(n-1)
│   ├── power2n(n-2) ...
│   └── power2n(n-2) ...
└── power2n(n-1)
    ├── power2n(n-2) ...
    └── power2n(n-2) ...
```

The number of calls is about **2ⁿ**. Every time n increases by 1, the time **doubles**.

- Measured at n=22: about **1 second** per call
- n=100 needs about **2ⁿ ≈ 1.3×10³⁰** calls
- Extrapolating, n=100 would take roughly **10¹⁵+ years** (far longer than the age of the universe)

So at n=100, Method 2a is not merely "slow" — it **cannot complete**. The program
therefore does not run it directly; it demonstrates the cost blowing up at a small n
(n=22) and extrapolates.

Method 2b (`2 * power2n(n-1)`) calls itself only once, so it makes n calls and is linear
and feasible. One tiny difference in how it's written (`+` twice vs. `2 *` once) is the
whole gap between O(2ⁿ) and O(n).

Method 3, even written as double recursion, is saved by the **lookup table**: each n is
computed only once, so it also collapses to O(n).

## Measured results (n = 100)

| Rank | Method | Time/call | Complexity |
|------|--------|-----------|------------|
| 1 | Method 1  built-in `2**n` | ~0.5 µs | O(1)* |
| 2 | Method 2b linear recursion | ~19 µs | O(n) |
| 3 | Method 3  recursion + memo | ~57 µs | O(n) |
| — | Method 2a double recursion | N/A (cannot run) | O(2ⁿ) |

> Exact numbers vary by machine. Method 3 is a bit slower than Method 2b here because
> each measurement clears the cache and pays for dict lookups/writes; for a single
> computation, memoization has no advantage. Memoization pays off only when the *same* n
> is computed many times.

## Conclusion

```
fast ──────────────────────────────────► slow
Method 1 built-in  >  Method 2b / Method 3 linear  >>>  Method 2a exponential (fails)
```

- **Choosing the right algorithm matters most.** Methods 2a and 2b differ by a single
  line, yet that's the difference between "instant" and "runs forever".
- Built-in operators are usually highly optimized — use them when you can.
- Memoization (a lookup table) can rescue a repeated exponential recursion back to
  linear, but it only helps when there is repeated work to cache.
