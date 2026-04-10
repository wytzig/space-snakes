# Code Review — Space Snakes Multiplayer + GitHub Pages

**Scope:** Full multiplayer feature + Pygbag/WASM deployment  
**Date:** 2026-04-10  
**Previous review:** same file — items marked FIXED or CARRIED

---

## Fixed Since Last Review

| # | Was | Now |
|---|-----|-----|
| 1 | `SnakeLogic.grow()` missing — server crash on food eat | Fixed: method added at `game_logic.py:49` |
| 2 | `websockets` unusable in WASM | Fixed: dual emscripten/desktop path in `client_net.py` |
| 3 | `pip3` installs to Python 3.7 | Documented in CLAUDE.md |
| 4 | `ws://` mixed-content warning | Documented in CLAUDE.md |
| 5 | `Snake` / `Food` classes dead code | Removed |
| 6 | Direction constants duplicated | Moved to `settings.py`; `game_logic.py` now imports from there |
| 7 | `main.py` raw string `"menu"` | Fixed: uses `STATE_MENU` |
| 8 | `asyncio.get_event_loop()` deprecated | Fixed: uses `get_running_loop()` |
| 9 | Grid surface allocated every frame | Fixed: cached in `HUD.__init__` |
| 10 | Dead snakes rendered identically to alive | Fixed: `alive == false` snakes are skipped |

---

## Critical Bugs

### 1. `settings.py:69` — `os.environ` is always empty in Pygbag WASM

```python
import os as _os
WS_URL = _os.environ.get("SPACE_SNAKES_WS_URL", "ws://localhost:8765")
```

This is the documented mechanism for setting the server URL on GitHub Pages, but it **does not work** in Pygbag. Pygbag compiles Python to WASM via Pyodide, and Pyodide's `os.environ` is an empty dict — there is no OS environment in a browser context. The env var will never be set, so `WS_URL` is always `"ws://localhost:8765"` in every WASM build. The GitHub Pages build will ship with the wrong URL.

**Fix:** Read the URL from the browser's location or query string at runtime, not from the environment:

```python
# settings.py — evaluated at import time inside WASM
import sys as _sys
if _sys.platform == "emscripten":
    import js as _js
    import urllib.parse as _up
    _qs = _up.parse_qs(_js.window.location.search.lstrip("?"))
    WS_URL = _qs.get("ws", ["wss://your-server.onrender.com"])[0]
else:
    import os as _os
    WS_URL = _os.environ.get("SPACE_SNAKES_WS_URL", "ws://localhost:8765")
```

Or simpler: hardcode the production URL for WASM and let the env var override for desktop only. Either way, the current code will always point to localhost in the browser.

---

## Deployment Blockers

### 2. No GitHub Pages CI/CD pipeline

There is no `.github/workflows/` directory and no `gh-pages` branch. The Pygbag build step (`python3 -m pygbag --build main.py`) has never been run, and nothing publishes `build/web/` to GitHub Pages. The feature is fully implemented but cannot actually be deployed as-is.

Minimum required: a `.github/workflows/deploy.yml` that runs `pygbag --build` and pushes the output to the `gh-pages` branch.

---

## Bugs

### 3. `client_net.py:87–88` — JS callbacks may be garbage-collected

```python
ws.onmessage = _on_message
ws.onclose = _on_close
```

In Pyodide (which Pygbag uses as its WASM runtime), Python functions assigned to JS properties need to be wrapped with `pyodide.ffi.create_proxy()` to prevent the Python garbage collector from freeing them while JS still holds a live reference. Without this the callback silently stops firing after a GC cycle, causing the client to stop receiving state updates mid-session.

```python
from pyodide.ffi import create_proxy
ws.onmessage = create_proxy(_on_message)
ws.onclose = create_proxy(_on_close)
```

### 4. `client_net.py:50–56` — `send_direction` builds an unused JSON string on desktop path

```python
def send_direction(self, direction):
    msg = json.dumps({"type": "input", "dir": direction})   # built unconditionally
    if sys.platform == "emscripten":
        if self._ws and self._connected:
            self._ws.send(msg)                              # used here
    else:
        if self._send_queue is not None:
            self._send_queue.put_nowait({"type": "input", "dir": direction})  # re-built as dict
```

On the desktop path `msg` is serialized to JSON but thrown away — the queue receives a freshly constructed dict instead. Move `json.dumps` inside the emscripten branch.

### 5. `settings.py:57–69` — `import os` at the bottom of the file

```python
# --- Multiplayer server ---
import os as _os
WS_URL = _os.environ.get(...)
```

Imports belong at the top of the file. The `_os` private alias is unnecessary — `settings.py` is not star-imported anywhere, so `os` in the module namespace is harmless. This is a style issue that will confuse anyone reading the file top-to-bottom.

---

## Carried / Still Unfixed (Low Severity)

### 6. `server.py:17` — `_next_id` grows forever

Module-level integer that increments on every connection. After many join/leave cycles the HUD shows "P101" etc. Skin cycling via `pid % 3` still works, but the label is misleading. Use `pid % 3` in the display string, or recycle IDs from a freed pool.

### 7. `server.py` — no session reset when all players leave

When all players disconnect, `session.snakes` becomes empty but food remains from the previous round. New players join a stale session with no way to start fresh.

### 8. `game_logic.py:113` — spawn slot reuse after out-of-order disconnects

```python
idx = len(self.snakes)
sx, sy = SPAWN_POSITIONS[idx % MAX_PLAYERS]
```

If player 0 disconnects and a new player joins while player 1 is still in the session, `len(self.snakes) == 1` assigns spawn index 1 (correct), but if player 1 then disconnects and another joins, the same index is reused. Under repeated churn two snakes can spawn at the same position.

### 9. `multiplayer.md` — stale protocol description

Still describes `{ "type": "join", "name": "Player1" }` and a lobby phase that was never built. Should reflect the actual protocol or be removed.

---

## Summary Table

| # | File | Severity | Issue |
|---|------|----------|-------|
| 1 | settings.py:69 | **Critical** | `os.environ` always empty in WASM — WS_URL is always localhost in browser builds |
| 2 | (missing) | **Blocker** | No `.github/workflows/` pipeline — GitHub Pages deploy is not wired up |
| 3 | client_net.py:87 | High | JS callbacks not wrapped in `create_proxy()` — GC will silently drop them |
| 4 | client_net.py:50 | Low | `json.dumps` called but discarded on desktop path |
| 5 | settings.py:57 | Low | `import os` at bottom of file; unconventional style |
| 6 | server.py:17 | Low | `_next_id` never resets; HUD shows "P101" after reconnects |
| 7 | server.py:16 | Low | No session reset when all players disconnect |
| 8 | game_logic.py:113 | Low | Spawn slot collision after out-of-order disconnects |
| 9 | multiplayer.md | Low | Stale protocol description |
