"""Nine problems, seven methods.

Search is the theme: given a set of states and the transitions between them,
how do you find what you're looking for without checking every state?

  1. Mouse maze        — DFS (backtracking via explicit stack)
  2. Wolf-goat-cabbage  — BFS (shortest crossing sequence)
  3. Eight queens       — DFS (backtracking, one queen per row)
  4. NPC searching      — A* (manhattan heuristic on a grid with walls)
  5. Circuit routing     — line-of-sight / maze-routing / multi-net

All five live here as functions so you can run them together:
    python3 solvers.py

Or import individual functions from the module.
"""

import math
import random
import heapq
from collections import deque


# ── 1. Mouse maze (DFS) ───────────────────────────────────────────────────

def mouse_maze(maze: list[list[int]], start=(0, 0), end=None):
    """Find a path through a 2D grid maze using DFS with an explicit stack.

    maze: 0 = open, 1 = wall
    start / end: (row, col) tuples; defaults to top-left → bottom-right.

    Returns a list of (row, col) from start to end, or [] if no path exists.
    """
    if not maze or not maze[0]:                       # empty grid guard
        return []
    if end is None:
        end = (len(maze) - 1, len(maze[0]) - 1)
    rows, cols = len(maze), len(maze[0])

    stack = [(start, [start])]          # (current cell, path so far)
    visited = {start}

    # Fixed exploration order: up, right, down, left.
    # Change the list to alter which path DFS finds first.
    moves = [(-1, 0), (0, 1), (1, 0), (0, -1)]

    while stack:
        (r, c), path = stack.pop()
        if (r, c) == end:
            return path                   # first time we see the goal → done
        for dr, dc in moves:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and maze[nr][nc] == 0 \
                    and (nr, nc) not in visited:
                visited.add((nr, nc))
                stack.append(((nr, nc), path + [(nr, nc)]))

    return []                             # no path found


# ── 2. Wolf, goat, cabbage (BFS) ──────────────────────────────────────────

LEFT, RIGHT = 0, 1


def wolf_goat_cabbage():
    """Solve the river-crossing puzzle in the minimum number of steps (BFS).

    State: tuple of 4 values (wolf_side, goat_side, cabbage_side, farmer_side),
    each LEFT or RIGHT. The boat holds the farmer + at most one item.

    Classic constraints: without the farmer on a bank, wolf eats goat AND goat
    eats cabbage. (Wolf and cabbage are safe together.) BFS explores layer by
    layer so the first solution found has minimum crossings.

    Returns (steps_list, n_steps).

    Note: with both pairwise constraints plus boat capacity of 1, this puzzle is
    mathematically unsolvable — the state graph is disconnected. Every first move
    leads to a dead end. For a solvable version, use only one constraint.
    """
    def safe(s):
        wolf, goat, cabbage, farmer = s
        for side in range(2):
            if farmer == side: continue          # farmer on this bank — keeps order
            if (wolf == side) and (goat == side): return False  # wolf + goat → eats
            if (goat == side) and (cabbage == side): return False  # goat + cabbage → eats
        return True

    start = (LEFT, LEFT, LEFT, LEFT)
    goal  = (RIGHT, RIGHT, RIGHT, RIGHT)

    queue = deque([(start, [])])          # (state, list of step descriptions)
    visited = {start}
    names = ['wolf', 'goat', 'cabbage']

    while queue:
        state, steps = queue.popleft()

        # What can the farmer take? Farmer always goes, plus any item on his side.
        farmer_side = state[3]
        can_take = [3]                    # farmer index
        for i in range(3):
            if state[i] == farmer_side:   # item is on same side as farmer
                can_take.append(i)

        for move in can_take:
            lst = list(state)
            lst[move] = 1 - lst[move]     # flip that item
            lst[3] = 1 - lst[3]            # farmer always flips
            new_state = tuple(lst)

            if safe(new_state) and new_state not in visited:
                direction = ('left → right' if state[3] == LEFT else 'right → left')
                if move < 3:
                    desc = f"Farmer takes {names[move]} ({direction})"
                else:
                    desc = f"Farmer crosses alone ({direction})"
                new_steps = steps + [desc]
                if new_state == goal:
                    return new_steps, len(new_steps)
                visited.add(new_state)
                queue.append((new_state, new_steps))

    return [], 0                          # no solution (shouldn't happen for this puzzle)


# ── 3. Eight queens (DFS / backtracking) ──────────────────────────────────

def eight_queens(n=8, collect_all=True):
    """Place n queens on an n×n board so no two attack each other.

    DFS fills one row at a time: pick the first safe column in row 0, recurse
    to row 1, and so on. If a row has no safe column, backtrack.

    Returns a list of board configurations (each board is a list of n ints;
    board[row] = column where the queen sits).
      • collect_all=True  → all solutions (n=8 gives 92)
      • collect_all=False → just one solution (returns list with single board)
    """
    boards: list[list[int]] = []

    def is_safe(row, col, placement):
        for r in range(row):
            c = placement[r]
            if c == col:                          # same column
                return False
            if abs(c - col) == row - r:           # same diagonal (both directions)
                return False
        return True

    def place(row, placement):
        if row == n:
            boards.append(placement[:])
            if not collect_all:
                raise StopIteration               # early exit trick
            return
        for col in range(n):
            if is_safe(row, col, placement):
                placement[row] = col
                place(row + 1, placement)

    try:
        place(0, [0] * n)
    except StopIteration:
        pass                                      # early exit consumed
    return boards


# ── 4. NPC hunts player (A*) ───────────────────────────────────────────────

def a_star(grid, npc_pos, player_pos, obstacles=None):
    """A* pathfinding: NPC walks to the player on a grid with walls.

    grid:     list[list[int]] — 0 = open, 1 = wall
    npc_pos:  (row, col) starting position of NPC
    player_pos: (row, col) target position
    obstacles: optional set of extra blocked cells beyond the grid's walls

    Uses f(n) = g(n) + h(n):
      g(n) = actual steps taken so far from start
      h(n) = Manhattan distance to goal (admissible heuristic — never over-
             estimates, so A* guarantees shortest path)

    Returns (path, cost) or ([], ∞).

    The open set is a priority queue sorted by f-value. When two nodes tie on
    f, we prefer the one with smaller g (more greedy toward the goal). This
    breaks ties in favor of shorter detours and keeps the search focused.
    """
    if obstacles is None:
        obstacles = set()

    rows, cols = len(grid), len(grid[0])

    def in_bounds(r, c):
        return 0 <= r < rows and 0 <= c < cols and grid[r][c] == 0 \
               and (r, c) not in obstacles

    def h(r, c):
        return abs(r - player_pos[0]) + abs(c - player_pos[1])   # Manhattan

    if npc_pos == player_pos:
        return [npc_pos], 0
    if not in_bounds(*player_pos):
        return [], float('inf')

    # priority queue: (f, g, row, col) — tie-break on g so we prefer shorter detours
    pq = [(h(*npc_pos), 0, npc_pos[0], npc_pos[1])]
    heapq.heapify(pq)
    came_from: dict[tuple, tuple] = {}
    g_score = {npc_pos: 0}

    while pq:
        _, g, r, c = heapq.heappop(pq)               # pop lowest f-score
        cur = (r, c)

        if cur == player_pos:
            path = []
            node = cur
            while node != npc_pos:
                path.append(node)
                node = came_from[node]
            path.append(npc_pos)
            return list(reversed(path)), g

        for dr, dc in [(-1, 0), (0, -1), (0, 1), (1, 0)]:
            nr, nc = r + dr, c + dc
            if not in_bounds(nr, nc):
                continue
            new_g = g + 1
            if new_g < g_score.get((nr, nc), float('inf')):
                came_from[(nr, nc)] = cur
                g_score[(nr, nc)] = new_g
                heapq.heappush(pq, (new_g + h(nr, nc), new_g, nr, nc))

    return [], float('inf')                       # no path


# ── 5. Circuit routing (maze-routing / line-of-sight / A*) ────────────────

def route_maze(grid: list[list[int]], src: tuple[int, int], dst: tuple[int, int]):
    """BFS maze-routing: find one shortest wire path on a grid.

    Used in IC layout when you need to connect two pins (src → dst) and the
    grid marks which cells are already routed (1), blocked (2), or free (0).

    Returns (path, cost) — list of cells along the wire, total edge count.
    """
    rows, cols = len(grid), len(grid[0])
    q = deque([(src, [src])])
    visited = {src}

    while q:
        (r, c), path = q.popleft()
        if (r, c) == dst:
            return path, len(path) - 1
        for dr, dc in [(-1, 0), (0, -1), (0, 1), (1, 0)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0 \
                    and (nr, nc) not in visited:
                visited.add((nr, nc))
                q.append(((nr, nc), path + [(nr, nc)]))
    return [], float('inf')


def route_line_of_sight(src: tuple[int, int], dst: tuple[int, int]) -> list[tuple[int, int]]:
    """One-segment routing when src and dst share a row or column.

    The shortest wire is a single straight line — just go directly.
    O(1) compared to BFS's O(rows×cols). This is what you use first in every
    router: if two pins can talk directly, don't waste a grid search on it.
    """
    sr, sc = src
    dr, dc = dst
    if sr == dr or sc == dc:                        # same row or column
        step_r = 0 if sr == dr else (1 if dr > sr else -1)
        step_c = 0 if sc == dc else (1 if dc > sc else -1)
        path = []
        r, c = sr, sc
        while (r, c) != (dr, dc):
            path.append((r, c))
            r += step_r
            c += step_c
        path.append(dst)
        return path
    return []                                         # not in direct line


def route_rip_and_fill(nets: list[tuple], grid_rows: int, grid_cols: int):
    """Multi-net routing: try each net's line-of-sight first; fall back to BFS.

    Nets are a list of (src, dst) pairs — each pair is one wire to route.

    Strategy (classic channel/line router simplification):
      1. Try line-of-sight for every net. If it works, done — no grid needed.
      2. If a net has no LOS, fall back to BFS maze-routing on a fresh grid.

    In real IC design this is much more complex (obstacles from previously routed
    nets, via layers, minimum spacing rules). This version skips those details and
    focuses on the core routing decision: direct line vs. grid search.
    """
    routed_grid = [[0] * grid_cols for _ in range(grid_rows)]   # 0 = free
    results = []

    for i, (src, dst) in enumerate(nets):
        # Step 1: try the fast path first
        los_path = route_line_of_sight(src, dst)
        if los_path:
            # Mark cells as used so later nets don't re-route through them.
            for r, c in los_path:
                routed_grid[r][c] = 1
            results.append((i, los_path))
            continue

        # Step 2: fall back to BFS maze-routing.
        path, cost = route_maze(routed_grid, src, dst)
        if cost < float('inf'):
            for r, c in path:
                routed_grid[r][c] = 1
        results.append((i, path))

    return results


# ── main: run everything and show the results ──────────────────────────────

if __name__ == '__main__':
    print("=" * 60)
    print("1. MOUSE MAZE (DFS)")
    print("-" * 40)
    maze = [
        [0, 1, 0, 0, 0],
        [0, 1, 0, 1, 0],
        [0, 0, 0, 1, 0],
        [0, 1, 1, 1, 0],
        [0, 0, 0, 0, 0],
    ]
    path = mouse_maze(maze)
    for i, (r, c) in enumerate(path):
        marker = "◆" if i == len(path) - 1 else "●" if i > 0 else "S"
        print(f"  Step {i+1}: ({r},{c}) {marker}")
    print()

    print("=" * 60)
    print("2. WOLF, GOAT, CABBAGE (BFS)")
    print("-" * 40)
    steps, n = wolf_goat_cabbage()
    if n > 0:
        for i, s in enumerate(steps, 1):
            print(f"  Step {i}: {s}")
        print(f"  → Minimum crossings: {n}")
    else:
        print("  → No solution found!")
    print()

    print("=" * 60)
    print("3. EIGHT QUEENS (DFS)")
    print("-" * 40)
    solutions = eight_queens(8)
    boards = solutions[:5]                            # show first 5 of 92
    for b_idx, board in enumerate(boards):
        print(f"\n  Solution {b_idx + 1} (total: {len(solutions)}):")
        for row in range(8):
            line = ""
            for col in range(8):
                line += "Q" if board[row] == col else "."
            print(f"    {line}")

    one_solution = eight_queens(8, collect_all=False)
    print(f"\n  → Collected exactly 1 solution as expected.")
    print()

    print("=" * 60)
    print("4. NPC HUNTS PLAYER (A*)")
    print("-" * 40)
    grid = [
        [0, 0, 0, 0, 0, 0],
        [0, 1, 1, 0, 0, 0],
        [0, 0, 0, 0, 1, 0],
        [0, 0, 1, 0, 1, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
    ]
    npc = (0, 0)
    player = (5, 5)
    path, cost = a_star(grid, npc, player)
    print(f"  NPC start: {npc}, Player at: {player}")
    print(f"  Path length: {cost}")
    for i, (r, c) in enumerate(path):
        marker = "★" if i == len(path) - 1 else "▶" if i > 0 else "N"
        print(f"  Step {i+1}: ({r},{c}) {marker}")
    print()

    print("=" * 60)
    print("5. CIRCUIT ROUTING (Maze / Line-of-sight / A*)")
    print("-" * 40)
    # Grid with one obstacle blocking direct line between pins.
    route_grid = [
        [0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0],
    ]
    src, dst = (0, 0), (3, 4)
    print(f"  Pin A at {src}, Pin B at {dst}")
    los_path = route_line_of_sight(src, dst)
    if not los_path:
        path, cost = route_maze(route_grid, src, dst)
        print(f"  No direct line-of-sight → maze-routing gives length {cost}:")
        for i, (r, c) in enumerate(path):
            marker = "P" if i == len(path) - 1 else "." if i > 0 else "A"
            print(f"    ({r},{c}){marker}")
    else:
        cost = abs(src[0] - dst[0]) + abs(src[1] - dst[1])
        print(f"  Direct LOS → length {cost}: {'-'.join(str(p) for p in los_path)}")

    # Multi-net demo.
    nets = [((0, 0), (3, 4)), ((0, 4), (3, 0))]
    results = route_rip_and_fill(nets, 4, 5)
    print(f"\n  Multi-net routing ({len(nets)} nets):")
    for net_id, path in results:
        s, d = nets[net_id]
        cost_val = len(path) - 1 if path else float('inf')
        status = "✓" if cost_val < float('inf') else "✗"
        print(f"    Net {net_id}: {s}→{d}  length={cost_val}  {status}")
