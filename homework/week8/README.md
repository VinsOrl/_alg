# Week 8 Traveling Salesman Problem: Five Ways to Attack It

## The problem

A salesman has to visit every city on a list exactly once and get back home,
and he wants the shortest possible route. That's it — that's the whole
problem. It sounds simple, but it's one of the most famous hard problems in
computer science: the number of possible routes through `n` cities is
`(n-1)!/2`, so for anything beyond ~15 cities, checking every route is out
of the question. You need a strategy that gets you a *good* route without
checking all of them.

`tsp.py` holds five different strategies. They all work on the same
representation: a tour is just a list of city indices in visiting order
(city 0, then city 1, then city 2, ...), and the "cost" of a tour is the
total distance if you walk it in a loop and come back to the start.

```python
def tour_length(tour, points):
    return sum(dist(points[tour[i]], points[tour[(i+1) % len(tour)]]) for i in range(len(tour)))
```

The five methods differ in *how* they build or improve that list, not in
how they measure it.

## 1. Greedy — nearest neighbor

The simplest thing you could possibly do: start somewhere, and at every
step walk to whichever unvisited city is closest right now. No lookahead,
no backtracking, no do-overs.

```python
def greedy(points, start=0):
    unvisited = set(range(n)) - {start}
    tour = [start]
    while unvisited:
        last = tour[-1]
        nxt = min(unvisited, key=lambda c: dist(points[last], points[c]))
        tour.append(nxt)
        unvisited.remove(nxt)
    return tour
```

This is fast (`O(n²)`) and it's a genuinely reasonable first guess. Its
weakness is that being greedy early costs you later: you keep picking the
closest city and eventually paint yourself into a corner, leaving one or
two far-flung cities that have to be stitched in at the very end with a
long, ugly detour. Every other method in this file starts from either a
random tour or this greedy tour, then tries to fix that kind of mistake.

## 2. The Improvement Method — 2-opt

This is the classic "look at my tour and see if I can un-cross it" move.
Picture the tour as a loop drawn on paper. If two of its edges cross each
other, you can almost always shorten the loop by reversing the stretch of
the path between them — like untangling a twisted rubber band.

Concretely: pick two edges `(a,b)` and `(c,d)` in the tour. Check whether
`dist(a,c) + dist(b,d)` is shorter than `dist(a,b) + dist(c,d)`. If it is,
reverse the segment between them and keep going. Repeat over every pair of
edges, over and over, until no reversal helps anymore.

```python
def improvement(tour, points):
    while improved:
        for i in range(n-1):
            for j in range(i+2, n):
                old = dist(a,b) + dist(c,d)
                new = dist(a,c) + dist(b,d)
                if new < old:
                    tour[i+1:j+1] = reversed(tour[i+1:j+1])
```

This is the single most effective cheap trick for TSP — it's what every
other search in this file is implicitly trying to approximate with less
structure. Run it on top of the greedy tour and it reliably shaves off a
meaningful chunk of distance by untangling the mess greedy left behind.

## 3. Hill Climbing — random swaps, only accept wins

Hill climbing is the laziest form of local search: stand on the hillside,
take a random step, and only keep it if it took you higher (here, "higher"
means "shorter tour"). No planning, no memory of past attempts, no way to
tolerate a step backward.

```python
def hill_climbing(points, iters=2000):
    tour = random shuffle
    for _ in range(iters):
        i, j = two random positions
        swap tour[i], tour[j]
        if the swap helped: keep it
        else: undo it
```

It's cheap and it does improve a random tour quite a bit. But "only ever
go downhill" is also its curse: once it reaches a tour where every single
swap makes things worse, it's stuck there for good, even if a much better
tour exists two swaps away. That stuck point is called a *local optimum*,
and it's the central problem the next two methods are built to deal with.

## 4. Gradient Descent — steepest descent among the neighbors

TSP doesn't actually have a gradient — there's no smooth surface to take a
derivative of, just a pile of discrete swaps. So "gradient descent" here
means the next best thing: at every step, instead of trying one random
swap like hill climbing does, look at *every possible swap* and take
whichever one shrinks the tour the most. That's the discrete analogue of
"follow the steepest direction downhill."

```python
def gradient_descent(points, max_steps=200):
    for _ in range(max_steps):
        best_swap = the single swap (i, j) that shrinks the tour the most
        if no swap helps: stop
        apply best_swap
```

This converges in far fewer steps than hill climbing because it's not
wasting moves on random tries — every step is the best available one. The
trade-off is cost: scanning every pair of cities at every step is `O(n²)`
per step, versus hill climbing's `O(1)` per step. And it has exactly the
same weakness as hill climbing underneath: it only ever accepts
improvements, so it converges to a local optimum and stops there, just
faster and more directly.

## 5. Simulated Annealing — sometimes accept a worse move

This is the one that actually tries to solve the local-optimum problem.
The idea is borrowed from metallurgy: heat a metal up and let it cool
slowly, and the atoms settle into a much more stable arrangement than if
you'd just dunked it in cold water. Translated into search terms: early
on, accept worse moves fairly often (so the search can climb back down out
of a bad valley and explore); as time goes on, accept worse moves less and
less (so it settles down and fine-tunes).

```python
def simulated_annealing(points, iters=5000, t_start=10.0, t_end=1e-3):
    t = t_start
    for _ in range(iters):
        swap two random cities
        delta = new_len - cur_len
        if delta < 0 or random() < exp(-delta / t):
            keep the swap   # a worse move is still sometimes kept
        else:
            undo it
        t *= cooling_rate   # temperature keeps dropping
        remember the best tour seen so far
```

The `exp(-delta/t)` line is the whole trick: when `t` is high, that
probability stays close to 1 even for a fairly bad `delta`, so almost
anything gets accepted. When `t` has cooled down near zero, that
probability collapses to nearly 0 for any `delta > 0`, so it behaves just
like hill climbing. It's hill climbing with a dial that starts at
"accept almost anything" and ends at "accept almost nothing."

## Side by side

| | Greedy | Improvement (2-opt) | Hill Climbing | Gradient Descent | Simulated Annealing |
|---|---|---|---|---|---|
| What it does | Always walk to the closest unvisited city | Un-crosses edges until none cross | Random swap, keep only if better | Best possible swap, every step | Random swap, sometimes keep it anyway |
| Can escape a local optimum? | n/a (no improvement step) | No | No | No | Yes, especially early on |
| Cost per step | — | `O(n²)` per pass | `O(n)` to score a swap | `O(n²)` per step | `O(n)` to score a swap |
| Where it tends to land | Decent but with a "painted into a corner" flaw | Big, reliable improvement over greedy | Local optimum, somewhat random quality | Local optimum, reached fast | Usually the best of the five, given enough iterations |

## The actual lesson here

Four of these five methods (hill climbing, 2-opt, gradient descent, and
simulated annealing) are really the same idea wearing different clothes:
try a small change to the tour, and decide whether to keep it. The only
real design decisions are (1) which changes you're even allowed to try —
a random swap vs. every possible swap vs. a segment reversal — and
(2) how picky you are about keeping them — only strict improvements, or
occasionally something worse. Greedy is the odd one out: it never looks
back at a tour it already built, it only makes one irreversible decision
after another. Running greedy first and then letting one of the other four
methods clean it up (like `improvement(greedy(points), points)`) is usually
a better use of the same code than starting any of them from a random
shuffle.

## Running it

```
python3 tsp.py
```

This checks all five methods against a 4-city square where the optimal
tour length is known exactly (`4.0`), then runs them on 20 random cities
and prints each method's tour length next to the greedy baseline, so you
can see how much each one improves on it.

Note on the output: `greedy` doesn't get its own printed row in that final
comparison — all five methods are implemented and all five run, but
`greedy`'s result is what's shown as the "(greedy: ...)" baseline next to
the other four, and it's also the tour that gets handed to `improvement()`
to clean up. It's still a complete, independent algorithm (`greedy()` in
`tsp.py`), just displayed as the point of comparison rather than a row of
its own.
