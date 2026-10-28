# Week 7 — C(n, k): Recursion vs. Dynamic Programming

## The problem, in plain words

When selecting `k` objects from a collection of `n`, with sequence irrelevant, what is the total quantity of possible selections? This value is formally known as the binomial coefficient, typically denoted as `C(n, k)` or expressed as "`n choose k`". Although a well-known expression exists—`n! / (k! × (n-k)!)`—that equation merely delivers the final result. It omits the underlying reasoning and falls outside our current objectives. Instead, we will construct this quantity from a foundational premise: treating each selection as a binary choice regarding a single element. We will explore two distinct implementation strategies and examine the computational trade-offs involved. The file `comb.py` encapsulates both approaches alongside a simple verification step that confirms alignment with Python’s built-in `math.comb` across all inputs where `n ≤ 14`.

## The idea both versions share: Pascal's rule

Consider arranging your `n` elements and isolating the final entry. That specific item either belongs to your target subset of size `k` or remains excluded. These two scenarios partition all possible valid combinations completely:

- **Included:** You must now select `k-1` additional items from the remaining `n-1`. This yields `C(n-1, k-1)` possibilities.
- **Excluded:** You must gather all `k` items from the remaining `n-1`. This yields `C(n-1, k)` possibilities.

Summing these branches accounts for every valid combination exactly once, without overlap or omission:

```
C(n, 0) = C(n, n) = 1                      (selecting none, or selecting all)
C(n, k) = C(n-1, k-1) + C(n-1, k)           (last element present, or absent)
```

This relationship mirrors Pascal's triangle—familiar from earlier mathematics education—except expressed through iterative updates rather than visual rows. Both implementations within `comb.py` rely on this exact mathematical identity; their distinction lies solely in traversal methodology.

## Version 1: recursion, the straightforward way (non-DP)

```python
def c_recursive(n: int, k: int) -> int:
    if k == 0 or k == n:
        return 1
    return c_recursive(n - 1, k - 1) + c_recursive(n - 1, k)
```

The code directly translates the mathematical identity into executable steps. Rather than caching intermediate results, each invocation simply delegates to two subordinate queries and aggregates their returns. While accurate and conceptually clean, this approach suffers from hidden inefficiency that becomes apparent during execution. Invoke `c_recursive(5, 2)` as an example: it triggers `c_recursive(4, 1)` alongside `c_recursive(4, 2)`. Examining further reveals that `c_recursive(4, 1)` invokes `c_recursive(3, 1)`, yet `c_recursive(4, 2)` independently triggers the exact same call via an alternate path. Identical parameters produce identical outputs, yet the computation repeats itself repeatedly, worsening dramatically as depth increases due to binary branching at every step.

**Why duplication explodes — shared subproblems.** The invocation hierarchy resembles this structure (abbreviated):

```
                    C(5,2)
                 /          \
           C(4,1)              C(4,2)
          /     \              /     \
     C(3,0)   C(3,1)      C(3,1)   C(3,2)
                  \____________/
                 identical task,
                 recalculated independently twice
```

Nodes lacking base cases generate two descendants, causing identical `(n, k)` tuples to recur across separate execution paths. This pattern precisely defines the scenario where dynamic optimization proves essential: decomposing a task into overlapping fragments that repeatedly require evaluation.

**Performance profile.** Every invocation performs constant-time operations while spawning two successors down to depth `n`. Consequently, total invocations scale proportionally to `C(n, k)` itself. When `k` approaches `n/2`, this scales exponentially with respect to `n` (approximately `O(2^n)` in worst-case scenarios). Execute `c_recursive(30, 15)` to observe processor strain firsthand. Memory consumption remains modest at `O(n)`, restricted solely to the execution stack frames required per depth level.

## Version 2: dynamic programming — remember, don't recompute

```python
def c_dp(n: int, k: int) -> int:
    table = [[0] * (k + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        for j in range(min(i, k) + 1):
            table[i][j] = 1 if j == 0 or j == i else table[i - 1][j - 1] + table[i - 1][j]
    return table[n][k]
```

While utilizing the identical mathematical principle—the inclusion or exclusion of the final element—this method inverts the evaluation direction. Rather than decomposing queries recursively and duplicating derivations, it iteratively constructs results forward, storing each outcome within a matrix as progress advances. Index `i` within the matrix represents the complete set of combinations for that specific item count. The initial row contains merely `[1]`, reflecting the single method of selecting zero elements from an empty set, while subsequent rows derive exclusively from their immediate predecessors.

Since each `(i, j)` coordinate undergoes calculation a single time and subsequently serves as a reference point for future dependencies, the repetitive overhead observed in the recursive variant vanishes completely. This strategy trades elegance for systematic record-keeping.

**Performance profile.** The matrix contains approximately `n × k` entries, each requiring constant-time population by summing two prior values. Execution duration therefore scales at `O(n·k)`. Memory allocation similarly occupies `O(n·k)` capacity to preserve the stored results—this is the necessary trade-off for avoiding redundant calculation. (Should only the terminal row prove necessary rather than the complete structure, storage could theoretically collapse into a linear `O(k)` array updated iteratively. `comb.py` retains the two-dimensional layout strictly for pedagogical clarity regarding Pascal's triangle geometry, not functional necessity.)

## Side by side

| | `c_recursive` (non-DP) | `c_dp` (DP) |
|---|---|---|
| Methodology | Regenerates the recurrence independently per invocation | Populates a matrix sequentially, retrieving stored values |
| Execution Speed | `O(2^n)` worst case — expands rapidly | `O(n·k)` — scales linearly relative to inputs |
| Memory Footprint | `O(n)` stack frames | `O(n·k)` matrix allocation |
| Repetitive Operations | Severe — identical `(i, j)` evaluated across multiple paths | Eliminated — each `(i, j)` addressed precisely once |
| Ideal Scenario | Minimal `n`, or when seeking straightforward formula evaluation | Substantial `n` where execution duration matters |

## The actual lesson here

Dynamic programming does not introduce a novel computational technique; rather, it applies the identical recursive relationship within an execution sequence designed to cache results rather than recalculate them. Recognizing when optimization becomes beneficial relies on identifying persistent repetition within the call hierarchy, not merely spotting mathematical or recursive phrasing. If a dependency graph repeatedly requests identical states, exchanging storage for indexed retrieval transforms explosive growth into manageable scaling. Conversely, absent such duplication, caching offers no advantage and merely introduces unnecessary overhead—standard recursion remains entirely sufficient in those contexts.

## Running it

```
python3 comb.py
```

Executing this script iterates through all valid combinations where `n` spans from 0 to 14, and for each, `k` ranges from 0 to `n`. It verifies that both `c_recursive` and `c_dp` produce outputs perfectly matching Python's native `math.comb`. The upper bound intentionally terminates at 14. Because the recursive variant operates exponentially, the limit exists solely to demonstrate performance degradation without inducing excessive waiting times.