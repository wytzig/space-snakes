# Code Review — Space Snakes

**Scope:** Full codebase  
**Date:** 2026-04-10

---

## Fixed Since Last Review

All 9 previously reported issues are closed:

| # | Was | Now |
|---|-----|-----|
| 1 | `os.environ` always empty in WASM — WS_URL always localhost in browser | Fixed: emscripten path reads URL from query string (`settings.py:76–80`) |
| 2 | No `.github/workflows/` pipeline | Fixed: `.github/workflows/deploy.yml` exists and wires up Pygbag build + Pages deploy |
| 3 | JS callbacks not wrapped in `create_proxy()` — GC silently drops them | Fixed: browser path is now pure JS; no Python callbacks cross the FFI boundary |
| 4 | `json.dumps` called but discarded on desktop `send_direction` path | Fixed: desktop path passes a dict directly to the queue |
| 5 | `import os` at bottom of `settings.py` | Fixed: both `import sys` and `import os` are now at the top |
| 6 | `_next_id` counter never reset — HUD showed "P101" after reconnects | Fixed: `add_player()` uses lowest-free-slot allocation; no monotonic counter |
| 7 | No session reset when all players disconnect | Fixed: `server.py:68–70` calls `session.reset()` in the `finally` block when lobby empties |
| 8 | Spawn slot collision after out-of-order disconnects | Fixed: `add_player()` scans `range(MAX_PLAYERS)` for the first free slot |
| 9 | `multiplayer.md` described a lobby/join phase that was never built | Fixed: protocol section now matches the implementation |

---

## Bugs

### 1. `client_net.py:131–136` — bare `except Exception: pass` swallows all errors in `_recv_loop`

```python
async def _recv_loop(self):
    try:
        async for raw in self._ws:
            self._process_message(raw)
    except Exception:
        self._connected = False
```

Any exception — including `AttributeError`, `TypeError`, or a bug in `_process_message` — silently sets `_connected = False` and exits. The player sees the game drop back to the menu with no indication of what went wrong. At minimum, log the exception. The same pattern appears in `_send_loop` (lines 138–147).

**Fix:**
```python
except Exception as exc:
    print(f"[recv_loop] disconnected: {exc}")
    self._connected = False
```

### 2. `client_net.py:54` — double `json.dumps` with no explanation

```python
payload = json.dumps(json.dumps({"type": "input", "dir": direction}))
js.eval(f"window._ss_ws && window._ss_ws.send({payload})")
```

The inner `json.dumps` produces a JSON string (`'{"type":"input","dir":"UP"}'`). The outer `json.dumps` wraps that string in JS-safe quotes so it can be dropped into `js.eval()` as a string literal. This is correct, but the double call looks like a bug to any future reader and will be "fixed" into an actual bug. Add a comment explaining the intent.

---

## Performance

### 3. `snake.py:13` + `food.py:13` — `pygame.Surface` allocated per-segment and per-food every frame

`draw_snake_body` allocates 2 new `Surface` objects per body segment on every call:

```python
for radius in (CELL + 6, CELL + 3):
    glow_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
```

`draw_food_orbs` allocates 3 surfaces per food item per frame. At 60 FPS with three snakes of length ~15 each, that's roughly 5,400 surface allocations per second, all of which immediately become garbage. This drives GC pressure and is the dominant frame-time cost.

**Fix:** Pre-allocate the glow surfaces once (they are all the same fixed size — `CELL` is a constant) and reuse them by clearing with `fill((0,0,0,0))` before each draw.

---

## Documentation / Dead Code

### 4. `snake-ai.md` describes `snake_ai.py` — file does not exist

`snake-ai.md` documents a `SnakeAI` class in `snake_ai.py` with specific integration points in `game.py`, but `snake_ai.py` does not exist in the repository and `game.py` has no import or call to it. The document is either describing a removed feature or an unimplemented one.

Either delete `snake-ai.md` or add a clear "Planned / not yet implemented" header so it isn't mistaken for documentation of working code.

### 5. `multiplayer.md` — "Open Questions" section is legacy planning debt

The bottom section lists questions ("Max players?", "What happens when a snake dies?", "Name entry?", "Room codes?") that have all been answered and implemented. New contributors reading this doc will be confused about whether these are still open decisions.

Delete the "Open Questions" and "New Files Required" sections — both are pre-implementation artefacts that no longer reflect reality.

---

## Low Severity

### 6. `game_logic.py:55–67` — respawn fallback is deterministic, not random

When no standard spawn positions are clear, `respawn()` scans the grid top-to-bottom and picks the *first* valid cell:

```python
for y in range(2, ROWS - 2):
    for x in range(2, COLS - 3):
        if all((x - i, y) in empty_cells for i in range(3)):
            candidates.append((x, y))
            break   # exits inner loop
    if candidates:
        break       # exits outer loop
```

Multiple dead snakes respawning in the same tick will all land at the same top-left cell (the grid is so full that only one spot is found, and both snakes pick it). This causes an immediate head-on collision on the next tick. Collect *all* fallback candidates (or at least several) before calling `random.choice`.

---

## Summary Table

| # | File | Severity | Issue |
|---|------|----------|-------|
| 1 | client_net.py:131–147 | Medium | Silent bare `except` in recv/send loops — errors invisible to dev and user |
| 2 | client_net.py:54 | Medium | Double `json.dumps` unexplained — looks like a bug, will be "fixed" into one |
| 3 | snake.py:13, food.py:13 | Medium | Per-frame `Surface` allocation per segment/food — dominant GC pressure at 60 FPS |
| 4 | snake-ai.md | Low | Documents `snake_ai.py` which does not exist |
| 5 | multiplayer.md | Low | "Open Questions" section is stale pre-implementation planning |
| 6 | game_logic.py:55–67 | Low | Respawn fallback is deterministic — crowded-grid snakes all land on same cell |
