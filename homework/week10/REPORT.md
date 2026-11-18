# Week 10 Report: Monte Carlo

Run: `python3 monte_carlo.py` (needs numpy; seed fixed with `np.random.seed(0)`). All asserts in the demo pass.

## Results (f = x1² + … + xn² on [0,1]ⁿ, exact = n/3, MC with N = 100,000)

| dim | k per axis | exact | Riemann | Riemann err | Riemann time | MC | MC err | 3×SE | MC time |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 100000 | 0.3333 | 0.33333 | 8.3e-12 | 0.00s | 0.33564 | 2.3e-03 | 2.8e-03 | 0.00s |
| 2 | 1000 | 0.6667 | 0.66667 | 1.7e-07 | 0.03s | 0.66331 | 3.4e-03 | 4.0e-03 | 0.00s |
| 5 | 22 | 1.6667 | 1.66581 | 8.6e-04 | 0.39s | 1.67165 | 5.0e-03 | 6.3e-03 | 0.01s |
| 100 | none | 33.3333 | infeasible | - | - | 33.32994 | 3.4e-03 | 2.8e-02 | 0.10s |

Other checks: derivative of x² at 3 = 6.0000000000393 (exact 6); 1D integral 0.33333333333 (exact 1/3); 1D MC 0.33304; gradient at [0.5, 1, 2, -3] = [1, 2, 4, -6] = 2x.

Judging rules (set beforehand): Riemann within 1e-3, MC within 3 standard errors. All met; no bugs found, seed not tuned. SE = sqrt(n·4/45)/sqrt(N), since Var[x²] on [0,1] is 1/5 − 1/9 = 4/45.

## Notes

- **low/high typo.** The question says "both low and high as 1", which gives a zero-volume box (integral 0). I used low = 0, high = 1.
- **5D k = 22, not 20.** The midpoint rule loses h²/12 per axis on x², so 5D with k = 20 has error 1.04e-3, just over the 1e-3 rule. k = 22 gives 8.6e-4 (5.15M points). Chosen before the final run.
- **100D Riemann is infeasible.** A grid needs kⁿ points. Even k = 2 gives 2¹⁰⁰ ≈ 1.3e30 points, which cannot be stored or looped over in any time or memory. `integral` raises `ValueError` and the demo prints "Riemann infeasible in 100D". Monte Carlo cost is N·n, independent of a grid, and its error (~1/√N) does not depend on dimension. That is why it works at 100D in 0.1 s.
- Functions are vectorised: `f` maps shape (..., n) to (...). The test `f` uses `np.sum(x**2, axis=-1)`.