# Week 5 — Recursion, Functional Programming, Lambda Calculus

This week is about **recursion**: solving a problem by handing a smaller copy
of the same problem back to yourself, again and again, until the copy is so
small the answer is obvious. It's also about **functional programming**, a
style where functions are values you pass around and where you don't use
loops or modify variables.

I solved three exercises. Each one is a single Python file that uses only the
standard library and checks its own answers with `assert`:

1. **Tower of Hanoi** (`hanoi.py`), once with recursion and once without.
2. **Symbolic differentiation** (`sym_diff.py`): a recursive `sym_diff(expr)`
   that finds derivatives the way you would on paper.
3. **Hand-made `map`, `filter` and `reduce`** (`fp_bubble.py`), used to build a
   bubble sort that contains no loops at all.

---

## What is recursion, really?

A recursive function is one that **calls itself**. That sounds circular, but
it works as long as two things are true:

1. **There is a base case.** Some input is so simple that the answer is known
   immediately and nothing needs to be called. For example, "an empty list
   needs no sorting."
2. **Every call gets closer to the base case.** Each time the function calls
   itself, the input must be smaller: one fewer disk, a shorter list, a
   smaller piece of a formula.

### An everyday analogy

Imagine you're standing in a long queue and want to know your position, but
you can't see the front. You ask the person in front of you, "What number are
you?" They don't know either, so they ask the person in front of *them*. The
question travels to the front, where the first person says "I'm number 1"
(that's the base case). The answers then travel back: "I'm 2", "I'm 3", and so
on, until someone tells you their number and you add 1.

Nobody did anything clever. Each person only solved "my number = the number
in front of me + 1". Recursion is exactly that: **trust that the smaller
problem gets solved, and only handle your own small step.**

### What does the computer actually do?

Every time a function is called, Python creates a **stack frame**, a small
note that remembers the function's local variables and where to return to.
Recursive calls pile those notes on top of each other (the *call stack*). When
the base case returns, the notes are removed one by one, in reverse order.

Python only allows about 1000 frames by default. That is why very deep
recursion fails with `RecursionError`. It also means any recursion can be
rewritten with a loop and a list that plays the role of the call stack. That's
how I solve Hanoi without recursion in section 1.

---

## 1. Tower of Hanoi (`hanoi.py`)

### The puzzle

There are three pegs, called **A**, **B** and **C**, and `n` disks of
different sizes. At the start, all disks sit on peg A, largest at the bottom
and smallest on top, like a pyramid. The goal is to move the whole pile to
peg C. There are two rules:

1. You may move only **one disk at a time**, always the top disk of a peg.
2. You may **never place a larger disk on top of a smaller one**.

Peg B is the helper, or spare, peg.

### The recursive idea

Trying to plan all the moves at once quickly gets confusing. Instead, think
only about the **largest disk**, disk `n`.

To move disk `n` from A to C, everything sitting on top of it (the `n − 1`
smaller disks) has to be out of the way. And it can't be on C, because that's
where disk `n` is going. So those `n − 1` disks must be on B. That gives a
three-step plan:

1. Move the top `n − 1` disks from **A to B**, using C as the helper.
2. Move disk `n` from **A to C**. This is one single move.
3. Move the `n − 1` disks from **B to C**, using A as the helper.

Steps 1 and 3 are the *same puzzle* with one fewer disk and different peg
names. We don't work out how they're done; we let recursion solve them. The
base case is `n = 0`: no disks, so there's nothing to do.

This is the whole solution in code:

```python
def hanoi_rec(n, src='A', dst='C', aux='B'):
    if n <= 0:
        return []
    return hanoi_rec(n - 1, src, aux, dst) + [(n, src, dst)] + hanoi_rec(n - 1, aux, dst, src)
```

It returns a list of moves. Each move is a tuple `(disk, from_peg, to_peg)`.
I used `n <= 0` instead of `n == 0` so that a negative `n` safely returns no
moves instead of recursing forever.

### Walking through `n = 3`

```
move disk 1 from A to C
move disk 2 from A to B      <- steps 1-3: the top 2 disks have moved A -> B
move disk 1 from C to B
move disk 3 from A to C      <- the big move: disk 3 goes straight to C
move disk 1 from B to A
move disk 2 from B to C      <- the last 3 moves: the 2 disks move B -> C
move disk 1 from A to C
```

The output has exactly the three-part shape described above: 3 moves to clear
the way, 1 big move, then 3 moves to rebuild the pile on top.

### Formula: how many moves does it take?

Let `T(n)` be the number of moves needed for `n` disks. The plan above uses
`T(n − 1)` moves, then 1 move, then `T(n − 1)` moves again:

```
T(0) = 0
T(n) = 2 · T(n − 1) + 1
```

This kind of definition is called a **recurrence**: the formula for `n` is
written in terms of `n − 1`. To find a direct formula, compute a few values:

| n | T(n) | 2ⁿ |
|---|------|----|
| 0 | 0 | 1 |
| 1 | 1 | 2 |
| 2 | 3 | 4 |
| 3 | 7 | 8 |
| 4 | 15 | 16 |

The pattern is that `T(n)` is always one less than a power of two:

```
T(n) = 2ⁿ − 1
```

**Why is that true?** Assume it holds for `n − 1`, so `T(n − 1) = 2ⁿ⁻¹ − 1`.
Plug that in:

```
T(n) = 2 · (2ⁿ⁻¹ − 1) + 1
     = 2ⁿ − 2 + 1
     = 2ⁿ − 1
```

It's also true for `n = 0`, because `2⁰ − 1 = 0`. So it is true for every `n`.
This argument is called *proof by induction*, and it is recursion applied to
proofs.

Also, no solution can do better than `2ⁿ − 1` moves, because the largest disk
must move at some point and everything above it must be cleared away first and
rebuilt afterwards.

**What the formula means in practice:** the number of moves *doubles* with
every extra disk. The legend says monks are moving 64 golden disks. That's
`2⁶⁴ − 1 ≈ 1.8 × 10¹⁹` moves. At one move per second, that's about
585 billion years, roughly 40 times the age of the universe. So the time is
`O(2ⁿ)`: exponential.

### The non-recursive version: simulating the call stack

The rules forbid recursion, but not the *idea* of recursion. As section 0
explained, recursion is just a stack of "things still to do" kept by the
computer. We can keep that stack ourselves in an ordinary Python list.

Each entry on the stack is a task `(k, src, dst, aux, expanded)`:

- `expanded = False` means "this is a whole sub-puzzle: move `k` disks from
  `src` to `dst`, still unsolved."
- `expanded = True` means "this is a single, ready move: move disk `k` from
  `src` to `dst`."

```python
def hanoi_iter(n, src='A', dst='C', aux='B'):
    moves, stack = [], [(n, src, dst, aux, False)]
    while stack:
        k, s, d, a, expanded = stack.pop()
        if k <= 0:
            continue
        if expanded:
            moves.append((k, s, d))
        else:  # push in reverse order: left subproblem, this move, right subproblem
            stack += [(k - 1, a, d, s, False), (k, s, d, a, True), (k - 1, s, a, d, False)]
    return moves
```

The loop keeps taking the top task off the stack:

- If it's a **ready move**, write it down.
- If it's an **unsolved puzzle**, break it into the same three steps as the
  recursive version and push them onto the stack.

**Why push them in reverse order?** A stack is *last in, first out*, like a
pile of plates. The first step (`k − 1` disks from `src` to `aux`) has to come
out first, so it must go in last. That's why the list is written step 3, then
step 2, then step 1.

Because the work is split up in exactly the same way, `hanoi_iter` produces
exactly the same moves as `hanoi_rec`. The self-check confirms it.

**Another non-recursive method:** the class reference uses a different trick.
On odd-numbered moves, it moves disk 1 one peg around a circle. On
even-numbered moves, it makes the only legal move that doesn't involve disk 1.
That also works, but it's harder to see *why* it works. The explicit stack
version is obviously correct, because it is the recursion written out by hand.

### How the self-check works

`check(n, moves)` replays the moves on three real stacks (Python lists) and
verifies:

- each move takes the disk that is actually on **top** of the source peg;
- each disk lands on an empty peg or on a **larger** disk (rule 2);
- at the end, all `n` disks are on C in the right order;
- the number of moves is exactly `2ⁿ − 1`.

The main block runs this for every `n` from 0 to 10, and it also checks that
the recursive and non-recursive answers are identical.

---

## 2. Symbolic differentiation (`sym_diff.py`)

### What is a derivative? (a gentle refresher)

The **derivative** of a function tells you how fast it changes. If `f(x)` is
your position over time, the derivative `f'(x)` is your speed. On a graph,
it's the **slope** of the curve at a point: steep means a large derivative,
flat means 0, going down means negative.

The formal definition is:

```
f'(x) = lim   f(x + h) − f(x)
        h→0   ───────────────
                    h
```

In words: take a tiny step `h` forward, look at how much `f` changed, and
divide by the size of the step. That's "rise over run" from school,
measured over a step so small it shrinks to zero.

### Numeric vs. symbolic

There are two ways to get a derivative with a computer:

- **Numerically**: plug a small `h` (like `0.000001`) into the formula above
  and get a *number* such as `6.0000001`. It's always slightly off, and it
  only tells you about one point.
- **Symbolically**: produce the *formula* of the derivative, exactly as you
  would on paper. For example, the derivative of `x³` is `3x²`. That's what
  `sym_diff` does. It's exact and works for every `x`.

### How an expression is stored: a tree of tuples

To work with a formula, the program needs to see its *structure*, not just
text. I store each expression as nested tuples:

| Math | Python |
|------|--------|
| `5` | `5` |
| `x` | `'x'` |
| `a + b`, `a − b`, `a · b`, `a / b` | `('+', a, b)`, `('-', a, b)`, `('*', a, b)`, `('/', a, b)` |
| `aⁿ` (n is a number) | `('^', a, n)` |
| `sin a`, `cos a`, `eᵃ`, `ln a` | `('sin', a)`, `('cos', a)`, `('exp', a)`, `('ln', a)` |

For example, `x² · sin(x)` becomes `('*', ('^', 'x', 2), ('sin', 'x'))`. Drawn
as a tree:

```
          *
        /   \
       ^     sin
      / \     |
     x   2    x
```

A formula is a **recursive structure**: every operator's arguments are
themselves formulas. That's why recursion fits so naturally here. To
differentiate a big formula, differentiate its smaller pieces, then combine
the results with the right rule.

### The rules, one by one

Below, `a` and `b` are any sub-expressions, `a'` means "the derivative of `a`"
(computed by a recursive call), and `n` and `c` are plain numbers.

#### Constant rule: `c' = 0`
A constant never changes, so its rate of change is zero. The derivative of
`5` is `0`.

#### Variable rule: `x' = 1`
`x` grows at exactly the same rate as itself. If `x` moves 1 step, `x` moves
1 step. On a graph, the line `y = x` has slope 1.

#### Sum and difference rule: `(a ± b)' = a' ± b'`
If two things change at the same time, the total change is the sum of the two
changes. If you walk at 3 km/h on a train that moves at 100 km/h, you move at
103 km/h overall.

#### Product rule: `(a · b)' = a' · b + a · b'`
Picture a rectangle whose width is `a` and height is `b`, so its area is
`a · b`. If both sides grow a little, the area gains a strip along one side
(the change in `a` times `b`) and a strip along the other (`a` times the
change in `b`). The tiny corner piece is so small that it disappears as the
step shrinks to zero. Each factor takes a turn changing while the other one
stays fixed.

#### Quotient rule: `(a / b)' = (a' · b − a · b') / b²`
This is the product rule applied to `a · (1/b)`. The top is like the product
rule but with a **minus**: when the bottom `b` grows, the fraction gets
*smaller*. Dividing by `b²` scales the result back down. A memory aid many
students use: "low d-high minus high d-low, over low squared."

#### Power rule with the chain rule: `(aⁿ)' = n · aⁿ⁻¹ · a'`
- **Power rule** (when `a` is just `x`): `(xⁿ)' = n · xⁿ⁻¹`. The exponent comes
  down in front and goes down by one. For example, `(x³)' = 3x²`. You can see
  why for `x²`: a square of side `x` gains two strips of length `x` when the
  side grows, so the change is `2x`.
- **Chain rule** (the extra `· a'`): when the inside is not just `x`, you must
  multiply by how fast the *inside* is changing.

**The chain rule in plain words:** if `y` depends on `u`, and `u` depends on
`x`, then

```
dy/dx = dy/du · du/dx
```

Think of gears. If gear A turns 3 times for each turn of gear B, and B turns
2 times for each turn of C, then A turns 3 · 2 = 6 times for each turn of C.
The rates multiply.

Example: for `(2x + 5)⁴`, the outside is "something to the 4th", whose
derivative is `4 · (something)³`, and the inside `2x + 5` changes at rate `2`.
So the answer is `4 · (2x + 5)³ · 2`.

#### Sine: `(sin a)' = cos a · a'`
The slope of the sine wave at any point equals the value of the cosine wave
there. At `x = 0`, sine climbs most steeply (slope 1) and `cos 0 = 1`. At the
top of the wave, sine is flat (slope 0) and cosine is 0. The `· a'` is the
chain rule again.

#### Cosine: `(cos a)' = −sin a · a'`
Cosine is the sine wave shifted a quarter turn. Right after `x = 0`, cosine
starts *falling*, which is why there's a minus sign.

#### Exponential: `(eᵃ)' = eᵃ · a'`
`eˣ` is the special function whose rate of growth is equal to its own value,
like money with continuous interest: the more you have, the faster it grows.
That self-copying property is what defines the number `e ≈ 2.71828`.

#### Natural log: `(ln a)' = a' / a`
`ln` is the reverse of `eˣ`. Since `eˣ` grows faster and faster, its reverse
grows slower and slower: its slope at `x` is `1/x`. At `x = 1` the slope is 1;
at `x = 100` it's only 0.01.

### How `sym_diff` turns these rules into code

Each rule becomes one `if` branch that **returns a new tree**. The `a'` in a
rule becomes a recursive call `sym_diff(a)`:

```python
if op == '*':
    b = rest[0]
    return ('+', ('*', da, b), ('*', a, sym_diff(b)))   # a'·b + a·b'
```

Recursion stops at the leaves of the tree: numbers (derivative 0) and `'x'`
(derivative 1). Every other call works on a smaller piece of the tree, so the
function always finishes.

### Cleaning up: `simplify`

Following the rules mechanically produces correct but messy results. For
example, `(x³)'` comes out as `((3 · (x ^ 2)) · 1)`. `simplify` walks the tree
recursively, starting from the leaves, and applies school-algebra clean-ups:

| Pattern | Becomes | Why |
|---------|---------|-----|
| two plain numbers, e.g. `2 * 3` | `6` | just do the arithmetic |
| `0 + a`, `a + 0`, `a − 0` | `a` | adding zero changes nothing |
| `0 · a`, `a · 0` | `0` | anything times zero is zero |
| `1 · a`, `a · 1`, `a / 1` | `a` | multiplying or dividing by one changes nothing |
| `a⁰` | `1` | anything to the 0th power is 1 |
| `a¹` | `a` | to the 1st power is itself |

It deliberately **does not** combine `1/0`, `0` to a negative power, or a
negative number to a fractional power (like `(−8)^0.5`). Those have no real
answer, so it leaves them as written instead of crashing or producing a
complex number.

`simplify` is not a full algebra system. For example, `4 · (2 · x)` stays as
written rather than becoming `8x`. The answer is still correct, just not as
short as possible.

### How the self-check works: a second opinion from numbers

How can we be sure a printed derivative is right? Ask a completely different
method and compare. For each test expression, the program evaluates the
symbolic derivative at `x = 0.3`, `1.0` and `2.5`, and compares it with a
**numeric** estimate:

```
f'(x) ≈ f(x + h) − f(x − h)
        ───────────────────     with h = 0.000001
                2h
```

This is the **central difference**. It looks at a tiny step on *both* sides of
`x` and measures the slope between them. It's more accurate than stepping
forward only, because errors on the two sides largely cancel out. The error
shrinks like `h²`, instead of `h` for the one-sided version.

If the two answers differ by more than `0.0001`, the `assert` fails. A typo in
any rule (for example, forgetting the minus sign in the cosine rule) would be
caught immediately.

### Run it

```bash
python3 sym_diff.py
```

```
d/dx 5 = 0
d/dx (x ^ 3) = (3 * (x ^ 2))
d/dx (((4 * (x ^ 2)) + (3 * x)) + 7) = ((4 * (2 * x)) + 3)
d/dx cos((3 * x)) = ((-1 * sin((3 * x))) * 3)
d/dx ((x ^ 2) * sin(x)) = (((2 * x) * sin(x)) + ((x ^ 2) * cos(x)))
d/dx (((2 * x) + 5) ^ 4) = ((4 * (((2 * x) + 5) ^ 3)) * 2)
d/dx sin((x ^ 2)) = (cos((x ^ 2)) * (2 * x))
d/dx (sin(x) / x) = (((cos(x) * x) - sin(x)) / (x ^ 2))
d/dx exp((2 * x)) = (exp((2 * x)) * 2)
d/dx ln(((x ^ 2) + 1)) = ((2 * x) / ((x ^ 2) + 1))
d/dx (5 - x) = -1
all checks passed
```

Reading a few of these in normal math notation:

- `4x² + 3x + 7`  →  `4 · 2x + 3`, which is `8x + 3`.
- `x² · sin x`  →  `2x · sin x + x² · cos x` (product rule).
- `sin(x²)`  →  `cos(x²) · 2x` (chain rule: the outside is sine, the inside
  changes at rate `2x`).
- `sin x / x`  →  `(cos x · x − sin x) / x²` (quotient rule).

---

## 3. Functional programming: `map`, `filter`, `reduce`, and bubble sort with no loops (`fp_bubble.py`)

### What is functional programming?

In ordinary programming you write *instructions*: "make a counter, loop, add
to it, change this variable". In **functional programming** you describe
*what things are*, mostly by combining functions:

- **Functions are values.** You can pass a function into another function,
  just like a number. A function that takes or returns another function is
  called a **higher-order function**.
- **No loops, no modifying data.** Instead of changing a list in place, you
  build a new one. Repetition is done with recursion.

`map`, `filter` and `reduce` are the three classic higher-order functions.
Almost any loop over a list can be written with them.

### The list recursion pattern: head and tail

All three functions use the same idea. A list is either:

- **empty** (the base case), or
- a **head** (the first element, `xs[0]`) followed by a **tail** (the rest,
  `xs[1:]`, which is a shorter list).

So you handle the head yourself and give the tail to a recursive call. The
list gets one element shorter each time, so it eventually becomes empty and
the recursion stops. It's the queue analogy from section 0 again.

### `my_map(f, xs)`: transform every element

```
map(f, [x₁, x₂, …, xₙ]) = [f(x₁), f(x₂), …, f(xₙ)]
```

Apply `f` to each element and keep the results in order. It's like a factory
conveyor belt where every item passes through the same machine.

```python
def my_map(f, xs):
    return [] if not xs else [f(xs[0])] + my_map(f, xs[1:])
```

In words: the map of an empty list is empty; otherwise it's `f(head)`
followed by the map of the tail.
`my_map(lambda x: x * x, [1, 2, 3, 4, 5])` gives `[1, 4, 9, 16, 25]`.

`lambda x: x * x` is a **lambda**, a small function with no name, written
inline. It means "take `x`, give back `x · x`".

### `my_filter(pred, xs)`: keep only what passes a test

```
filter(p, xs) = the elements x of xs for which p(x) is True, in the same order
```

`pred` (short for *predicate*) is a function that answers yes or no. It's like
a sieve: small items fall through, and the rest stay.

```python
def my_filter(pred, xs):
    if not xs:
        return []
    return ([xs[0]] if pred(xs[0]) else []) + my_filter(pred, xs[1:])
```

In words: keep the head if it passes the test (otherwise drop it), then filter
the tail. `my_filter(lambda x: x % 2 == 0, [1, 2, 3, 4, 5])` gives `[2, 4]`.

### `my_reduce(f, xs, init)`: fold a list into one value

```
reduce(f, [x₁, x₂, …, xₙ], init) = f( … f( f(init, x₁), x₂ ) …, xₙ )
```

That formula looks scary, but it describes something you do every day.
Adding up a shopping receipt: start at 0, add the first price, add the next
price to that running total, and so on. The **running total** is called the
*accumulator*, and `f` is "how to combine the running total with the next
item".

Writing out `reduce(+, [1, 2, 3, 4, 5], 0)` step by step:

```
start              0
f(0, 1)       =    1
f(1, 2)       =    3
f(3, 3)       =    6
f(6, 4)       =   10
f(10, 5)      =   15   <- result
```

```python
def my_reduce(f, xs, init=_MISSING):
    if init is _MISSING:
        if not xs:
            raise TypeError('my_reduce() of empty sequence with no initial value')
        return my_reduce(f, xs[1:], xs[0])
    return init if not xs else my_reduce(f, xs[1:], f(init, xs[0]))
```

- When the list is empty, the accumulator **is** the answer.
- Otherwise, combine the accumulator with the head, then reduce the tail with
  that new accumulator.
- If you don't give a starting value, the first element is used as the start,
  just like Python's own `functools.reduce`. Reducing an empty list without a
  starting value raises an error, because there's nothing to return.

**A small but important detail:** the "no starting value" marker is a special
private object `_MISSING`, not `None`. The class reference uses `None`, which
means that if you *deliberately* pass `None` as the start value, it gets
ignored. With `_MISSING`, `None` is treated as a real value. The self-check
tests this case.

### Bubble sort, the normal way (for comparison)

Bubble sort repeatedly walks through the list and **swaps neighbours that are
in the wrong order**. Each full walk is called a *pass*. During a pass, the
largest value gets pushed all the way to the end, like a bubble rising to the
top of water, which is where the name comes from. After one pass, the last
element is in its final place. Repeat on the rest of the list.

The usual code uses two nested `for` loops. Our job is to do the same thing
with **no loops**.

### One pass using `reduce`

Here's the key observation: during a pass, you carry the **largest value seen
so far** to the right. At each new element, the smaller of the two is left
behind, and the larger one keeps moving. That's exactly a *reduce*. The
accumulator is a pair `(done, carry)`:

- `done`: the elements already left behind, in order.
- `carry`: the bubble, the largest value so far.

```python
def step(acc, x):
    done, carry = acc
    return (done + [x], carry) if carry > x else (done + [carry], x)
```

In words: if the bubble is bigger than the new element, leave the new element
behind and keep carrying the bubble. Otherwise, leave the bubble behind and
pick up the new element as the new bubble.

We start with `done = []` and `carry = xs[0]`, then reduce over the rest of
the list. At the end, the bubble is the largest element, so it goes last.

**Why `carry > x` and not `min`/`max`?** An earlier version used
`min(carry, x)` and `max(carry, x)`. Code review found that when two values
are equal or can't be compared (like `NaN`), `min` and `max` both return the
*same* object, so one element was **duplicated and the other lost**. The
explicit comparison always keeps both elements. It's also **stable**: equal
elements stay in their original order.

### Trace: one pass over `[5, 1, 4, 2]`

| Next element `x` | `carry > x`? | `done` after | `carry` after |
|---|---|---|---|
| (start) | | `[]` | `5` |
| `1` | 5 > 1 yes | `[1]` | `5` |
| `4` | 5 > 4 yes | `[1, 4]` | `5` |
| `2` | 5 > 2 yes | `[1, 4, 2]` | `5` |

Result of the pass: `[1, 4, 2] + [5]` = `[1, 4, 2, 5]`. The `5` bubbled to the
end.

### The full sort: recursion instead of the outer loop

```python
def bubble_sort(xs):
    if len(xs) <= 1:
        return list(xs)
    passed = bubble_pass(xs)
    return bubble_sort(passed[:-1]) + [passed[-1]]
```

After a pass, the last element is final. So we sort everything *except* the
last element (a smaller problem, done by recursion) and stick the last element
back on the end. A list of 0 or 1 elements is already sorted: that's the base
case.

Continuing the example:

```
bubble_sort([5, 1, 4, 2])
  pass -> [1, 4, 2, 5]        ->  bubble_sort([1, 4, 2]) + [5]
    pass -> [1, 2, 4]         ->  bubble_sort([1, 2]) + [4]
      pass -> [1, 2]          ->  bubble_sort([1]) + [2]
        base case             ->  [1]
= [1] + [2] + [4] + [5] = [1, 2, 4, 5]
```

Inside the sort there are no `for` or `while` loops and no list
comprehensions. The outer loop is replaced by the recursion in `bubble_sort`,
and the inner loop is replaced by `my_reduce`. (The test code at the bottom
of the file uses comprehensions to *generate random test lists*. That's test
setup only, not part of the sort.)

### Formula: how much work is it?

A pass over a list of length `k` makes `k − 1` comparisons. The lists get one
shorter each time (`n`, `n − 1`, …, `2`), so the total is:

```
(n − 1) + (n − 2) + … + 2 + 1  =  n(n − 1) / 2
```

**Why that sum?** Write the sum forwards and backwards and add the two
columns:

```
  (n−1) + (n−2) + … +   1
+   1   +   2   + … + (n−1)
= n     + n     + … +   n      <- (n − 1) columns, each adding up to n
```

That's `n · (n − 1)`, which is double the sum we want, so the sum is
`n(n − 1) / 2`. For 8 elements, that's `8 · 7 / 2 = 28` comparisons. The
growth is `O(n²)`: double the list, and it takes about four times as long.

**Known limits of this version** (also noted in a `ponytail:` comment in the
code):

- Every recursive call uses a stack frame, and Python allows about 1000. That
  limits the input to roughly 900 elements.
- `done + [x]` and `xs[1:]` copy lists on every step. That makes this version
  slower in practice than a normal bubble sort. It doesn't matter at homework
  sizes, but it would for a big list. The goal here was to show the idea, not
  to be fast.

### How the self-check works

It compares `bubble_sort(xs)` with Python's built-in `sorted(xs)` on tricky
fixed cases (empty list, one element, duplicates, negatives, a reversed list)
and on 50 random lists. It also checks that `my_reduce` accepts `None` as a
real starting value.

### Run it

```bash
python3 fp_bubble.py
```

```
map square : [1, 4, 9, 16, 25]
filter even: [2, 4]
reduce sum : 15
bubble_sort: [64, 34, 25, 12, 22, 11, 90, 5] -> [5, 11, 12, 22, 25, 34, 64, 90]
all checks passed
```

---

## 4. Where does lambda calculus fit in?

**Lambda calculus** is a tiny mathematical model of computation, invented by
Alonzo Church in the 1930s. It has only three things:

| Form | Meaning | Python equivalent |
|------|---------|-------------------|
| `x` | a variable | `x` |
| `λx. M` | a function that takes `x` and returns `M` | `lambda x: M` |
| `M N` | apply function `M` to argument `N` | `M(N)` |

There are no numbers, no loops and no variables that change, yet it can
compute anything a computer can. It is the theory behind functional
programming, and Python's `lambda` keyword is named after it.

All three exercises this week use its two big ideas:

- **Functions as values:** `my_map`, `my_filter` and `my_reduce` take a function
  like `lambda x: x * x` as an argument.
- **Repetition through recursion instead of loops:** pure lambda calculus has
  no `for` or `while`, so all repetition comes from functions applying
  themselves. That's exactly how the bubble sort works here.

---

## 5. Problems I found in the reference answers

I compared my solutions with the class reference answers
(`ccc115a/alg/_more/homework/week5`) and noticed these issues:

1. **`fp_each.py` isn't really bubble sort.** It compares `a[j]` with `a[i]`
   for every `j < i`, not neighbouring pairs, so it's a different exchange
   sort. It also only uses its own `each` function, not map/filter/reduce.
   `fp.py` is the one that actually fits the assignment.
2. **`fp.py`'s `my_reduce` uses `None` as "no starting value".** A deliberate
   `None` start value is silently ignored. My version uses a private marker
   object instead.
3. **`hanoi_rec.py` crashes for `n = 0`.** Its base case is `n == 1`, so `n = 0`
   calls itself with `−1`, `−2`, … until Python raises `RecursionError`.
4. **`sym_diff.py` has gaps.** Expressions such as `x ** x` silently get a wrong
   derivative, because the exponent is assumed to be a number. `5 - x` raises
   `TypeError`, because there is no `__rsub__`. Division isn't supported.
5. **None of the reference files check their output.** They only print it.
   Each of my files ends with `assert` checks, so a wrong answer stops the
   script with an error.

---

## 6. Files in this folder

| File | What it is |
|------|------------|
| `hanoi.py` | Tower of Hanoi: recursive `hanoi_rec` and non-recursive `hanoi_iter` (explicit stack), with a move checker. |
| `sym_diff.py` | Recursive symbolic differentiation `sym_diff(expr)`, plus `simplify`, `to_str` and a numeric self-check. |
| `fp_bubble.py` | Hand-made `my_map`, `my_filter` and `my_reduce`, and a bubble sort with no loops. |
| `README.md` | This file. |

To run everything:

```bash
python3 hanoi.py && python3 sym_diff.py && python3 fp_bubble.py
```

Each script prints `all checks passed` only if every `assert` succeeds.

## Agent Use
Claude Code
