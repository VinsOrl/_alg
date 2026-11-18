# Week 10 Report: Monte Carlo

Run: `python3 monte_carlo.py` (needs numpy; seed fixed with `np.random.seed(0)`). All asserts in the demo pass.

## Results (f = x1² + … + xn² on [0,1]ⁿ, exact = n/3, MC with N = 100,000)

| dim | k per axis | exact | Riemann | Riemann err | Riemann time | MC | MC err | 3×SE | MC time |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 100000 | 0.3333 | 0.33333 | 8.3e-12 | 0.00s | 0.33391 | 5.8e-04 | 2.8e-03 | 0.00s |
| 2 | 1000 | 0.6667 | 0.66667 | 1.7e-07 | 0.03s | 0.66854 | 1.9e-03 | 4.0e-03 | 0.00s |
| 5 | 22 | 1.6667 | 1.66581 | 8.6e-04 | 0.39s | 1.66855 | 1.9e-03 | 6.3e-03 | 0.01s |
| 100 | none | 33.3333 | infeasible | - | - | 33.32859 | 4.7e-03 | 2.8e-02 | 0.10s |

Judging rules (set beforehand): Riemann within 1e-3, MC within 3 standard errors. All met; no bugs found, seed not tuned. SE = sqrt(n·4/45)/sqrt(N), since Var[x²] on [0,1] is 1/5 − 1/9 = 4/45.

## Test results

The demo is the test (plain asserts; every line prints OK or the run stops). Covers: derivative and integral of x² and sin, MC 1D for x² and sin, gradient at [1,2,3], MC 2D, and the 1/2/5/100D table. Full run output:

```
OK   d/dx x^2 at 3: 6.000000 (exact 6.000000, tol 1e-03)
OK   int x^2 on [0,1]: 0.333333 (exact 0.333333, tol 1e-03)
OK   d/dx sin at 0: 1.000000 (exact 1.000000, tol 1e-03)
OK   int sin on [0,pi]: 2.000000 (exact 2.000000, tol 1e-03)
OK   MC int x^2 on [0,1]: 0.333042 (exact 0.333333, tol 3e-03)
OK   MC int sin on [0,pi]: 1.999706 (exact 2.000000, tol 9e-03)
gradient at [1,2,3]: [2. 4. 6.] exact [2 4 6]
OK   MC int x^2+y^2 on [0,1]^2: 0.663309 (exact 0.666667, tol 4e-03)

Items 5 and 6: Riemann and Monte Carlo by dimension

 dim     exact    Riemann     R err  R time         MC    MC err     3*SE  MC time
   1    0.3333    0.33333   8.3e-12   0.00s    0.33391   5.8e-04  2.8e-03    0.00s
   2    0.6667    0.66667   1.7e-07   0.03s    0.66854   1.9e-03  4.0e-03    0.00s
   5    1.6667    1.66581   8.6e-04   0.38s    1.66855   1.9e-03  6.3e-03    0.01s
Riemann infeasible in 100D (k=2 -> 2^100 points)
 100   33.3333 infeasible         -       -   33.32859   4.7e-03  2.8e-02    0.12s
exit code: 0
```

## Notes

- **low/high.** The updated questions say low=0, high=1, which is what is used (the old wording "both as 1" was a typo).
- **AI disclosure.** Stated in the `monte_carlo.py` docstring and in a README section, as the questions require.
- **Spec change.** Code updated after the revised specs/questions: added sin tests, gradient at [1,2,3], 2D MC test, and the AI statement.
- **5D k = 22, not 20.** The midpoint rule loses h²/12 per axis on x², so 5D with k = 20 has error 1.04e-3, just over the 1e-3 rule. k = 22 gives 8.6e-4 (5.15M points). Chosen before the final run.
- **100D Riemann is infeasible.** A grid needs kⁿ points. Even k = 2 gives 2¹⁰⁰ ≈ 1.3e30 points, which cannot be stored or looped over in any time or memory. `integral` raises `ValueError` and the demo prints "Riemann infeasible in 100D". Monte Carlo cost is N·n, independent of a grid, and its error (~1/√N) does not depend on dimension. That is why it works at 100D in 0.1 s.
- Functions are vectorised: `f` maps shape (..., n) to (...). The test `f` uses `np.sum(x**2, axis=-1)`.