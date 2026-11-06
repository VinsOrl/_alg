# Week 2 — Four Recurrences, Four Growth Rates

A recurrence relation describes the cost of a problem of size `n` in terms of the cost of smaller versions of the same problem. If an algorithm calls itself, its running time is naturally written this way. Solving the recurrence means turning it into a plain formula in `n`, and from that formula we read off the Big O.

Four recurrences, and each one lands in a different complexity class. `recurrences.py` has the closed forms and checks them against brute force:

```
python3 recurrences.py
```

It prints `ok` if every formula matches the recurrence on every size tested.

## The answers

| # | Recurrence | Exact solution | Big O |
|---|---|---|---|
| 1 | T(n) = T(n−1) + 8, T(1) = 1 | 8n − 7 | **O(n)** |
| 2 | T(n) = 2T(n−1) + 9, T(1) = 1 | 5·2ⁿ − 9 | **O(2ⁿ)** |
| 3 | T(n) = 2T(n/2) + 1, T(1) = 1 | 2n − 1 (for n = 2ᵏ) | **O(n)** |
| 4 | T(n) = T(n/2) + 1, T(1) = 1 | log₂n + 1 (for n = 2ᵏ) | **O(log n)** |

For #3 and #4 the input is cut in half each time, so the clean answer is for powers of 2 (n = 1, 2, 4, 8, …). For other `n` the Big O stays the same.

The method for all four is the same. Write out the first few terms, spot the pattern, then confirm it. Here it is for each.

---

## 1. T(n) = T(n−1) + 8 — a straight line

Each call does 8 units of work, then hands a problem one size smaller to itself. Unrolling it:

```
T(n) = T(n-1) + 8
     = T(n-2) + 8 + 8
     = T(n-3) + 8 + 8 + 8
     ...
     = T(1) + 8 + 8 + ... + 8        (n-1 eights)
```

We started at `n` and stopped at `1`, so that's `n − 1` steps, each adding 8:

> T(n) = 1 + 8(n − 1) = **8n − 7**

Sanity check with small values: T(1)=1, T(2)=9, T(3)=17, T(4)=25. Each term is 8 more than the last, which is what the recurrence says.

The constant 8 doesn't matter for Big O. Whether it's 8 or 800, the cost grows linearly, so this is **O(n)**. It's the shape of a simple loop that does a fixed amount of work per element.

---

## 2. T(n) = 2T(n−1) + 9 — doubling, and the +9 is a trap

Now the problem shrinks by one but the work **doubles**. That's the same trap as the double recursion in week 1: two calls on a size just one smaller.

A first attempt at unrolling gets messy because of the `+ 9`:

```
T(n) = 2T(n-1) + 9
     = 2(2T(n-2) + 9) + 9      = 4T(n-2) + 18 + 9
     = 8T(n-3) + 36 + 18 + 9
```

It works, but the pattern is annoying to read. There's a neater trick: **shift the sequence so the constant disappears.** Add 9 to both sides:

```
T(n) + 9 = 2T(n-1) + 18 = 2 * (T(n-1) + 9)
```

Look at what happened. If we define `S(n) = T(n) + 9`, then `S(n) = 2·S(n−1)`, a pure doubling with no constant. That one is easy: every step multiplies by 2.

- Starting point: S(1) = T(1) + 9 = 1 + 9 = 10
- After n−1 doublings: S(n) = 10 · 2ⁿ⁻¹ = 5 · 2ⁿ
- Shift back: T(n) = S(n) − 9 = **5·2ⁿ − 9**

Check: T(1)=1, T(2)=2·1+9=11, T(3)=2·11+9=31, T(4)=71, T(5)=151. The formula gives 5·4−9=11, 5·8−9=31, 5·16−9=71, 5·32−9=151. All match.

This is **O(2ⁿ)**. Each extra input element doubles the cost, so n = 50 is already around 5×10¹⁵ steps. It's not a practical algorithm past a few dozen elements.

---

## 3. T(n) = 2T(n/2) + 1 — split in half, but both halves still count

This is the divide-and-conquer shape: split the input in two halves, solve **both**, and spend a constant amount of work combining. To keep the math clean, let n = 2ᵏ so it halves evenly all the way down to 1.

Picture the recursion tree. Level by level:

| Level | Number of subproblems | Work per subproblem | Work at this level |
|---|---|---|---|
| 0 | 1 | 1 | 1 |
| 1 | 2 | 1 | 2 |
| 2 | 4 | 1 | 4 |
| … | … | … | … |
| k | 2ᵏ = n | 1 (the base case) | n |

The number of subproblems doubles each level, and so does the work. Adding all the levels:

> 1 + 2 + 4 + … + 2ᵏ = 2ᵏ⁺¹ − 1 = 2n − 1

So T(n) = **2n − 1**. Checking small powers of 2: T(1)=1, T(2)=2·1+1=3, T(4)=2·3+1=7, T(8)=2·7+1=15. The formula gives 1, 3, 7, 15.

This is **O(n)**. The tree has about `n` nodes in total, and each node does a constant amount of work. It's the same cost as walking the whole list once. Most of the work sits at the bottom level, where the `n` leaves are.

You can also get this from the Master theorem: a = 2, b = 2, f(n) = 1. Since f(n) = O(n^(log₂2 − ε)) = O(n^(1−ε)), the leaves dominate and T(n) = Θ(n).

---

## 4. T(n) = T(n/2) + 1 — cut in half and throw half away

This looks similar to #3, but there is only **one** recursive call. The problem is halved and we only continue with one half, like binary search. Again let n = 2ᵏ:

```
T(n) = T(n/2) + 1
     = T(n/4) + 1 + 1
     = T(n/8) + 1 + 1 + 1
     ...
     = T(1) + (1 + 1 + ... + 1)       (k ones)
```

How many halvings does it take to get from `n = 2ᵏ` down to 1? Exactly `k = log₂n`. So:

> T(n) = 1 + log₂n

Check: T(1)=1, T(2)=2, T(4)=3, T(8)=4, T(16)=5. Each doubling of `n` adds just one step.

This is **O(log n)**, the very fast end of the scale. Searching a sorted list of a million items takes about 20 steps, and a billion takes about 30.

---

## Putting the four side by side

| Recurrence | What it does | Growth |
|---|---|---|
| T(n−1) + 8 | one call, size shrinks by 1 | O(n) |
| 2T(n−1) + 9 | **two** calls, size shrinks by 1 | O(2ⁿ) |
| 2T(n/2) + 1 | two calls, size **halves** | O(n) |
| T(n/2) + 1 | **one** call, size halves | O(log n) |

Two things decide the growth rate, and they are easy to mix up:

1. **How fast does the problem shrink?** Subtracting 1 each time is slow, since you need about `n` levels. Halving is fast, since you only need about `log n` levels.
2. **How many calls do you make per level?** One call keeps the work thin. Two calls make it branch, and branching over many levels adds up quickly.

#2 is the dangerous combination: slow shrinking **and** branching. That's why it blows up to exponential while #1, which has the same slow shrinking but no branching, stays linear. #3 also branches, but because it halves, the tree only has log n levels and the total ends up merely linear.

---

## How the code checks the answers

`recurrences.py` defines each recurrence literally, exactly as written above, and compares it to the closed form:

- #1 and #2 are checked for n = 1 to 19.
- #3 and #4 are checked for n = 2⁰ to 2¹¹, because the formulas assume powers of 2.

If any closed form were off by even one, an `assert` would fail. With all four passing, the formulas above are not just plausible, they are verified.
