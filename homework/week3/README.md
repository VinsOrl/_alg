# Week 3 — Brute-Force SAT Solver (Truth-Table Enumeration)

A Python program that decides the **Boolean Satisfiability problem (SAT)** by
systematically enumerating truth tables.

## What is SAT?

SAT asks: *given a Boolean formula, is there an assignment of `true`/`false` to
its variables that makes the whole formula evaluate to `true`?*

- If such an assignment exists, the formula is **SATISFIABLE** (and that
  assignment is a *model* / *witness*).
- If no assignment works, the formula is **UNSATISFIABLE**.

SAT is the classic NP-complete problem.
Reference: <https://en.wikipedia.org/wiki/Boolean_satisfiability_problem>

## The approach: enumerate the truth table

For a formula with `n` variables there are exactly `2^n` possible assignments.
This solver simply:

1. Generates **every** one of the `2^n` assignments (the full truth table).
2. **Evaluates** the formula under each assignment.
3. Reports **SATISFIABLE** as soon as any assignment makes it true (also counting
   how many do), or **UNSATISFIABLE** if none do.

This is the exhaustive brute-force baseline — no clever pruning (no DPLL, no unit
propagation). It is simple and always correct, but exponential.

## CNF and literal encoding

The formula is given in **Conjunctive Normal Form (CNF)**: an AND of *clauses*,
where each clause is an OR of *literals*, and a literal is a variable or its
negation.

Variables are numbered `1, 2, 3, ...` and encoded as integers (DIMACS
convention):

| Integer | Meaning            |
|---------|--------------------|
| `n`     | variable `xn` is true   |
| `-n`    | variable `xn` is false (negated) |

- A **clause** is a list of literals: `[1, -3, 2]` means `(x1 ∨ ¬x3 ∨ x2)`.
- A **formula** is a list of clauses, all ANDed together.

Special cases: an empty formula (no clauses) is trivially **true**; a formula
that contains an *empty clause* is **false**.

## DIMACS input format

The solver reads the standard DIMACS CNF text format (see `example.cnf`):

```
c This is a comment line
c 'p cnf <num_vars> <num_clauses>' declares the problem size
p cnf 3 3
1 -3 0        <- clause (x1 ∨ ¬x3)
2 3 -1 0      <- clause (x2 ∨ x3 ∨ ¬x1)
-2 3 0        <- clause (¬x2 ∨ x3)
```

- Lines beginning with `c` are comments.
- The `p cnf` header gives the variable and clause counts.
- Each remaining line lists a clause's literals, terminated by `0`.

## How to run

Run the built-in demo formulas (one satisfiable, one unsatisfiable):

```bash
python3 sat_solver.py
```

Solve a DIMACS `.cnf` file:

```bash
python3 sat_solver.py example.cnf
```

### Sample output

```
Variables: 3   Clauses: 3
Formula (CNF): (x1 v ~x3) ^ (x2 v x3 v ~x1) ^ (~x2 v x3)

x1 x2 x3 | F
-----------
 F  F  F | 1
 F  F  T | 1
 F  T  F | 0
 ...
Enumerated 8 assignment(s); 5 satisfy the formula.
Result: SATISFIABLE
  A satisfying assignment: x1=F x2=F x3=F
```

The last column `F` is the value of the whole formula (`1` = true, `0` = false)
for that row.

## Complexity

- **Time:** `O(2^n · m)` — `2^n` assignments, each checked against `m` clauses.
- **Space:** `O(n)` per assignment (assignments are generated one at a time).

Because printing `2^n` rows becomes impractical for large `n`, the solver prints
the full table only when `n ≤ 16` (`MAX_VARS_TO_PRINT` in `sat_solver.py`); above
that it still computes the verdict but skips dumping every row.

## Files

| File            | Purpose                                    |
|-----------------|--------------------------------------------|
| `sat_solver.py` | The solver (Python standard library only). |
| `example.cnf`   | A small satisfiable DIMACS sample.         |
| `README.md`     | This document.                             |


## Agent Use
Claude Code (LLM model: qwen3.8)
