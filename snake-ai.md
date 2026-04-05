# Snake AI — Feature & Implementation Log

## Current version: v4 — Food-Seeking + Flood-Fill Safety + Personality

### File
`snake_ai.py` — `SnakeAI.decide(snake, all_occupied, food_pos)`

### How it works
1. Collect all non-reverse directions that step to an in-bounds, unoccupied cell.
2. **Flood-fill** each candidate destination to count total reachable open area.
3. **BFS** from the snake's head to `food_pos` through unoccupied cells; record the first-step direction.
4. If the BFS food direction is a safe candidate **and** its flood-fill count >= personality threshold → chase food.
5. Otherwise → pick the candidate with the largest flood-fill area, with personality-scaled noise.

`all_occupied` contains bodies of **alive snakes only** — dead bodies become corpse food pellets.

### Personality (greediness)
Each snake is assigned `greediness = random.random()` at spawn (stored on the `Snake` object).

| greediness | behaviour |
|---|---|
| 0.0 (cautious) | Only chases food when flood-fill area >= full body length |
| 0.5 (balanced) | Chases food when area >= ~62% of body length |
| 1.0 (reckless) | Chases food when area >= ~25% of body length; very erratic fallback |

**Food-chase threshold**: `max(2, int(body_len * (1.0 - greediness * 0.75)))`

**Fallback noise scale**: `random.uniform(0, 0.5 + greediness * 1.5)` — greedy snakes pick
more erratically when not chasing food, while cautious snakes consistently prefer the safest route.

### Behaviour by snake size
| Snake length | Behaviour |
|---|---|
| Short (≤ 10) | Aggressively chases food; flood-fill threshold easily met |
| Medium | Chases food unless path leads into a tight space |
| Long (≥ 30+) | Often falls back to open-space routing; avoids tunnels that would trap it |

### What it avoids
- Grid border collisions
- Other alive snake bodies
- Self-trapping (flood-fill < threshold triggers safety fallback; threshold depends on greediness)

### What it does NOT handle
- Head-to-head collision prediction (doesn't model where other snakes will be next tick)
- Tail-chasing optimisation (treats own tail as permanently blocked; a snake could in theory follow its own tail through a tight space)

### Known limitations
- BFS treats the snake's own tail as permanently blocked, so paths through
  tight spaces that would open up as the tail retreats are rejected.
- No inter-snake coordination — two snakes may race for the same food and
  collide head-on.

---

## Planned / Future AI levels

| Level | Name | Description |
|---|---|---|
| v2 | Body-aware | Extend safe-cell check to also exclude all other snakes' bodies |
| v3 | Flood-fill | Before turning, flood-fill to estimate reachable cells; prefer the larger region |
| v4 | Personality + Corpse-seeking | Per-snake greediness; dead bodies become food; BFS to nearest target (**current**) |
| v6 | Aggressive | Predict other snakes' next head positions and cut them off |

---

## Integration points

- `game.py` instantiates one shared `SnakeAI()` and calls `ai.decide(snake, all_occupied)`
  once per snake per game tick (inside the `SPEED_NORMAL` timer block).
- `all_occupied` is a `set` of `(x, y)` grid cells from all living snakes built
  *before* any snake moves that tick — available for future AI levels to use.
- Each `Snake` exposes `.next_dir`, `.head()`, `.body`, `.alive`, and `.score`.
