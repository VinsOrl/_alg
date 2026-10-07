"""Hand-made map / filter / reduce, and bubble sort with no loops (recursion only)."""
import random

_MISSING = object()


def my_map(f, xs):
    return [] if not xs else [f(xs[0])] + my_map(f, xs[1:])


def my_filter(pred, xs):
    if not xs:
        return []
    return ([xs[0]] if pred(xs[0]) else []) + my_filter(pred, xs[1:])


def my_reduce(f, xs, init=_MISSING):
    if init is _MISSING:
        if not xs:
            raise TypeError('my_reduce() of empty sequence with no initial value')
        return my_reduce(f, xs[1:], xs[0])
    return init if not xs else my_reduce(f, xs[1:], f(init, xs[0]))


def bubble_pass(xs):
    """One bubble pass: compare neighbours, the larger one keeps moving right."""
    def step(acc, x):
        done, carry = acc
        return (done + [x], carry) if carry > x else (done + [carry], x)
    done, last = my_reduce(step, xs[1:], ([], xs[0]))
    return done + [last]


# ponytail: recursion depth caps input at ~900 items and slicing is O(n^2) memory; fine for homework
def bubble_sort(xs):
    if len(xs) <= 1:
        return list(xs)
    passed = bubble_pass(xs)
    return bubble_sort(passed[:-1]) + [passed[-1]]


if __name__ == '__main__':
    nums = [1, 2, 3, 4, 5]
    print('map square :', my_map(lambda x: x * x, nums))
    print('filter even:', my_filter(lambda x: x % 2 == 0, nums))
    print('reduce sum :', my_reduce(lambda a, x: a + x, nums))
    data = [64, 34, 25, 12, 22, 11, 90, 5]
    print('bubble_sort:', data, '->', bubble_sort(data))

    assert my_reduce(lambda a, x: a, [1, 2], None) is None
    cases = [[], [1], [2, 1], [3, 3, 1], [-5, 0, -1, 7], list(range(20, 0, -1))]
    cases += [[random.randint(-50, 50) for _ in range(random.randint(0, 30))] for _ in range(50)]
    for c in cases:
        assert bubble_sort(c) == sorted(c), c
    print('all checks passed')
