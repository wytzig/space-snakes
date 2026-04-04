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
| Multiplayer (local) | Planned | Two snakes, split screen or shared |

---

## Architecture

```
space-snakes/
├── main.py              # Entry point, game loop
├── game.py              # Core game state machine
├── snake.py             # Snake entity (movement, growth, rendering)
├── food.py              # Food spawning and rendering
├── renderer.py          # All drawing logic, glow effects
├── settings.py          # Constants and config (colors, speeds, sizes)
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
- **Game states**: `MENU → PLAYING → PAUSED → GAME_OVER → SETTINGS`

---

## Recurring Issues / Known Gotchas

- **pygame install on WSL**: `pip3 install pygame` tries to compile from source and fails without SDL dev libs. Use `sudo apt install python3-pygame` instead — it's pre-built and just works.
- **Always use `python3` / `pip3`**: The system `python` on this WSL install is Python 2.7. All code is Python 3. Running with `python` will fail immediately.
- **Non-ASCII in source files**: Python 2 chokes on any unicode in source without an encoding declaration. Avoid all non-ASCII in comments/strings (arrows, em-dashes, etc.) to keep the files safe even if someone runs the wrong interpreter.
- **Pygame font rendering on WSL**: May need to install fonts via `sudo apt install fonts-dejavu` if custom .ttf missing.
- **Glow performance**: Drawing many alpha surfaces per frame is expensive. If FPS drops, reduce glow layers or use `pygame.transform.smoothscale` less aggressively.
- **Grid alignment**: Always floor-divide pixel coords when converting back to grid. Off-by-one errors common at edges.
- **Event loop**: Always drain the event queue fully each frame — missing `pygame.QUIT` causes the window to freeze on close.
- **WSL display**: Requires a running X server (e.g. VcXsrv, Xming, or WSLg). Set `DISPLAY=:0` if not auto-detected.
