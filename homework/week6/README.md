# Week 6 — A Lambda Calculus Interpreter

Week 5's notes introduced the notation (`λx. M`, variables, application) as
background for hand-rolled `map`/`filter`/`reduce`. This week writes a program
that actually *reads* that notation as source text and *runs* it, printing
every beta-reduction step so the whole calculation process is visible.

`lambda_calculus.py` is a single self-contained file: term representation,
substitution, reducer, parser, a handful of named terms, example programs,
and a self-check.

## Not the same as "encoding lambda calculus in Python"

The course's own reference material (`lambdaCalculus.py` in the
`04c-LambdaCalculus` folder) writes Church booleans, numerals, and the
Y-combinator directly as nested Python `lambda` closures, e.g.
`TRUE = lambda x: lambda y: x`. That's a neat trick — it reuses Python's own
substitution machinery — but it never parses lambda-calculus *text* and never
shows a reduction trace; the closures just run.

This exercise is the other direction: it parses a string like `AND TRUE
FALSE` as a lambda-calculus term and reduces it one beta-step at a time,
printing the term after every step.

---

## 1. The formal rules

Lambda calculus has exactly three kinds of thing you can write, and exactly
one rule for "running" them. Everything else in this file is built on top of
these few formulas.

### Syntax (grammar)

```
Term ::= x              a variable
       | λx. Term        an abstraction ("a function of x")
       | Term Term       an application ("call the first on the second")
```

In plain words: a lambda-calculus program is either a name, a function
definition, or one thing being called with another thing as its argument.
There is nothing else — no numbers, no booleans, no loops. (Later sections
show how numbers and booleans get *built* out of nothing but this.)

### Free variables

```
FV(x)      = { x }
FV(λx. M)  = FV(M)  \  { x }
FV(M N)    = FV(M)  ∪  FV(N)
```

A variable is "free" in a term if it's used but not bound by an enclosing
`λ`. In `λx. x y`, `x` is bound (it's the parameter) but `y` is free — it
refers to something from outside. `free_vars()` in the code is a direct,
line-for-line translation of this formula.

### Substitution — the formula that matters most

Writing `M[x := N]` means "take term `M` and replace every free occurrence of
`x` with `N`." The textbook definition has four cases:

```
x [x := N]        = N
y [x := N]        = y                                  if y ≠ x

(M₁ M₂) [x := N]  = (M₁[x := N]) (M₂[x := N])

(λx. M) [x := N]  = λx. M                               (x is shadowed — nothing to do)
(λy. M) [x := N]  = λy. (M[x := N])                      if y ≠ x  and  y ∉ FV(N)
(λy. M) [x := N]  = λy'. (M[y := y'][x := N])            if y ≠ x  and  y ∈ FV(N)
                    where y' is a fresh name
```

The first three lines are exactly what you'd guess: substitute inside a
variable, substitute inside both halves of an application, and do nothing if
the variable you're replacing is already shadowed by a closer binder. The
last two lines are the one case that's easy to get wrong — see the next
section for why.

### Alpha-conversion — renaming a bound variable changes nothing

```
λx. M   ≡α   λy. (M[x := y])          provided y ∉ FV(M)
```

In words: the *name* of a bound variable is just a label; `λx. x` and
`λz. z` are the same function ("return whatever you're given"). You're always
allowed to rename a bound variable to a fresh name, as long as that fresh
name doesn't already mean something else inside the body. This is the escape
hatch substitution uses when a name clash would otherwise cause trouble.

### Beta-reduction — the one computational step

```
(λx. M) N   →β   M[x := N]
```

This is the entire "engine" of lambda calculus: applying a function `λx. M`
to an argument `N` means substituting `N` for `x` throughout `M`. Every
"calculation" you'll see printed by this program is one or more applications
of this single rule. `step()` in the code looks for a sub-term shaped exactly
like the left-hand side (`(λx. M) N`) and rewrites it to the right-hand side.

(Eta-conversion — `λx. M x ≡η M` when `x ∉ FV(M)`, saying a function that
just forwards its argument is the same as not wrapping it at all — exists
too, but this interpreter doesn't implement it; see Known Limitations.)

---

## 2. Term representation

The grammar above becomes three `collections.namedtuple`s:

```python
Var = namedtuple('Var', 'name')       # x
Abs = namedtuple('Abs', 'param body') # λx. body
App = namedtuple('App', 'func arg')   # func arg
```

Immutable, stdlib, free `__eq__`/`__repr__` — no need for a custom class.
Every function in the file (`free_vars`, `subst`, `step`, `pretty`) is a
case-by-case match on these three shapes, directly mirroring the formulas
above.

## 3. The hard part: variable capture, worked by hand

Take the substitution `(λy. x) [x := y]` — i.e. plug `y` in for `x` inside
`λy. x`. Read literally, "replace `x` with `y`" gives `λy. y`. But `λy. y` is
the *identity function* — "return whatever you're handed" — while the
original `λy. x` meant "ignore whatever you're handed, return the outside
value called `x`." Those are completely different functions. Something went
wrong.

What went wrong: the `y` we substituted *in* got silently swallowed by the
`λy` that was already sitting there — it got **captured**, exactly the case
the last line of the substitution formula calls out:

```
(λy. M) [x := N]  = λy'. (M[y := y'][x := N])   if y ∈ FV(N)
```

Here `N = y`, so `y ∈ FV(N)` is true — the trap condition fires. The fix is
to first alpha-rename the binder to a name nobody's using (`y'`), *then*
substitute:

```
(λy. x) [x := y]  ==  λy'. y        —   NOT   λy. y
```

`fresh_name()` picks `y'` by appending `'` until the name is free. This is
the one part of the interpreter that must be exactly right: get it wrong and
most examples still "work" by coincidence (their variable names never
collide), but the interpreter would silently give a wrong answer the moment
a program reuses a name — which is exactly the kind of bug that's invisible
until it isn't. There's a dedicated `assert` for this one case in `__main__`.

## 4. Reduction strategy: which redex to reduce first?

A term can contain more than one place where the beta-rule applies (more
than one "redex"). Lambda calculus is famously **confluent** (the
Church–Rosser theorem): if a term has a normal form at all, you'll reach the
*same* normal form no matter which redex you reduce first. But if you don't
reduce in a good order, you can still end up doing unnecessary work, or — for
certain terms — never finish even though a normal form exists.

This interpreter always reduces the **leftmost-outermost** redex first
("normal order"): scan the term left to right, and the moment you find a
`(λx. M) N` shape, reduce that one before looking any deeper. Humanized: "say
the function's name before looking inside its argument." The payoff is a
guarantee — normal order is proven to find a normal form whenever one
exists, which is *not* true of the opposite choice (applicative order,
a.k.a. call-by-value: always reduce an argument before substituting it),
because applicative order can get stuck fully evaluating an argument that
the function was going to throw away anyway.

`reduce_steps()` repeatedly calls `step()` and records every intermediate
term, stopping after `max_steps` (default 200) if nothing has reached a
normal form yet. That cap exists because some terms — most famously
`OMEGA = (λx. x x) (λx. x x)` — never reach a normal form at all: reducing
`OMEGA` produces `OMEGA` again, forever. Without a cap the program would just
hang.

## 5. Syntax supported

- `\x.x` or `λx.x` for abstraction
- juxtaposition for application: `f x y` means `(f x) y`
- parens for grouping
- multi-argument sugar: `\x y.x` desugars to `\x.\y.x`
- named terms (macros): `TRUE`, `AND`, `SUCC`, `PLUS`, etc. are substituted
  by name at parse time — not a real `let` with scoping, just a lookup table,
  which is all these examples need

## 6. Church encodings used by the examples

Lambda calculus has no built-in booleans or numbers — the grammar in
section 1 is *all* there is. Church encoding is the trick of building
booleans and numbers purely out of functions, so plain beta-reduction can
compute with them.

**Booleans as selectors.** A boolean's whole job is to pick one of two
things:

```
TRUE  = λx. λy. x        "given two choices, return the first"
FALSE = λx. λy. y        "given two choices, return the second"
```

So a boolean *is* a two-argument chooser function — there's no separate
`if`, the boolean does the choosing by how it's applied: `TRUE a b` reduces
to `a`, `FALSE a b` reduces to `b`.

`AND = λp. λq. p q p` reads as: "ask `p` to choose between `q` and `p`
itself." If `p` is `TRUE`, it chooses the first option, `q` — so the result
*is* `q`, which is correct: "true AND q" should just be whatever `q` is. If
`p` is `FALSE`, it chooses the second option, `p` itself — which is `FALSE`
— correct again: "false AND anything" is false, without even needing to look
at `q`.

**Numbers as "do it n times."** A Church numeral for `n` doesn't store the
number `n` anywhere — it *is* the instruction "apply the next argument, `n`
times, to the one after that":

```
ZERO  = λf. λx. x                 apply f  zero  times
ONE   = λf. λx. f x               apply f  once
TWO   = λf. λx. f (f x)           apply f  twice
THREE = λf. λx. f (f (f x))       apply f  three times
```

`SUCC = λn. λf. λx. f (n f x)` means "whatever `n` already does — applying
`f` some number of times to `x` — do that, then apply `f` one more time on
top." That's the definition of "successor": one more than `n`.

`PLUS = λm. λn. λf. λx. m f (n f x)` means "first let `n` apply `f` to `x`
its own number of times, *then* let `m` apply `f` that many more times on
top of the result." Doing `n` applications and then `m` more applications is
exactly addition.

## 7. Walking through the example traces

Running the file prints every beta-reduction step for six programs. Here's
what's actually happening at each step, narrated — cross-reference against
the formulas above.

**`(\x.x) y` → `y`.** One redex: `(λx. x) y` matches the beta-rule's
left-hand side exactly, with `M = x` and `N = y`. Substituting gives
`x[x := y] = y`. Done in one step — the simplest possible calculation.

**`AND TRUE FALSE` → `FALSE`.** Unfolding the macros gives
`(λp.λq. p q p) (λx.λy.x) (λx.λy.y)`. Step 1 substitutes `p := TRUE`,
exposing `λq. TRUE q TRUE`. Step 2 substitutes `q := FALSE`, giving
`TRUE FALSE TRUE` — a chooser being handed its two choices. Steps 3–4 apply
`TRUE`'s own definition (`λx.λy.x`, "pick the first") to those two choices,
landing on `FALSE`. This is `AND`'s selector logic from section 6, playing
out one substitution at a time.

**`AND TRUE TRUE` → `TRUE`.** Identical shape to the line above, except the
second choice `TRUE` is picked this time (because the first argument still
determines everything) — the trace is the same four steps with `TRUE` in
both slots, ending on `TRUE`.

**`SUCC ONE` → `TWO`.** `SUCC`'s body `f (n f x)` gets `n := ONE`, giving
`f ((λf.λx. f x) f x)`. The inner application `(λf.λx. f x) f x` is itself a
tiny beta-redex hiding inside — reducing it (two more steps, substituting
`f` then `x`) collapses it down to `f x`, so the whole thing becomes
`f (f x)` — which is, by definition, `TWO`. "One more than one is two,"
proved by substitution rather than arithmetic.

**`PLUS TWO THREE` → `FIVE`** (printed as `λf.λx. f (f (f (f (f x))))`).
Same idea at a larger scale: `PLUS`'s body says "run `THREE`'s three
applications of `f` to `x` first, then run `TWO`'s two applications on top of
that." The trace shows exactly that unfolding — `THREE` expanding to three
nested `f`s, then `TWO` wrapping two more `f`s around the outside — six
printed steps that end on five nested `f`s total.

**`OMEGA` — never reduces.** `OMEGA = (λx. x x) (λx. x x)`. Beta-reducing it
substitutes the whole term for `x` inside `x x`, giving back `(λx. x x)
(λx. x x)` — the exact same term. Every "step" produces an identical result,
forever; there is no normal form to reach. The trace demonstrates the
`max_steps` guard from section 4 firing and reporting "did not terminate"
instead of looping forever — the printed trace is deliberately trimmed after
the first few and last few steps (the underlying data still has all 200+200
if you remove the cap; only the *printout* is shortened, so the self-checks
still see every step).

## 8. How to run

```
python3 lambda_calculus.py
```

Prints the full reduction trace for each example, then runs `assert`-based
self-checks — including the variable-capture case from section 3 — and
finishes with `all checks passed`.

## 9. Known limitations (ponytail notes)

- Fixed step cap, no cycle detection — a program that genuinely needs more
  than 200 steps just needs a larger `max_steps` argument.
- No eta-conversion — only beta reduction (see section 1).
- No real `let`/scoping — named terms are a flat substitution table, not a
  lexically-scoped binding form.
- Parse errors are plain `SyntaxError`s with the offending token, not a
  pointer into the source line — fine for short one-line programs like these.
