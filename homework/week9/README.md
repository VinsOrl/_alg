# Week 9 — Five Search Problems, Seven Ways to Attack Them

A search problem: you have a bunch of possible states and the transitions between them. How do you find what you're looking for without checking everything?

Five problems. The answers share an idea but use very different algorithms. `solvers.py` has the code; run it with:

```
python3 solvers.py
```

---

## Mouse maze — DFS

A grid, a mouse at the top-left corner, a goal at the bottom-right. Walls are 1s, open cells are 0s. The mouse can move up, down, left, or right. Find any path to the exit.

DFS here just picks a direction and goes as far as it can. When it hits a wall or an already-visited cell, it backs up to the last intersection and tries somewhere else. If every reachable cell is visited without finding the goal, there's no path.

We use an explicit stack instead of recursion so the walk is easy to see — you can swap direction order by changing one list without touching recursive calls at all. The moment we pop the goal off the stack, the path we built to get there *is* the answer.

The tradeoff is honest: DFS gets you *a* path fast because it doesn't look ahead. It's just not guaranteed to be the shortest one. If you need minimum steps, use BFS instead — which explores layer by layer like ripples in a pond, checking every 1-step solution before any 2-step one.

---

## Wolf, goat, cabbage — BFS

Here's where things get interesting. Four things need to cross a river: a wolf, a goat, a cabbage, and a farmer. The boat holds the farmer plus one item at most. Left alone together, the wolf eats the goat and the goat eats the cabbage. What's the minimum number of crossings?

BFS is right for this because it checks every 1-step solution before any 2-step one, every 2-step before any 3-step. The first time it reaches the goal state (everyone on the far side), that path has the minimum number of moves — by construction, not luck.

**This puzzle is actually unsolvable.** With both constraints (wolf+goat AND goat+cabbage) and boat capacity of exactly 1 item, every first move leads to a dead end. Take the goat first: now you have wolf+goat on the far bank without supervision. Put it back and try the wolf: goat+cabbage together unsupervised. Try the cabbage first: same problem. The state graph is disconnected — no path from start to goal exists at all.

That sounds like a failure but it's actually the whole point of demonstrating BFS. It doesn't just find solutions — it correctly *proves* no solution exists by exhaustively exploring every reachable state and finding none match the goal. For a solvable version, use only one constraint (e.g., "goat eats cabbage" only).

---

## Eight queens — DFS with backtracking

Place 8 queens on an 8×8 board so no two attack each other. Row by row, column by column: try placing a queen in the first safe square of row 0, then do the same for row 1, and keep going. If you reach a row where every column is unsafe, backtrack — remove the queen from row N-1 and try its next column instead.

The safety check is one formula that catches everything: a new queen at `(row, col)` conflicts with an existing queen at `(r, placement[r])` if they share a column (`c == col`) or a diagonal (`abs(c - col) == row - r`). That's it — 8 directions of attack captured by two comparisons.

The classical board has exactly 92 solutions. That feels like a lot until you realize there are 8^8 = 16 million raw configurations. Backtracking prunes the search tree aggressively: once two queens share a column or diagonal, every configuration below that point is dead and gets cut off immediately.

---

## NPC hunts player — A*

An NPC on a grid needs to walk to the player's position. Walls block movement. Find the shortest valid path.

A* works by adding a compass to BFS. BFS spreads evenly in all directions like water — fine, but wasteful when you have a target. A* says: *explore what looks promising first.* It does this with `f(n) = g(n) + h(n)`:

- **g(n)** — exact steps taken to reach this cell from start
- **h(n)** — estimated distance remaining (Manhattan distance on a grid)
- **f(n)** — total estimated cost if you go through here

It pops the cell with the smallest f first, updates its neighbors, and repeats. On a large open grid, A* visits orders of magnitude fewer nodes than BFS because it's focused rather than scattered.

The Manhattan heuristic works because on an orthogonal grid (up/down/left/right only), the shortest possible path between two points is exactly `|r1-r2| + |c1-c2|`. And crucially, it never overestimates — which means A* is guaranteed to find the shortest path. If you could cheat with a heuristic that underestimates, you'd visit fewer nodes but might miss the optimal route. Overestimate and the algorithm breaks entirely.

---

## Circuit routing

In IC design, "routing" means connecting pins on a chip with metal wire without crossing anything that shouldn't be connected. It's one of the hardest problems in EDA (electronic design automation). This file strips it down to what actually matters for learning: three approaches layered from cheapest to most expensive.

**Line-of-sight.** If two pins share a row or column, go straight. O(1). Try this first — if you can route directly, don't waste compute on a grid search.

**Maze-routing (BFS).** When no direct line exists, find the shortest path around obstacles. Obstacles include walls plus any previously routed wires. This is the same BFS from problem 1 applied to chip layout.

**Multi-net routing.** Route nets one at a time: try line-of-sight first, fall back to BFS if blocked. Mark routed cells as obstacles so later nets work around existing wire. In real chip design this becomes exponentially harder — multiple metal layers, via connections, signal timing optimization, nets with 3+ pins, minimum spacing rules. The two-layer, two-pin version here captures the core idea: *try the simple thing first, fall back to search when it breaks.*

---

## Side by side

| Problem | Method | Shortest path? | Why this one |
|---------|--------|----------------|-------------|
| Mouse maze | DFS | No — finds any path quickly | Good enough when you just need an exit |
| River crossing | BFS | Yes, by construction | Small state space makes "check everything" cheap |
| Eight queens | DFS + backtracking | N/A — constraint satisfaction, not optimization | Backtracking prunes impossible branches instantly |
| NPC hunt | A* | Yes (with admissible heuristic) | Focused search visits far fewer nodes than BFS on large grids |
| Circuit LOS | Direct math | N/A — straight line by definition | O(1), beats any search algorithm |
| Circuit maze | BFS | Yes, on the grid | Reliable fallback when LOS fails |
| Circuit multi-net | LOS-first + BFS | Locally optimal only | Sequential routing isn't globally optimal; real routers use more complex strategies |

---

## The common thread

All seven methods are search. They differ in how they choose what to try next:

- **DFS** commits to one direction and goes deep — fast but blind to alternatives
- **BFS** checks everything at distance 1, then everything at distance 2, etc. — exhaustive but wasteful on directed problems
- **A*** sits between them — like BFS but ordered by promise rather than blindly

The maze and circuit routing use the same grid representation; it's just a question of whether you need *any* path or the *shortest* one. Eight queens has no concept of distance — it's pure constraint satisfaction where backtracking prunes entire branches when a single cell is wrong. And the river crossing puzzle, in its classic two-constraint form, teaches an important lesson: sometimes the right answer from a search algorithm is "there is no solution."

---

## Running it

```bash
cd week9
python3 solvers.py
```

This runs all five problems and prints the results. The maze shows step-by-step movement through walls. The river crossing prints "No solution found!" — which is correct for this version, not a bug. Eight queens displays the first 5 of 92 valid board layouts. The NPC demo walks through obstacles on a grid. Circuit routing shows both line-of-sight and BFS fallback with results for each net.
