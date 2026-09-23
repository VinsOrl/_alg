#!/usr/bin/env python3
"""Brute-force SAT solver via systematic truth-table enumeration.

The Boolean Satisfiability problem (SAT) asks whether a Boolean formula can be
made true by some assignment of true/false to its variables.
See: https://en.wikipedia.org/wiki/Boolean_satisfiability_problem

This program decides SAT the most direct (exponential) way: it enumerates ALL
2**n possible truth assignments of the n variables, evaluates the formula under
each, and reports the formula SATISFIABLE if any assignment makes it true.

Formulas are given in Conjunctive Normal Form (CNF): an AND of clauses, where
each clause is an OR of literals. A literal is a variable or its negation.

Encoding (matches the DIMACS convention):
    - Variables are numbered 1, 2, 3, ...
    - The integer  n  means "variable n is true".
    - The integer -n  means "variable n is false" (negated).
    - A clause is a list of literals, e.g. [1, -3, 2]  =>  (x1 OR NOT x3 OR x2).
    - A formula is a list of clauses.

Usage:
    python3 sat_solver.py            # run the built-in demo formulas
    python3 sat_solver.py file.cnf   # solve a DIMACS CNF file
"""

import sys
from itertools import product

# Above this many variables the full truth table has too many rows to print
# (2**16 = 65536). We still solve, but skip dumping every row to the screen.
MAX_VARS_TO_PRINT = 16


def parse_dimacs(text):
    """Parse DIMACS CNF text into (num_vars, clauses).

    Lines starting with 'c' are comments. The 'p cnf <vars> <clauses>' header
    declares the problem size. Every other token stream is a list of literals
    terminated by 0; a single clause may even span multiple lines.
    """
    tokens = []
    declared_vars = 0
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("c"):
            continue
        if line.startswith("p"):
            # e.g. "p cnf 3 2"
            parts = line.split()
            if len(parts) >= 3:
                declared_vars = int(parts[2])
            continue
        tokens.extend(line.split())

    clauses = []
    current = []
    for tok in tokens:
        value = int(tok)
        if value == 0:
            clauses.append(current)
            current = []
        else:
            current.append(value)
    if current:  # tolerate a final clause with no trailing 0
        clauses.append(current)

    # Number of variables = max of the declared header and the literals seen.
    max_literal = max((abs(lit) for clause in clauses for lit in clause),
                      default=0)
    num_vars = max(declared_vars, max_literal)
    return num_vars, clauses


def evaluate(clauses, assignment):
    """Return True if every clause is satisfied by `assignment`.

    `assignment` maps variable number -> bool. A clause is satisfied when at
    least one of its literals is true. An empty clause is always false, so a
    formula containing an empty clause is unsatisfiable.
    """
    for clause in clauses:
        clause_true = False
        for lit in clause:
            var = abs(lit)
            value = assignment[var]
            if lit < 0:
                value = not value
            if value:
                clause_true = True
                break
        if not clause_true:
            return False
    return True


def enumerate_truth_table(num_vars, clauses):
    """Yield (assignment, formula_value) for all 2**num_vars assignments.

    `assignment` is a dict {var: bool} for var in 1..num_vars.
    """
    variables = range(1, num_vars + 1)
    for combo in product([False, True], repeat=num_vars):
        assignment = dict(zip(variables, combo))
        yield assignment, evaluate(clauses, assignment)


def _fmt(value):
    return "T" if value else "F"


def solve(num_vars, clauses, show_table=True):
    """Print the truth table (size permitting) and the SAT verdict.

    Returns (is_sat, model) where model is the first satisfying assignment
    (a dict) or None.
    """
    print(f"Variables: {num_vars}   Clauses: {len(clauses)}")
    print("Formula (CNF):", format_formula(clauses) or "(empty -> trivially true)")
    print()

    printable = show_table and num_vars <= MAX_VARS_TO_PRINT
    if printable:
        header = " ".join(f"x{v}" for v in range(1, num_vars + 1))
        print(f"{header} | F")
        print("-" * (len(header) + 4))
    elif show_table:
        print(f"[Truth table has 2^{num_vars} rows -- too large to print; "
              f"solving without printing every row.]")
        print()

    total_rows = 0
    sat_count = 0
    first_model = None
    for assignment, value in enumerate_truth_table(num_vars, clauses):
        total_rows += 1
        if value:
            sat_count += 1
            if first_model is None:
                first_model = dict(assignment)
        if printable:
            row = " ".join(
                f"{_fmt(assignment[v]):>{len(f'x{v}')}}"
                for v in range(1, num_vars + 1)
            )
            print(f"{row} | {1 if value else 0}")

    print()
    print(f"Enumerated {total_rows} assignment(s); "
          f"{sat_count} satisfy the formula.")
    if first_model is not None:
        witness = " ".join(
            f"x{v}={_fmt(first_model[v])}" for v in range(1, num_vars + 1)
        )
        print("Result: SATISFIABLE")
        if witness:
            print(f"  A satisfying assignment: {witness}")
        return True, first_model
    else:
        print("Result: UNSATISFIABLE")
        return False, None


def format_formula(clauses):
    """Human-readable CNF like: (x1 v ~x3) ^ (x2 v x3 v ~x1)."""
    def lit(l):
        return f"~x{abs(l)}" if l < 0 else f"x{l}"

    parts = []
    for clause in clauses:
        if not clause:
            parts.append("(FALSE)")  # empty clause
        else:
            parts.append("(" + " v ".join(lit(l) for l in clause) + ")")
    return " ^ ".join(parts)


# --- Built-in demonstration formulas (used when no file argument is given) ---
DEMOS = [
    ("Demo 1 -- satisfiable: (x1 v ~x3) ^ (x2 v x3 v ~x1)",
     3, [[1, -3], [2, 3, -1]]),
    ("Demo 2 -- unsatisfiable: (x1) ^ (~x1)",
     1, [[1], [-1]]),
]


def run_demos():
    for i, (title, num_vars, clauses) in enumerate(DEMOS):
        if i:
            print("\n" + "=" * 60 + "\n")
        print(title)
        print()
        solve(num_vars, clauses)


def run_file(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            text = fh.read()
    except OSError as exc:
        print(f"Error: cannot read '{path}': {exc}", file=sys.stderr)
        return 1
    try:
        num_vars, clauses = parse_dimacs(text)
    except ValueError as exc:
        print(f"Error: malformed DIMACS in '{path}': {exc}", file=sys.stderr)
        return 1
    print(f"Loaded DIMACS file: {path}\n")
    solve(num_vars, clauses)
    return 0


def main(argv):
    if len(argv) <= 1:
        run_demos()
        return 0
    if argv[1] in ("-h", "--help"):
        print(__doc__)
        return 0
    return run_file(argv[1])


if __name__ == "__main__":
    sys.exit(main(sys.argv))
