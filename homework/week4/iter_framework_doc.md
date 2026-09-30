# Documentation for `iter_framework.py`

This document explains what `iter_framework.py` does, how its central function
works, and what each of its nine example algorithms is doing. You don't need to
know any of these algorithms beforehand. Each section starts with the problem in
plain words and then shows how the code solves it.

---

## 1. The big idea: one loop, many algorithms

The program's main point is that many famous algorithms from different areas
(math, linear algebra, physics simulation, web search, machine learning) all
share the same skeleton:

```
start with a guess
repeat:
    improve the guess using some rule
until the guess is good enough
```

In math notation: `x₁ = g(x₀)`, `x₂ = g(x₁)`, `x₃ = g(x₂)`, …, stopping when some
condition is met.

Only two things change from one algorithm to the next:

| Piece | What it answers | Name in the code |
|-------|-----------------|------------------|
| **The update rule** `g` | "Given my current guess, what's a better one?" | `transition_func` |
| **The stopping rule** | "Is this good enough to stop?" | `is_converged` |

So instead of writing nine separate loops, the program writes the loop **once**
(`generic_iterator`) and hands it a different update rule and stopping rule for
each algorithm.

The "guess" is called the **state**, and it doesn't have to be a single number.
Depending on the algorithm it is a number, a list of numbers (vector), a table
of numbers (matrix), or a pair of values (tuple). The loop doesn't care what the
state is. It just keeps passing it to the update rule.

---

## 2. The engine: `generic_iterator`

```python
def generic_iterator(transition_func, is_converged, initial_state, max_iter=1000):
    state = initial_state
    for iteration in range(max_iter):
        next_state = transition_func(state)
        if is_converged(state, next_state, iteration):
            return next_state, iteration + 1
        state = next_state
    print("  [警告] 達到最大迭代次數仍未完全收斂")
    return state, max_iter
```

### What goes in

| Parameter | What it is |
|-----------|------------|
| `transition_func` | A function that takes the current state and returns the next one. This is the update rule `g`. |
| `is_converged` | A function that takes `(old_state, new_state, iteration_number)` and returns `True` when it's time to stop. |
| `initial_state` | The starting guess. |
| `max_iter` | A safety limit (default 1000) so a method that never settles can't loop forever. |

### What comes out

A pair: `(final_state, number_of_steps)`.

### Step by step, in plain words

1. Start with the initial guess.
2. Use the update rule to compute the next guess.
3. Ask the stopping rule: "old guess vs new guess, are we done?"
   - **Yes** → return the new guess and how many steps it took.
   - **No** → the new guess becomes the current guess; go back to step 2.
4. If 1000 rounds pass without stopping, print a warning (the Chinese message
   means "reached the maximum number of iterations without fully converging")
   and return the last guess.

### Details worth knowing

- **Why the stopping rule gets both old and new.** Most algorithms stop when
  the guess barely changes, and you can only measure a change by comparing two
  guesses. It also receives the step number, for algorithms that just run a
  fixed number of steps.
- **Stopping rules differ between algorithms.** Most here use "the change is
  smaller than 0.000001" (`1e-6`). The RK4 demo stops when simulated time
  reaches a target. The QR demo checks whether the matrix has become almost
  diagonal, without comparing it to the old one at all.
- **"Stopped changing" is not the same as "correct."** A small change only
  means the method has slowed down. A method that crawls slowly toward the
  answer can take a tiny step while still being noticeably off. For
  fast-converging methods (most of the ones here) this isn't a problem, but it's
  worth knowing.
- **A small quirk on timeout.** If the limit is hit, the function returns the
  guess from the previous round and discards the one it just computed. This
  only matters when something has already gone wrong.

---

## 3. Quick overview of all nine demos

| # | Demo | What it solves | The state | Update rule (short) | Stops when | Steps |
|---|------|----------------|-----------|---------------------|------------|-------|
| 1 | Fixed-point | A 2-variable equation `X = g(X)` | 2 numbers | apply `g` | change < 1e-6 | 23 |
| 2 | Newton | Root of `x² − 4 = 0` | 1 number | follow the tangent line | change < 1e-6 | 5 |
| 3 | Gauss-Seidel | 3 linear equations, 3 unknowns | 3 numbers | solve each equation for its own variable | biggest change < 1e-6 | 9 |
| 4 | Power iteration | Largest eigenvalue of a matrix | direction (unit vector) | multiply by matrix, rescale | vector stops moving | 17 |
| 5 | QR algorithm | All eigenvalues of a matrix | a 3×3 matrix | factor as Q·R, multiply back as R·Q | off-diagonal ≈ 0 | 19 |
| 6 | RK4 | A differential equation over time | `(time, value)` | one careful time step | time reaches 2 | 10 |
| 7 | PageRank | Importance of 4 web pages | 4 scores | redistribute scores along links | change < 1e-6 | 15 |
| 8 | K-Means | Group 30 points into 2 clusters | 2 cluster centres | assign points, move centres | centres stop moving | 4 |
| 9 | EM (two coins) | Bias of two coins you can't tell apart | 2 probabilities | guess which coin, re-estimate | both change < 1e-6 | 16 |

The rest of this document goes through them one at a time.

---

## 4. The nine demos explained

### 4.1 Fixed-point iteration — `demo_fixed_point`

**The problem.** Find two numbers `X = (X₀, X₁)` that satisfy

```
X₀ = 0.5·X₀ − 0.2·X₁ + 0.3
X₁ = 0.2·X₀ + 0.5·X₁ + 0.4
```

**How it's solved.** The equations already have the form `X = g(X)`. So start
at `(0, 0)`, plug the current values into the right-hand side, and use the
result as the new values. Repeat.

**Why it settles down.** Each round, the distance to the true answer gets
multiplied by about 0.54. (Technically: the eigenvalues of the coefficient
matrix are `0.5 ± 0.2i`, whose size is √0.29 ≈ 0.54.) Because that factor is
below 1, the error shrinks every round, roughly halving each time.

**Result.** `(0.24138, 0.896552)` after 23 steps. You can check it: solving the
equations by hand gives exactly `(7/29, 26/29)`.

---

### 4.2 Newton's method — `demo_newton`

**The problem.** Find `x` such that `x² − 4 = 0` (the answer is 2).

**How it's solved.** Start at `x = 1`. At the current guess, draw the tangent
line to the curve `f(x) = x² − 4` and jump to where that line hits zero. That
point is the next guess:

```
x_next = x − f(x) / f'(x) = x − (x² − 4) / (2x)
```

**Why it's so fast.** Near the answer, Newton's method roughly **doubles the
number of correct digits** every step (called quadratic convergence). That's
why it only needs 5 steps.

**Watch out.** The starting guess decides which answer you get: start positive
and you reach `2`, start negative and you reach `−2`. Starting at exactly `0`
crashes, because the tangent line there is flat and the formula divides by zero.

**Result.** `x = 2.000000` after 5 steps.

---

### 4.3 Gauss-Seidel — `demo_gauss_seidel`

**The problem.** Solve three equations with three unknowns:

```
 4x₀ −  x₁        =  7
 −x₀ + 4x₁ −  x₂  =  2
       −x₁ + 4x₂  = 13
```

**How it's solved.** Start with all unknowns at 0. Go through the equations one
by one and solve each for "its own" variable, treating the others as known.
Equation 0 gives a new `x₀`, equation 1 gives a new `x₁`, and so on. One full
pass over all three equations is one step.

**The trick that makes it Gauss-Seidel.** When computing `x₁`, it immediately
uses the `x₀` that was **just updated in this same pass**, not last pass's value.
In the code, `x_new` is both read and written inside the loop, which is what
makes this happen. (The simpler Jacobi method waits and uses only old values;
Gauss-Seidel usually converges faster.) The `x.copy()` at the start keeps the
old state untouched so the stopping rule can compare old and new.

**Why it settles down.** In every row, the number on the diagonal (4) is bigger
than the other numbers in that row combined (1 + 1). A matrix like that is
called *diagonally dominant*, and Gauss-Seidel is guaranteed to converge for it.

**Result.** `x = (2.25, 2, 3.75)` after 9 steps. Plug it in: `4·2.25 − 2 = 7` ✓.

---

### 4.4 Power iteration — `demo_power_iteration`

**The problem.** Every square matrix has special directions called
*eigenvectors*: when the matrix multiplies such a vector, the vector only gets
stretched, not turned. The stretch factor is its *eigenvalue*. We want the
**largest** one.

**How it's solved.** Start with a random vector. Multiply it by the matrix, then
shrink it back to length 1 (otherwise it would grow without limit). Repeat.

**Why it works.** Any vector is a mix of the eigenvectors. Each multiplication
stretches every part of that mix by its own eigenvalue, so the part belonging
to the biggest eigenvalue grows fastest. After enough rounds, it's the only part
left that matters, and the vector points along that eigenvector. The bigger the
gap between the largest and second-largest eigenvalue, the faster this happens.

**Getting the eigenvalue.** Once the vector `v` has settled, the eigenvalue is
`vᵀ·A·v` (the Rayleigh quotient): how much `A` stretches `v`.

**Watch out.** If the largest eigenvalue were negative, the vector would flip
direction every step and the stopping rule would never say "done". This
matrix's eigenvalues are all positive, so that doesn't happen here.

**Result.** Largest eigenvalue `4.721570` after 17 steps.

---

### 4.5 QR algorithm — `demo_qr_algorithm`

**The problem.** Find **all** the eigenvalues of a 3×3 matrix, not just the
biggest.

**How it's solved.** Each step:
1. Split the matrix into two pieces, `A = Q·R` (the QR decomposition: `Q` is a
   rotation and `R` is upper-triangular).
2. Multiply them back in the **opposite order**: `A_next = R·Q`.

In the code this is the one-liner `np.dot(*reversed(np.linalg.qr(Ak)))`:
`np.linalg.qr` returns `(Q, R)`, `reversed` flips it to `(R, Q)`, and `np.dot`
multiplies them.

**Why it works.** Swapping the order never changes the eigenvalues (`R·Q` is
just `A` seen from a rotated viewpoint). But each swap moves the numbers off the
diagonal closer to zero. Eventually the matrix is almost diagonal, and for a
diagonal matrix the eigenvalues are simply the numbers on the diagonal.

**The stopping rule** adds up the absolute values of everything *off* the
diagonal and stops when that total is below `1e-6`.

**Watch out.** This works nicely for symmetric matrices (like this one). For
some non-symmetric matrices the off-diagonal part never fully disappears, and
the loop would run until the 1000-step limit. Real libraries add extra tricks
("shifts") to make it faster and more robust. This is the plain textbook
version.

**Result.** Eigenvalues `5.732051, 2.267949, 1.0` after 19 steps. These are
exactly `2 + √3`, `2 − √3` and `1`.

---

### 4.6 Runge-Kutta 4 (RK4) — `demo_rk4`

**The problem.** We know how fast a quantity `y` changes over time,
`dy/dt = y − t + 1`, and its starting value `y(0) = 1`. What is `y` at time
`t = 2`?

**How it's solved.** Walk forward in time in small steps of `h = 0.2`. The
naive approach would be "new y = old y + slope × h", but the slope changes
during the step. RK4 measures the slope four times (at the start, twice in the
middle, and at the end of the step) and takes a weighted average:

```
k1 = slope at the start
k2 = slope at the middle, using k1 to get there
k3 = slope at the middle again, using k2 (a better estimate)
k4 = slope at the end, using k3
new y = old y + h/6 · (k1 + 2·k2 + 2·k3 + k4)
```

The state is the pair `(time, y)`, and each step moves time forward by 0.2.

**A different kind of stopping rule.** This isn't searching for a fixed answer,
so "stop when it stops changing" makes no sense. It stops when time reaches 2.
The `− 1e-9` in the code handles a floating-point quirk: adding 0.2 ten times
gives `1.9999999999999998` on a computer, not exactly `2.0`.

**How accurate is it?** The exact solution is `y = eᵗ + t`, so
`y(2) = e² + 2 ≈ 9.389056`. RK4 gets `9.388889`, off by about 0.00017. A
smaller `h` would be more accurate (RK4's error shrinks with `h⁴`, so halving
`h` makes the error roughly 16 times smaller).

**Result.** `y(2) ≈ 9.388889` after 10 steps.

---

### 4.7 PageRank — `demo_pagerank`

**The problem.** Four web pages link to each other. Which pages are most
"important"? This is the idea Google started with.

**The random surfer.** Picture someone clicking links at random, forever. The
share of time they spend on each page is that page's importance. Pages that many
other pages link to, especially important ones, get visited more.

**How it's solved.**
- `M` is the link matrix. Column `j` says where a surfer on page `j` goes next:
  its links, split evenly. (Each column adds up to 1.)
- With probability `d = 0.85` the surfer follows a link. Otherwise (15%) they get
  bored and jump to a random page. Combining both gives the "Google matrix"
  `G = 0.85·M + 0.15/4 · (all ones)`.
- Start with equal scores `(0.25, 0.25, 0.25, 0.25)`. Each step, pass the scores
  along the links: `r_next = G · r`. Repeat until the scores stop changing.

**Why it settles down.** The 15% random jump guarantees a single stable answer
and makes the error shrink by at least a factor of 0.85 each step. The scores
always add up to 1, because nobody leaves the system.

This is actually power iteration (4.4) again, applied to `G`. Its largest
eigenvalue is exactly 1, which is why no rescaling is needed.

**Result.** Scores `(0.3246, 0.2251, 0.2251, 0.2251)` after 15 steps. Page 0 is
the most important, and the other three tie.

---

### 4.8 K-Means clustering — `demo_kmeans`

**The problem.** We have 30 points on a plane. We (secretly) generated 15 around
`(2, 2)` and 15 around `(−2, −2)`. Can the algorithm find the two groups without
being told?

**How it's solved.** Keep two "centres", starting at the first two data points.
Each step:
1. **Assign:** give every point to its nearest centre.
2. **Update:** move each centre to the average position of the points assigned
   to it.

Repeat until the centres stop moving.

**Why it stops.** Both steps can only make the total "distance from points to
their centre" smaller, never bigger. There are only finitely many ways to split
the points into groups, so it must settle eventually.

**Watch out.**
- It finds *a* good grouping, not necessarily the *best* one. Different
  starting centres can give different results.
- If a centre ends up with no points at all, the average of zero points is
  `NaN` ("not a number"). The loop can never finish after that. It doesn't happen
  with this data, but a real program should handle it.

**Result.** Centres at about `(−2.11, −2.13)` and `(1.83, 1.80)` after only 4
steps, close to the true `(−2, −2)` and `(2, 2)`.

---

### 4.9 EM algorithm: two coins — `demo_em_two_coin`

**The problem.** There are two coins, A and B, each with an unknown chance of
landing heads. Someone ran 5 experiments. In each one they secretly picked a
coin and flipped it 10 times. We only see the heads/tails counts:

```
5H 5T,  9H 1T,  8H 2T,  4H 6T,  7H 3T
```

We are never told which coin was used. Estimate each coin's chance of heads.

**Why it's tricky.** If we knew which coin made each experiment, we would just
count heads per coin. If we knew each coin's bias, we could guess which coin
made each experiment. We know neither. EM gets around this by alternating
between the two.

**How it's solved.** Start with a rough guess, `θ_A = 0.6`, `θ_B = 0.5`. Each
step:
1. **E-step (Expectation):** for each experiment, ask "how likely is this result
   from coin A vs coin B, given my current guesses?" For example, `9H 1T` looks
   much more like the coin with the higher bias. Turn that into a split, such as
   "80% coin A, 20% coin B".
2. **M-step (Maximization):** re-estimate each coin's bias from those splits. A
   coin gets 80% of that experiment's heads and flips, and so on, then
   `θ = its weighted heads / its weighted flips`.

Repeat until both estimates stop changing.

**Why it works.** Each round is guaranteed not to make the estimates explain the
data any worse, so they keep improving until they settle. As with K-Means, the
result can depend on the starting guess. In fact, K-Means is a "hard" version
of EM: every point goes 100% to one group instead of being split by
probabilities.

**Small safety check.** The line `if (l_A + l_B) > 0 else 0.5` avoids a
division by zero in the (very unlikely) case that both probabilities round to 0.

**Result.** `θ_A ≈ 0.7968`, `θ_B ≈ 0.5196` after 16 steps. One coin is
noticeably biased toward heads, and the other is close to fair.

---

## 5. Running the program

You need Python 3 and `numpy` (`pip install numpy`). Then:

```bash
python3 iter_framework.py
```

It runs all nine demos in order. Each prints its name, its result, and how many
steps (`耗時 N 次迭代` = "took N iterations") it needed:

```
=========================================================
   全系列經典迭代演算法 - 統一抽象框架展示 (Unified Framework)
=========================================================

--- 1. 二維不動點迭代法 (Fixed-Point Iteration) ---
結果: [0.24138  0.896552] (耗時 23 次迭代)

--- 2. 牛頓法求根 (Newton's Method: x^2 - 4 = 0) ---
結果: 根 x = 2.000000 (耗時 5 次迭代)

--- 3. 高斯-賽得爾法 (Gauss-Seidel Linear Solver) ---
結果: x = [2.25 2.   3.75] (耗時 9 次迭代)

--- 4. 冪次迭代法 (Power Iteration: SVD / 主特徵向量) ---
結果: 最大特徵值 = 4.721570 (耗時 17 次迭代)

--- 5. QR 演算法 (QR Algorithm: 計算所有特徵值) ---
結果: 所有特徵值 = [5.732051 2.267949 1.      ] (耗時 19 次迭代)

--- 6. 龍格-庫塔法 (RK4 ODE Solver: dy/dt = y - t + 1) ---
結果: 於 t = 2.0 時, y = 9.388889 (耗時 10 步)

--- 7. PageRank (Power Iteration 隨機衝浪者模型) ---
結果: 網頁權重分佈 = [0.3246 0.2251 0.2251 0.2251] (耗時 15 次迭代)

--- 8. K-Means 聚類 (Hard EM 演算法) ---
結果: 最終分群中心 = 
[[-2.1143 -2.128 ]
 [ 1.826   1.7977]] (耗時 4 次迭代)

--- 9. EM 演算法 (Two-Coin Problem 潛在變數估計) ---
結果: 估計硬幣機率 Theta_A = 0.7968, Theta_B = 0.5196 (耗時 16 次迭代)
```

### Checking the answers

Where an exact answer is known, the program's result matches it:

| Demo | Exact answer | Program |
|------|--------------|---------|
| Fixed-point | `(7/29, 26/29) ≈ (0.24138, 0.89655)` | `(0.24138, 0.896552)` ✓ |
| Newton | `2` | `2.000000` ✓ |
| Gauss-Seidel | `(2.25, 2, 3.75)` | `(2.25, 2, 3.75)` ✓ |
| QR | `2 + √3, 2 − √3, 1` | `5.732051, 2.267949, 1.0` ✓ |
| RK4 | `e² + 2 ≈ 9.389056` | `9.388889` (off by 0.00017, due to step size) |

---

## 6. Related file

`iter_nobel_nn.py` reuses the same `generic_iterator` for the two neural-network
memory models behind the 2024 Nobel Prize in Physics. The Hopfield network
repairs a damaged pattern by updating it until it stops changing (a fixed
point, like demo 1). The RBM's CD-k training step runs exactly `k` rounds of
sampling (a fixed step count, like the RK4 demo).
