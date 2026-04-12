# Multiplayer Planning — Space Snakes

## The Core Constraint

GitHub Pages serves **static files only** (HTML, CSS, JS, WASM). It cannot run Python, open sockets, or maintain any server-side state. This forces two decisions:

1. The game client must run **in a browser**.
2. Real-time player sync requires an **external service** (there is no way around this for multiplayer).

---

## Why the Current Stack Doesn't Port Directly

Pygame is a desktop library that wraps SDL2. Browsers have no SDL2. Two paths exist to make Python/Pygame run in a browser:

- **Pygbag** — compiles Python + Pygame to WebAssembly (WASM). The game runs client-side in the browser with no rewrite. Network calls must use async WebSockets (not the standard `socket` module).
- **Rewrite in JavaScript** — full rewrite using the Canvas API or a library like Phaser.js. Browsers are the native target, so no WASM layer needed.

---

## Option Comparison

| | Option A: Pygbag + WS Server | Option B: JS Rewrite + Firebase |
|---|---|---|
| Codebase | Keep Python | Full JS rewrite |
| Runs on GitHub Pages | Yes (WASM bundle) | Yes |
| Multiplayer backend | WebSocket server (needs hosting) | Firebase Realtime DB (serverless) |
| Extra hosting needed | Yes — Render / Railway / Fly.io (free tier available) | No (Firebase free tier) |
| Complexity | Medium — async networking in Pygame is awkward | Medium — rewrite cost upfront |
| Performance | Good (WASM) | Good (native browser) |
| Long-term maintainability | Pygbag is a niche tool; quirks exist | Standard web stack |

---

## Recommended Path: Option A (Pygbag + WebSocket Server)

**Reason:** Keeps the existing Python game logic intact. The rewrite cost of Option B is high and the game logic would need to be re-implemented from scratch in JS.

**Trade-off accepted:** A small free-tier WebSocket server is needed. Render.com and Railway both offer always-on free tiers that are sufficient for a low-traffic game.

---

## Architecture

```
GitHub Pages                    Render / Railway
+-------------------+           +------------------+
| index.html        |           |                  |
| game.wasm (Pygbag)|  <------> | WS Server        |
| assets/           | WebSocket | (Python asyncio  |
+-------------------+           |  or Node.js)     |
                                +------------------+
```

### Client (Pygbag, runs in browser)
- Builds the existing game into a `.wasm` bundle via `pygbag main.py`
- Replaces blocking network calls with `asyncio` + `websockets`
- Sends player input events to the server each frame
- Receives authoritative game state from the server and renders it

### Server (Python asyncio — new file `server.py`)
- Manages a **lobby**: players connect, server assigns them a color/slot
- Runs the **authoritative game loop** (snake moves, food, collision)
- Broadcasts full game state to all connected clients at a fixed tick rate (~10 Hz)
- Handles join/leave gracefully (snake is removed on disconnect)

### State sync model: **Server-authoritative**
- Clients send only direction inputs (`UP`, `DOWN`, `LEFT`, `RIGHT`)
- Server owns all game state; clients are pure renderers
- Avoids desyncs and makes cheating impossible

---

## Lobby Design

No accounts or passwords — join and play immediately:

1. Player opens the game URL on GitHub Pages and presses Enter
2. Client connects to the WS server (no join message needed — the server assigns a slot)
3. Server sends `{ "type": "joined", "player_id": 0 }` (slot 0, 1, or 2)
4. Server rejects with `{ "type": "error", "msg": "game full" }` if all 3 slots are taken
5. Game loop is already running; the new snake appears in the next broadcast
6. Server ticks every `SPEED_NORMAL / FPS` seconds and pushes full game state

**Client → Server:** `{ "type": "input", "dir": "UP" }` (only direction inputs are sent)

**Server → Client:** `{ "type": "state", "player_id": 0, "snakes": [...], "foods": [...] }`

When all clients disconnect the session resets (scores and food cleared).

---

## Deployment

1. Install Pygbag: `pip3 install pygbag`
2. Build: `python3 -m pygbag --build main.py` → outputs `build/web/`
3. Push to `main` — GitHub Actions handles the Pygbag build and Pages deploy automatically.
4. Deploy `server.py` to Render (free tier, auto-deploys from GitHub via `render.yaml`)
5. `WS_URL` in `settings.py` defaults to the Render URL; override via `?ws=` query param.
