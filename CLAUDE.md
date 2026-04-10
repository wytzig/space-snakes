# Space Snakes — Claude Development Tracker

## Project Overview
A 16-bit retro-style snake game with neon laser aesthetics, set in space. Built with Python + Pygame.

---

## Feature Status

| Feature | Status | Notes |
|---|---|---|
| Game loop / window init | Done | 60fps, fullscreen toggle |
| Snake movement + input | Done | WASD + arrow keys |
| Food / pellet spawning | Done | Glowing orb style |
| Collision detection | Done | Wall + self |
| Score display | Done | Retro pixel font |
| Neon laser snake skin | Done | Glow shader via surface layering |
| Starfield background | Done | Parallax scrolling stars |
| Main menu screen | Done | Title + start/quit |
| Game over screen | Done | Score + restart prompt |
| Sound effects | Planned | eat, death, boost |
| Background music | Planned | Chiptune / synthwave loop |
| Settings screen | Planned | Background themes, snake color, speed |
| Multiple snake skins | Planned | Different neon colors/patterns |
| Power-ups | Planned | Speed boost, shield, multi-food |
| High score persistence | Planned | JSON save file |
| Particle effects | Planned | Death explosion, eat burst |
| Background themes | Planned | Deep space, nebula, asteroid field |
| Multiplayer (online) | Done | Up to 3 players via WebSocket; death->food+respawn; per-player neon colors |

---

## Architecture

```
space-snakes/
├── main.py                  # Async entry point (Pygbag-compatible)
├── game.py                  # Multiplayer client: connects to server, renders state
├── game_logic.py            # Server-side pure-Python game logic (no pygame)
├── server.py                # Asyncio WebSocket server (run separately or deploy to Render)
├── client_net.py            # WebSocket client wrapper used by game.py
├── snake.py                 # draw_snake_body() + Snake class (rendering)
├── food.py                  # draw_food_orbs() + Food class (rendering)
├── renderer.py              # Starfield, HUD (scores, menu, grid)
├── settings.py              # Constants and config (colors, speeds, WS_URL)
├── requirements_server.txt  # websockets package for server deployment
├── assets/
│   ├── fonts/           # Pixel fonts (.ttf)
│   ├── sounds/          # SFX and music (.ogg / .wav)
│   └── images/          # Any static sprites
├── CLAUDE.md            # This file
└── README.md            # User-facing docs
```

### Key Design Decisions
- **Glow effect**: Rendered by drawing multiple blurred/alpha-scaled copies of the snake body at increasing sizes, then compositing.
- **Snake body**: List of (x, y) grid cells. Head is `body[0]`. Each tick, prepend new head and pop tail (unless growing).
- **Grid vs pixel**: Internal logic uses grid cells; renderer scales to pixel coords.
- **Game states**: `MENU → PLAYING`

---

## Recurring Issues / Known Gotchas

- **pygame install on WSL**: `pip3 install pygame` tries to compile from source and fails without SDL dev libs. Use `sudo apt install python3-pygame` instead — it's pre-built and just works.
- **websockets install**: `/usr/bin/pip3` on this machine is tied to Python 3.7, but `python3` resolves to 3.10. Always use `python3 -m pip install websockets` so the package lands in the running interpreter, not 3.7.
- **WS_URL for production**: `settings.py` defaults to `ws://localhost:8765`. Before building with Pygbag for GitHub Pages, set env var `SPACE_SNAKES_WS_URL=wss://your-server.onrender.com` (must be `wss://` — browsers block `ws://` from HTTPS pages).
- **Always use `python3` / `pip3`**: The system `python` on this WSL install is Python 2.7. All code is Python 3. Running with `python` will fail immediately.
- **Non-ASCII in source files**: Python 2 chokes on any unicode in source without an encoding declaration. Avoid all non-ASCII in comments/strings (arrows, em-dashes, etc.) to keep the files safe even if someone runs the wrong interpreter.
- **Pygame font rendering on WSL**: May need to install fonts via `sudo apt install fonts-dejavu` if custom .ttf missing.
- **Glow performance**: Drawing many alpha surfaces per frame is expensive. If FPS drops, reduce glow layers or use `pygame.transform.smoothscale` less aggressively.
- **Grid alignment**: Always floor-divide pixel coords when converting back to grid. Off-by-one errors common at edges.
- **Event loop**: Always drain the event queue fully each frame — missing `pygame.QUIT` causes the window to freeze on close.
- **WSL display**: Requires a running X server (e.g. VcXsrv, Xming, or WSLg). Set `DISPLAY=:0` if not auto-detected.
