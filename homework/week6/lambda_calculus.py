"""Lambda calculus interpreter: parses \\x.x-style source and shows every beta-reduction step."""
import re
from collections import namedtuple

Var = namedtuple('Var', 'name')
Abs = namedtuple('Abs', 'param body')
App = namedtuple('App', 'func arg')


def free_vars(term):
    if isinstance(term, Var):
        return {term.name}
    if isinstance(term, App):
        return free_vars(term.func) | free_vars(term.arg)
    return free_vars(term.body) - {term.param}


def fresh_name(base, avoid):
    name = base
    while name in avoid:
        name = name + "'"
    return name


def subst(term, var, value):
    """Capture-avoiding substitution: term[var := value]."""
    if isinstance(term, Var):
        return value if term.name == var else term
    if isinstance(term, App):
        return App(subst(term.func, var, value), subst(term.arg, var, value))
    if term.param == var:
        return term
    if term.param not in free_vars(value):
        return Abs(term.param, subst(term.body, var, value))
    z = fresh_name(term.param, free_vars(value) | free_vars(term.body) | {var})
    renamed_body = subst(term.body, term.param, Var(z))
    return Abs(z, subst(renamed_body, var, value))


def step(term):
    """One normal-order (leftmost-outermost) beta reduction. Returns (term, changed)."""
    if isinstance(term, App):
        if isinstance(term.func, Abs):
            return subst(term.func.body, term.func.param, term.arg), True
        new_func, changed = step(term.func)
        if changed:
            return App(new_func, term.arg), True
        new_arg, changed = step(term.arg)
        return App(term.func, new_arg), changed
    if isinstance(term, Abs):
        new_body, changed = step(term.body)
        return Abs(term.param, new_body), changed
    return term, False


def reduce_steps(term, max_steps=200):
    trace = [term]
    for _ in range(max_steps):
        term, changed = step(term)
        if not changed:
            return trace, True
        trace.append(term)
    # ponytail: flat step-count cap, no cycle/size detection -- raise max_steps
    # or add a visited-term set if a program needs deeper/looping reduction
    return trace, False


def pretty(term):
    if isinstance(term, Var):
        return term.name
    if isinstance(term, Abs):
        return '\\' + term.param + '.' + pretty(term.body)
    func_str = pretty(term.func)
    if isinstance(term.func, Abs):
        func_str = '(' + func_str + ')'
    arg_str = pretty(term.arg)
    if isinstance(term.arg, (Abs, App)):
        arg_str = '(' + arg_str + ')'
    return func_str + ' ' + arg_str


TOKEN_RE = re.compile(r"\\|λ|\.|\(|\)|[A-Za-z_][A-Za-z0-9_']*|\S")


def tokenize(source):
    return [t for t in TOKEN_RE.findall(source) if not t.isspace()]


class Parser:
    def __init__(self, tokens, macros):
        self.tokens = tokens
        self.i = 0
        self.macros = macros

    def peek(self):
        return self.tokens[self.i] if self.i < len(self.tokens) else None

    def advance(self):
        tok = self.peek()
        self.i += 1
        return tok

    def expect(self, tok):
        got = self.advance()
        if got != tok:
            raise SyntaxError(f'expected {tok!r}, got {got!r}')

    def parse_expr(self):
        if self.peek() in ('\\', 'λ'):
            return self.parse_abs()
        return self.parse_app()

    def parse_abs(self):
        self.advance()  # '\' or 'λ'
        params = []
        while self.peek() != '.':
            tok = self.advance()
            if tok is None or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_']*", tok):
                raise SyntaxError(f'expected parameter name, got {tok!r}')
            params.append(tok)
        self.expect('.')
        body = self.parse_expr()
        for param in reversed(params):
            body = Abs(param, body)
        return body

    def parse_app(self):
        term = self.parse_atom()
        while self.peek() is not None and self.peek() not in (')', '.'):
            term = App(term, self.parse_atom())
        return term

    def parse_atom(self):
        tok = self.advance()
        if tok == '(':
            term = self.parse_expr()
            self.expect(')')
            return term
        if tok is not None and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_']*", tok):
            return self.macros.get(tok, Var(tok))
        raise SyntaxError(f'unexpected token {tok!r}')


def parse(source, macros=None):
    p = Parser(tokenize(source), macros or {})
    term = p.parse_expr()
    p.expect(None)
    return term


MACROS = {}


def define(name, source):
    MACROS[name] = parse(source, MACROS)


define('IDENTITY', r'\x.x')
define('TRUE', r'\x.\y.x')
define('FALSE', r'\x.\y.y')
define('AND', r'\p.\q.p q p')
define('ZERO', r'\f.\x.x')
define('ONE', r'\f.\x.f x')
define('TWO', r'\f.\x.f (f x)')
define('THREE', r'\f.\x.f (f (f x))')
define('SUCC', r'\n.\f.\x.f (n f x)')
define('PLUS', r'\m.\n.\f.\x.m f (n f x)')
define('OMEGA', r'(\x.x x) (\x.x x)')

EXAMPLES = [
    ('Identity applied to a free variable', '(\\x.x) y'),
    ('AND TRUE FALSE -> FALSE', 'AND TRUE FALSE'),
    ('AND TRUE TRUE -> TRUE', 'AND TRUE TRUE'),
    ('SUCC ONE -> TWO', 'SUCC ONE'),
    ('PLUS TWO THREE -> FIVE', 'PLUS TWO THREE'),
    ('OMEGA: divergence, proves the step guard', 'OMEGA'),
]


def run_example(title, source, max_steps=200):
    term = parse(source, MACROS)
    trace, terminated = reduce_steps(term, max_steps)
    print('---', title, '---')
    print('source:', source)
    for i, t in enumerate(trace[:10] if len(trace) > 20 else trace):
        print(' ', i, '=>', pretty(t))
    if len(trace) > 20:
        print('  ...', len(trace) - 15, 'more steps, all unchanged ...')
        for i, t in enumerate(trace[-5:], start=len(trace) - 5):
            print(' ', i, '=>', pretty(t))
    if terminated:
        print('normal form:', pretty(trace[-1]))
    else:
        print('did not terminate within', max_steps, 'steps')
    print()
    return trace, terminated


if __name__ == '__main__':
    for title, source in EXAMPLES:
        run_example(title, source)

    assert pretty(subst(parse(r'\y.x'), 'x', Var('y'))) == "\\y'.y"
    assert pretty(parse(r'\x y.x')) == pretty(parse(r'\x.\y.x'))
    assert pretty(parse(r'(\x.x) y')) == '(\\x.x) y'

    expected = {
        'Identity applied to a free variable': 'y',
        'AND TRUE FALSE -> FALSE': '\\x.\\y.y',
        'AND TRUE TRUE -> TRUE': '\\x.\\y.x',
        'SUCC ONE -> TWO': '\\f.\\x.f (f x)',
        'PLUS TWO THREE -> FIVE': '\\f.\\x.f (f (f (f (f x))))',
    }
    for title, source in EXAMPLES:
        if title == 'OMEGA: divergence, proves the step guard':
            continue
        term = parse(source, MACROS)
        trace, terminated = reduce_steps(term)
        assert terminated, title
        assert pretty(trace[-1]) == expected[title], title

    trace, terminated = reduce_steps(parse('OMEGA', MACROS), max_steps=10)
    assert not terminated
    assert len(trace) == 11

    print('all checks passed')
