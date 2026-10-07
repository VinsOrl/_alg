"""Tower of Hanoi: recursive and non-recursive (explicit stack) solutions."""


def hanoi_rec(n, src='A', dst='C', aux='B'):
    if n <= 0:
        return []
    return hanoi_rec(n - 1, src, aux, dst) + [(n, src, dst)] + hanoi_rec(n - 1, aux, dst, src)


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


def check(n, moves):
    pegs = {'A': list(range(n, 0, -1)), 'B': [], 'C': []}
    for disk, s, d in moves:
        assert pegs[s] and pegs[s][-1] == disk, f'disk {disk} not on top of {s}'
        assert not pegs[d] or pegs[d][-1] > disk, f'disk {disk} placed on smaller disk'
        pegs[d].append(pegs[s].pop())
    assert pegs['C'] == list(range(n, 0, -1)) and len(moves) == 2 ** n - 1


if __name__ == '__main__':
    for n in range(11):
        rec, it = hanoi_rec(n), hanoi_iter(n)
        assert rec == it
        check(n, rec)
    for disk, s, d in hanoi_iter(3):
        print(f'move disk {disk} from {s} to {d}')
    print('all checks passed')
