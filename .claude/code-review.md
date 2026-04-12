<!-- last-reviewed: 3dfcc3ffd3bb7db180c68ca44f4b34d5393cb8aa -->
# Code Review — Space Snakes

**Scope:** All previously open issues resolved in working tree  
**Date:** 2026-04-12

---

## Open Issues

_None._

---

## Recently Closed (this session)

| # | Issue | Resolution |
|---|-------|------------|
| 1 | `client_net.py` bare `except` in recv/send loops | `exc` now logged via `print()` at lines 156, 167 |
| 2 | `game.py` stale `_mute_btn_rect` on early return | `_mute_btn_rect = None` set before return when state is None |
| 3 | `snake.py`/`food.py` per-frame Surface allocation | `_glow_cache` dict pre-allocates and reuses surfaces |
| 4 | `renderer.py` orphaned `NEON_PINK` import | Removed from import list |
| 5 | `client_net.py:54` double `json.dumps` unexplained | Inline comment explains inner/outer intent |
| 6 | `docs/README.md` music feature unchecked, M key absent | Feature checked; M row added to controls table |
| 7 | Menu hint text missing M keybinding | Updated to `"ESC quit   F fullscreen   M mute"` |
| 8 | `game_logic.py` respawn fallback deterministic | Fallback collects all candidates; `random.choice` picks from full set |
