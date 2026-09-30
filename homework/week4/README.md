# Week 4 — The Iteration Method

This week is about the **iteration method**: a way to solve a problem by
guessing, improving the guess, and repeating until the guess stops changing.
This README explains the idea from scratch, walks through the exercise I chose
(solving `cos(x) = x`), and describes the other files in this folder.

---

## 1. What is the iteration method?

Some equations can't be rearranged into a neat `x = ...` formula. The iteration
method doesn't try to. Instead, you:

1. **Start with a guess** `x₀`. It doesn't need to be a good one.
2. **Apply an update rule** `g` to get a better guess: `x₁ = g(x₀)`.
3. **Repeat** with the new guess: `x₂ = g(x₁)`, `x₃ = g(x₂)`, and so on.
4. **Stop** when the guess barely changes between two steps. At that point
   `x ≈ g(x)`, and that `x` is the answer.

A value where `x = g(x)` is called a **fixed point**: plugging it into the rule
gives the same value back, so the process has settled there.

### An everyday analogy

Think of adjusting a shower's temperature. You turn the knob, feel the water,
and turn it a little again. Each adjustment is smaller than the last, and after
a few rounds the temperature stops changing. That settled position is the fixed
point. You never calculated it; you got there by repeating a simple correction.

### Does it always work?

No. Whether the guesses settle down depends on the rule `g`. Close to the
answer, the key quantity is the slope `|g'(x)|`:

- If `|g'(x)| < 1`, each step **shrinks** the distance to the answer, so the
  guesses converge.
- If `|g'(x)| > 1`, each step **stretches** the distance, so the guesses run
  away from the answer.

The smaller the slope, the faster it converges. This is why the same equation
can be solved quickly or slowly depending on how you write `g`. The class
example `iterative3.py` shows this: it tries three different rules for `√3`,
and they behave very differently.

---

## 2. My exercise: solving `cos(x) = x`

### The problem

Find the number `x` (in radians) where `cos(x)` equals `x` itself.

There is no algebra trick that isolates `x` in this equation, so we have to
approximate it. The answer is known as the **Dottie number**, about
**0.739085133215**. Fun fact: if you type any number into a calculator (in
radian mode) and keep pressing the `cos` button, you end up at this number.
That button-mashing *is* the iteration method.

### Method 1: plain fixed-point iteration, `x = cos(x)`

The equation already has the form `x = g(x)` with `g(x) = cos(x)`, so the rule
is simply: *take the cosine of your current guess.*

Starting from `x₀ = 1`:

| Step | Guess `x` | Change from previous |
|------|-----------|----------------------|
| 1 | 0.540302 | 0.460 |
| 2 | 0.857553 | 0.317 |
| 3 | 0.654290 | 0.203 |
| 4 | 0.793480 | 0.139 |
| 5 | 0.701369 | 0.092 |
| … | … | … |
| 69 | 0.739085133215 | < 0.000000000001 |

Two things to notice:

- **It zig-zags.** The guesses jump above and below the answer
  (0.54 → 0.86 → 0.65 → 0.79 …). That happens because the slope of `cos(x)`
  near the answer is negative: a guess that is too low produces the next guess
  too high, and the other way around.
- **It is slow.** Each change is only about two-thirds of the one before
  (0.460 → 0.317 → 0.203 …). The exact factor is `|g'(x)| = sin(0.739) ≈ 0.674`.
  Because it is below 1, the method converges. Because it is not far below 1, it
  takes **69 steps** to reach 12 decimal places.

### Method 2: Newton's method

Newton's method is a smarter iteration rule. Rewrite the problem as finding
where `f(x) = x − cos(x)` equals zero. At the current guess, draw the tangent
line to `f` and take the point where that line crosses zero as the next guess:

```
x_next = x − f(x) / f'(x)  =  x − (x − cos x) / (1 + sin x)
```

Starting again from `x₀ = 1`:

| Step | Guess `x` | Change from previous |
|------|-----------|----------------------|
| 1 | 0.750363867840 | 0.25 |
| 2 | 0.739112890911 | 0.011 |
| 3 | 0.739085133385 | 0.000028 |
| 4 | 0.739085133215 | 0.00000000017 |
| 5 | 0.739085133215 | 0 |

Done in **5 steps**. The changes shrink faster and faster, and the number of
correct digits roughly **doubles** each step (1 → 4 → 9 → 12+). That is called
*quadratic convergence*.

### Why is Newton so much faster?

Newton's method is still a fixed-point iteration `x = g(x)`. Its `g` is just
built so that its slope at the answer is exactly **0**. Recall the rule from
section 1: a smaller slope means faster convergence. Method 1 has a slope of
0.674, so every step keeps about 67% of the error. Newton has a slope of 0, so
each step's error is roughly the *square* of the previous one, which shrinks
dramatically once it's small.

| | Fixed point `x = cos(x)` | Newton |
|---|---|---|
| Rule | `cos(x)` | `x − (x − cos x)/(1 + sin x)` |
| Slope at the answer | ≈ 0.674 | 0 |
| Type of convergence | linear (fixed % per step) | quadratic (digits double) |
| Steps needed | 69 | 5 |
| Work per step | 1 cosine | 1 cosine + 1 sine + a division |

The trade-off: Newton does a bit more work per step and needs the derivative of
`f`, but it needs far fewer steps.

### How the code works

`cos_fixed_point.py` is short. It uses only Python's built-in `math` module, so
there is nothing to install.

- `iterate(g, x0, tol, max_iter)` is the general loop. It keeps computing
  `x = g(x)` until the change is smaller than `tol` (default `1e-12`), and
  returns the answer plus the number of steps. If the guesses still haven't
  settled after `max_iter` steps, it raises an error instead of running forever.
- `fixed` and `newton` are the two update rules, each one line long.
- The main block runs both methods, prints the first 10 steps of each so you
  can watch them converge, and then **checks** each answer with
  `assert abs(cos(x) - x) < 1e-10`. If either method gave a wrong answer, the
  script would stop with an error.

### Run it

```bash
python3 cos_fixed_point.py
```

```
Fixed point  x = cos(x)
    1  x = 0.540302305868  |dx| = 4.60e-01
    2  x = 0.857553215846  |dx| = 3.17e-01
    3  x = 0.654289790498  |dx| = 2.03e-01
  ...
  -> x = 0.739085133215 after 69 steps, cos(x) - x = 6.5e-13

Newton
    1  x = 0.750363867840  |dx| = 2.50e-01
    2  x = 0.739112890911  |dx| = 1.13e-02
    3  x = 0.739085133385  |dx| = 2.78e-05
    4  x = 0.739085133215  |dx| = 1.70e-10
    5  x = 0.739085133215  |dx| = 0.00e+00
  -> x = 0.739085133215 after 5 steps, cos(x) - x = 0.0e+00
```

How to read it:

- `x` is the current guess.
- `|dx|` is how much the guess changed in that step. The loop stops once it
  drops below `1e-12`.
- `cos(x) - x` at the end shows how close the final answer is to satisfying the
  equation. `0` or a tiny number like `6.5e-13` means it is correct to about
  12 decimal places.

---

## 3. Documentation for `iter_framework.py`

The second part of the assignment is documentation for `iter_framework.py`,
which is in [`iter_framework_doc.md`](iter_framework_doc.md).

In short: that program shows that nine well-known algorithms all fit the same
"guess, update, check" loop from section 1. They are Newton's method,
Gauss-Seidel, power iteration, the QR algorithm, Runge-Kutta, PageRank,
K-Means, EM, and plain fixed-point iteration. The loop is written once as
`generic_iterator`, and each algorithm only supplies its own update rule and
its own stopping condition. The doc explains each one, why it converges, and
where it can go wrong.

---

## 4. Supplement: the 2024 Nobel Prize in Physics

`iter_nobel_nn.py` is reading material from class. It uses the same
`generic_iterator` for the two neural-network memory models behind the 2024
Nobel Prize in Physics:

- **Hopfield network:** repairs a damaged pattern by updating it until it
  stops changing (a fixed point, just like in section 1).
- **RBM with CD-k (Hinton):** runs exactly `k` sampling steps back and forth
  between the visible and hidden layers.

---

## 5. Files in this folder

| File | What it is |
|------|------------|
| `cos_fixed_point.py` | **My exercise.** Solves `cos(x) = x` with fixed-point iteration and with Newton's method. Standard library only. |
| `iterative3.py` | Reference example from class: three different iteration rules for `√3`. |
| `iter_framework.py` | From class: nine classic algorithms written on one shared `generic_iterator`. |
| `iter_framework_doc.md` | **My documentation** for `iter_framework.py`. |
| `iter_nobel_nn.py` | Supplement from class: Hopfield network and RBM CD-k on the same framework. |
| `README.md` | This file. |

## Agent Use
Claude Code
