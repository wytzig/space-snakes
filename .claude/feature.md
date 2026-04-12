# Feature: Code-Review Fixes (batch)

## Already resolved in working tree (no action needed)
- #1 recv/send bare except — exc logged at lines 156, 167
- #3 per-frame Surface alloc — _glow_cache in snake.py + food.py
- #5 double json.dumps — comment added at client_net.py:54
- #8 respawn determinism — fallback loop collects all candidates, no break

## To implement

| # | File | Fix |
|---|------|-----|
| 2 | game.py:117 | Set `_mute_btn_rect = None` before early return when state is None |
| 4 | renderer.py:6 | Remove unused `NEON_PINK` from import |
| 6 | docs/README.md | Mark music done; add M key to controls table |
| 7 | renderer.py:81 | Append `M mute` to menu hint string |
