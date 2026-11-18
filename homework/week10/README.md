# Week 10 — Monte Carlo: Random Points Beat Grids

Integrating a function means adding up its area (or volume). Two ways to do it numerically:

- **Riemann sum:** cut each axis into `k` pieces, evaluate `f` at the middle of every cell, add up value × cell volume.
- **Monte Carlo:** throw `N` random points in the box, average `f`, multiply by the box volume.

`monte_carlo.py` has both, plus derivatives and gradients. Needs numpy:

```
python3 monte_carlo.py
```

It prints a table and stops with an assertion error if any result is off.

## AI usage

This program and this README were written with AI assistance (Claude Code).

## What's in it

| Function | Job |
|---|---|
| `numeric_derivative(f, x)` | one variable, central difference (f(x+h) − f(x−h)) / 2h |
| `numeric_integral(f, a, b)` | one variable, midpoint sum |
| `mc_integral_1d(f, a, b, N)` | one variable, Monte Carlo |
| `gradient(f, x)` | n variables, central difference on each coordinate |
| `mc_integral(f, low, high, N)` | n variables, volume × mean of f at N random points |
| `integral(f, low, high, k)` | n variables, midpoint Riemann on a k-per-axis grid |

## Test function

f(x) = x1² + … + xn² on the box [0,1]ⁿ. Exact integral = n/3, exact gradient = 2x. The question says "low and high as 1", which would be a zero-size box, so low = 0, high = 1 is used.

## The answers

| dim | exact | Riemann | Monte Carlo (N = 100,000) |
|---|---|---|---|
| 1 | 0.3333 | 0.33333 | 0.33391 |
| 2 | 0.6667 | 0.66667 | 0.66854 |
| 5 | 1.6667 | 1.66581 | 1.66855 |
| 100 | 33.3333 | **infeasible** | 33.32859 |

## Why the Riemann sum dies at 100D

A grid with `k` points per axis in `n` dimensions has `kⁿ` cells. 1D with k = 100000 is fine, 2D with k = 1000 is 1 million cells, 5D with k = 22 is 5 million. But 100D with the tiniest grid, k = 2, is 2¹⁰⁰ ≈ 10³⁰ cells. No computer can visit those, so `integral` refuses and the demo prints "Riemann infeasible in 100D". This is the curse of dimensionality.

Monte Carlo costs `N × n` and its error shrinks like 1/√N whatever `n` is. So at 100D it gives 33.330 vs exact 33.333 in a tenth of a second. The price is that it is random: the error is a few thousandths, not 1e-12.

## How "correct" is judged

- Riemann: error under 1e-3. For 5D, k = 20 gives 1.04e-3 (midpoint rule loses h²/12 per axis), so k = 22 is used.
- Monte Carlo: error under 3 standard errors, where SE = sqrt(Var f / N). If it is bigger, that is a bug, not bad luck. The seed is fixed (`np.random.seed(0)`).

See `REPORT.md` for the full table, code review and security audit notes.
