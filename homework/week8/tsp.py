"""Traveling Salesman Problem, five ways.

All five share one neighborhood: a tour is a permutation of city indices,
and a "move" either swaps two positions or reverses a segment (2-opt).
Only the construction/acceptance rule differs between methods.

- greedy:              nearest-neighbor construction, no improvement.
- improvement (2-opt): repeatedly reverse a segment if it shortens the tour,
                        until no reversal helps (classic local search for TSP).
- hill_climbing:        random swap moves, keep only if the swap improves
                        the tour (stochastic first-improvement).
- gradient_descent:     steepest-descent sibling of hill climbing: each step
                        checks every swap and takes the single best one,
                        stopping at a local optimum. TSP has no real gradient
                        (it's discrete), so "steepest among neighbors" stands
                        in for the gradient direction.
- simulated_annealing:  swap moves like hill climbing, but worse swaps are
                        accepted with probability exp(-delta/T) as T cools,
                        letting it escape local optima hill climbing can't.
"""

import math
import random


def dist(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def tour_length(tour: list[int], points: list[tuple[float, float]]) -> float:
    return sum(dist(points[tour[i]], points[tour[(i + 1) % len(tour)]]) for i in range(len(tour)))


def swap_delta(tour: list[int], points: list[tuple[float, float]], i: int, j: int) -> float:
    """Change in tour length from swapping positions i and j, without rebuilding the tour.

    Only the edges touching i and j change, so this is O(1) instead of the
    O(n) of swapping and re-running tour_length.
    """
    n = len(tour)
    if i == j:
        return 0.0
    if i > j:
        i, j = j, i
    a, b = tour[i], tour[j]
    ip, inx = points[tour[i - 1]], points[tour[(i + 1) % n]]
    jp, jnx = points[tour[j - 1]], points[tour[(j + 1) % n]]
    if (i + 1) % n == j:  # adjacent: ip - a - b - jnx
        old = dist(ip, points[a]) + dist(points[a], points[b]) + dist(points[b], jnx)
        new = dist(ip, points[b]) + dist(points[b], points[a]) + dist(points[a], jnx)
    elif (j + 1) % n == i:  # adjacent across the wrap: jp - b - a - inx
        old = dist(jp, points[b]) + dist(points[b], points[a]) + dist(points[a], inx)
        new = dist(jp, points[a]) + dist(points[a], points[b]) + dist(points[b], inx)
    else:
        old = dist(ip, points[a]) + dist(points[a], inx) + dist(jp, points[b]) + dist(points[b], jnx)
        new = dist(ip, points[b]) + dist(points[b], inx) + dist(jp, points[a]) + dist(points[a], jnx)
    return new - old


def greedy(points: list[tuple[float, float]], start: int = 0) -> list[int]:
    n = len(points)
    unvisited = set(range(n)) - {start}
    tour = [start]
    while unvisited:
        last = tour[-1]
        nxt = min(unvisited, key=lambda c: dist(points[last], points[c]))
        tour.append(nxt)
        unvisited.remove(nxt)
    return tour


def improvement(tour: list[int], points: list[tuple[float, float]]) -> list[int]:
    """2-opt: reverse any segment that shortens the tour, until none do."""
    tour = tour[:]
    n = len(tour)
    improved = True
    while improved:
        improved = False
        for i in range(n - 1):
            for j in range(i + 2, n):
                a, b, c, d = tour[i], tour[i + 1], tour[j], tour[(j + 1) % n]
                if i == 0 and j == n - 1:
                    continue
                old = dist(points[a], points[b]) + dist(points[c], points[d])
                new = dist(points[a], points[c]) + dist(points[b], points[d])
                if new < old - 1e-9:
                    tour[i + 1 : j + 1] = reversed(tour[i + 1 : j + 1])
                    improved = True
    return tour


def hill_climbing(points: list[tuple[float, float]], iters: int = 2000, seed: int | None = None) -> list[int]:
    rng = random.Random(seed)
    n = len(points)
    tour = list(range(n))
    rng.shuffle(tour)
    best_len = tour_length(tour, points)
    for _ in range(iters):
        i, j = rng.sample(range(n), 2)
        tour[i], tour[j] = tour[j], tour[i]
        new_len = tour_length(tour, points)
        if new_len < best_len:
            best_len = new_len
        else:
            tour[i], tour[j] = tour[j], tour[i]
    return tour


def gradient_descent(points: list[tuple[float, float]], max_steps: int = 200, seed: int | None = None) -> list[int]:
    rng = random.Random(seed)
    n = len(points)
    tour = list(range(n))
    rng.shuffle(tour)
    cur_len = tour_length(tour, points)
    for _ in range(max_steps):
        best_delta, best_swap = 0.0, None
        for i in range(n):
            for j in range(i + 1, n):
                delta = swap_delta(tour, points, i, j)
                if delta < best_delta - 1e-9:
                    best_delta, best_swap = delta, (i, j)
        if best_swap is None:
            break
        i, j = best_swap
        tour[i], tour[j] = tour[j], tour[i]
        cur_len += best_delta
    return tour


def simulated_annealing(
    points: list[tuple[float, float]],
    iters: int = 5000,
    t_start: float = 10.0,
    t_end: float = 1e-3,
    seed: int | None = None,
) -> list[int]:
    rng = random.Random(seed)
    n = len(points)
    tour = list(range(n))
    rng.shuffle(tour)
    cur_len = tour_length(tour, points)
    best_tour, best_len = tour[:], cur_len
    if iters == 0:
        return best_tour
    cooling = (t_end / t_start) ** (1 / iters)
    t = t_start
    for _ in range(iters):
        i, j = rng.sample(range(n), 2)
        tour[i], tour[j] = tour[j], tour[i]
        new_len = tour_length(tour, points)
        delta = new_len - cur_len
        if delta < 0 or rng.random() < math.exp(-delta / t):
            cur_len = new_len
            if cur_len < best_len:
                best_tour, best_len = tour[:], cur_len
        else:
            tour[i], tour[j] = tour[j], tour[i]
        t *= cooling
    return best_tour


def demo() -> None:
    rng0 = random.Random(42)
    sample_points = [(rng0.uniform(0, 10), rng0.uniform(0, 10)) for _ in range(8)]
    sample_tour = list(range(8))
    rng0.shuffle(sample_tour)
    for _ in range(50):
        i, j = rng0.sample(range(8), 2)
        before = tour_length(sample_tour, sample_points)
        expected_delta = swap_delta(sample_tour, sample_points, i, j)
        sample_tour[i], sample_tour[j] = sample_tour[j], sample_tour[i]
        after = tour_length(sample_tour, sample_points)
        assert abs((after - before) - expected_delta) < 1e-9, "swap_delta disagrees with brute force"

    square = [(0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)]
    optimal = 4.0

    assert simulated_annealing(square, iters=0) is not None

    g = greedy(square)
    assert sorted(g) == list(range(4))
    assert abs(tour_length(g, square) - optimal) < 1e-9

    imp = improvement(hill_climbing(square, iters=50, seed=1), square)
    assert abs(tour_length(imp, square) - optimal) < 1e-9

    gd = gradient_descent(square, seed=2)
    assert abs(tour_length(gd, square) - optimal) < 1e-9

    sa = simulated_annealing(square, iters=500, seed=3)
    assert abs(tour_length(sa, square) - optimal) < 1e-9

    rng = random.Random(0)
    points = [(rng.uniform(0, 100), rng.uniform(0, 100)) for _ in range(20)]
    greedy_tour = greedy(points)
    greedy_len = tour_length(greedy_tour, points)
    for name, result in [
        ("improvement", improvement(greedy_tour, points)),
        ("hill_climbing", hill_climbing(points, seed=0)),
        ("gradient_descent", gradient_descent(points, seed=0)),
        ("simulated_annealing", simulated_annealing(points, seed=0)),
    ]:
        assert sorted(result) == list(range(20)), f"{name} produced an invalid tour"
        print(f"{name:20s} {tour_length(result, points):8.2f}  (greedy: {greedy_len:.2f})")


if __name__ == "__main__":
    demo()
