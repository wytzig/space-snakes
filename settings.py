import sys
import os

# --- Window ---
TITLE = "Space Snakes"
SCREEN_W = 960
SCREEN_H = 720
FPS = 60

# --- Grid ---
CELL = 24           # pixels per grid cell
COLS = SCREEN_W // CELL
ROWS = SCREEN_H // CELL

# --- Speeds (ticks between snake moves) ---
SPEED_NORMAL = 8    # move every N frames

# --- Colors ---
WHITE      = (255, 255, 255)
NEON_GREEN = (0,   255, 80)
NEON_CYAN  = (0,   240, 255)
NEON_PINK  = (255, 0,   180)
NEON_GOLD  = (255, 220, 0)
STAR_DIM   = (80,  80,  120)
STAR_BRIGHT= (200, 200, 255)

# --- Snake skin presets ---
SKINS = {
    "laser_green": {
        "head":  NEON_GREEN,
        "body":  (0, 180, 50),
        "glow":  (0, 255, 80),
    },
    "laser_cyan": {
        "head":  NEON_CYAN,
        "body":  (0, 160, 200),
        "glow":  (0, 240, 255),
    },
    "laser_pink": {
        "head":  NEON_PINK,
        "body":  (180, 0, 120),
        "glow":  (255, 0, 180),
    },
}

DEFAULT_SKIN = "laser_green"

# --- Background themes ---
BACKGROUNDS = {
    "deep_space": {"star_count": 200, "bg_color": (2, 0, 10)},
    "nebula":     {"star_count": 150, "bg_color": (5, 0, 20)},
}

DEFAULT_BG = "deep_space"

# --- Player skins (index = player slot 0..2) ---
PLAYER_SKINS = ["laser_green", "laser_cyan", "laser_pink"]

# --- Game states ---
STATE_MENU    = "menu"
STATE_PLAYING = "playing"

# --- Direction vectors (shared by game_logic and client input) ---
UP    = (0, -1)
DOWN  = (0,  1)
LEFT  = (-1, 0)
RIGHT = (1,  0)
OPPOSITES = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}
DIR_MAP = {"UP": UP, "DOWN": DOWN, "LEFT": LEFT, "RIGHT": RIGHT}

# --- Music ---
MUSIC_PATH = os.path.join(os.path.dirname(__file__), "assets", "sounds", "space_snakes.ogg")
MUSIC_VOLUME = 0.7

# --- Multiplayer server ---
# Desktop: override with env var SPACE_SNAKES_WS_URL (must be ws://)
# Browser (Pygbag): os.environ is always empty; URL is read from the query string instead.
#   e.g. https://yourname.github.io/space-snakes/?ws=wss://your-server.onrender.com
#   Must be wss:// — browsers block ws:// connections from HTTPS pages.
_RENDER_URL = "wss://space-snakes-p6tu.onrender.com"  # update if you redeploy to Render

if sys.platform == "emscripten":
    # os.environ is always empty in WASM — read the server URL from the query string.
    # e.g. https://wytzig.github.io/space-snakes/?ws=wss://other-server.onrender.com
    import js as _js
    import urllib.parse as _up
    _qs = _up.parse_qs(_js.window.location.search.lstrip("?"))
    WS_URL = _qs.get("ws", [_RENDER_URL])[0]
else:
    WS_URL = os.environ.get("SPACE_SNAKES_WS_URL", "ws://localhost:8765")

