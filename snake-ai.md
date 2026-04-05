# Snake AI — Feature & Implementation Log

## Current version: v2 — Open-Space Seeking

### File
`snake_ai.py` — `SnakeAI.decide(snake, all_occupied)`

### How it works
1. Collect all three non-reverse directions.
2. Filter to those that step to an **in-bounds, unoccupied** cell.
3. Score each safe direction:
   - **open_neighbors**: number of free in-bounds cells adjacent to the destination cell (0-4).
   - **straight bonus**: +0.3 for continuing in the current direction (reduces jitter).
   - **noise**: uniform random 0–0.4 (breaks ties, adds unpredictability).
4. Pick the direction with the highest score.
5. If no direction is safe, hold course (snake will die on the next step).

`all_occupied` contains bodies of **all** snakes — alive AND dead — so dead snake
bodies act as solid permanent obstacles.

### What it avoids
- Grid border collisions
- Other snake bodies (alive and dead)
- Self-body collisions (own body is part of `all_occupied`)

### What it does NOT handle
- Food seeking (no targeting)
- Head-to-head collision prediction (doesn't anticipate where other snakes will be next tick)
- Long-term path planning (looks only 1 step + 1 neighbor level ahead)

### Known limitations
- Still gets trapped in shrinking pockets because it only evaluates immediate
  open neighbors, not total reachable area (flood-fill would fix this — see v3).
- Can still loop in open areas if noise repeatedly favours the same sub-optimal path.

---

## Planned / Future AI levels

| Level | Name | Description |
|---|---|---|
| v2 | Body-aware | Extend safe-cell check to also exclude all other snakes' bodies |
| v3 | Flood-fill | Before turning, flood-fill to estimate reachable cells; prefer the larger region |
| v4 | Food-seeking | A* or greedy pathfinding toward the food pellet when safe |
| v5 | Aggressive | Predict other snakes' next head positions and cut them off |

---

## Integration points

- `game.py` instantiates one shared `SnakeAI()` and calls `ai.decide(snake, all_occupied)`
  once per snake per game tick (inside the `SPEED_NORMAL` timer block).
- `all_occupied` is a `set` of `(x, y)` grid cells from all living snakes built
  *before* any snake moves that tick — available for future AI levels to use.
- Each `Snake` exposes `.next_dir`, `.head()`, `.body`, `.alive`, and `.score`.
