import pygame

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

# --- Game states ---
STATE_MENU      = "menu"
STATE_PLAYING   = "playing"
STATE_PAUSED    = "paused"
STATE_GAMEOVER  = "gameover"

