"""Recursive symbolic differentiation with respect to x.

Expressions are nested tuples:
  number | 'x' | ('+', a, b) | ('-', a, b) | ('*', a, b) | ('/', a, b)
  | ('^', a, n) with n a number | ('sin', a) | ('cos', a) | ('exp', a) | ('ln', a)
"""
import math
import operator

OPS = {'+': operator.add, '-': operator.sub, '*': operator.mul, '/': operator.truediv, '^': operator.pow}
FUNCS = {'sin': math.sin, 'cos': math.cos, 'exp': math.exp, 'ln': math.log}


def sym_diff(e):
    if isinstance(e, (int, float)):
        return 0
    if e == 'x':
        return 1
    op, a, *rest = e
    da = sym_diff(a)
    if op in '+-':
        return (op, da, sym_diff(rest[0]))
    if op == '*':
        b = rest[0]
        return ('+', ('*', da, b), ('*', a, sym_diff(b)))
    if op == '/':
        b = rest[0]
        return ('/', ('-', ('*', da, b), ('*', a, sym_diff(b))), ('^', b, 2))
    if op == '^':
        n = rest[0]
        return ('*', ('*', n, ('^', a, n - 1)), da)
    if op == 'sin':
        return ('*', ('cos', a), da)
    if op == 'cos':
        return ('*', ('*', -1, ('sin', a)), da)
    if op == 'exp':
        return ('*', e, da)
    if op == 'ln':
        return ('/', da, a)
    raise ValueError(f'unknown operator {op!r}')


def simplify(e):
    if not isinstance(e, tuple):
        return e
    op, *args = e
    args = [simplify(a) for a in args]
    num = lambda v: isinstance(v, (int, float))
    if op in FUNCS:
        return (op, args[0])
    a, b = args
    bad_pow = op == '^' and ((a == 0 and b < 0) or (a < 0 and b != int(b))) if num(a) and num(b) else False
    if num(a) and num(b) and not (op == '/' and b == 0) and not bad_pow:
        return OPS[op](a, b)
    if op == '+' and a == 0: return b
    if op in '+-' and b == 0: return a
    if op == '*' and (a == 0 or b == 0): return 0
    if op == '*' and a == 1: return b
    if op in '*/' and b == 1: return a
    if op == '^' and b == 0: return 1
    if op == '^' and b == 1: return a
    return (op, a, b)


def to_str(e):
    if not isinstance(e, tuple):
        return str(e)
    op, *args = e
    if len(args) == 1:
        return f'{op}({to_str(args[0])})'
    return f'({to_str(args[0])} {op} {to_str(args[1])})'


def evaluate(e, x):
    if isinstance(e, (int, float)):
        return e
    if e == 'x':
        return x
    op, *args = e
    v = [evaluate(a, x) for a in args]
    return FUNCS[op](*v) if op in FUNCS else OPS[op](*v)


if __name__ == '__main__':
    exprs = [
        5,
        ('^', 'x', 3),
        ('+', ('+', ('*', 4, ('^', 'x', 2)), ('*', 3, 'x')), 7),
        ('cos', ('*', 3, 'x')),
        ('*', ('^', 'x', 2), ('sin', 'x')),
        ('^', ('+', ('*', 2, 'x'), 5), 4),
        ('sin', ('^', 'x', 2)),
        ('/', ('sin', 'x'), 'x'),
        ('exp', ('*', 2, 'x')),
        ('ln', ('+', ('^', 'x', 2), 1)),
        ('-', 5, 'x'),
    ]
    h = 1e-6
    for e in exprs:
        d = simplify(sym_diff(e))
        print(f'd/dx {to_str(e)} = {to_str(d)}')
        for x in (0.3, 1.0, 2.5):
            numeric = (evaluate(e, x + h) - evaluate(e, x - h)) / (2 * h)
            assert abs(evaluate(d, x) - numeric) < 1e-4, (to_str(e), x)
    print('all checks passed')
