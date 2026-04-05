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
SPEED_FAST   = 4

# --- Colors ---
BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
NEON_GREEN = (0,   255, 80)
NEON_CYAN  = (0,   240, 255)
NEON_PINK  = (255, 0,   180)
NEON_GOLD  = (255, 220, 0)
DIM_PURPLE = (20,  0,   40)
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
    "deep_space": {"star_count": 200, "nebula": False, "bg_color": (2, 0, 10)},
    "nebula":     {"star_count": 150, "nebula": True,  "bg_color": (5, 0, 20)},
}

DEFAULT_BG = "deep_space"

# --- Game states ---
STATE_MENU      = "menu"
STATE_PLAYING   = "playing"
STATE_PAUSED    = "paused"
STATE_GAMEOVER  = "gameover"
STATE_SETTINGS  = "settings"

# --- Spectator / AI battle ---
NUM_SNAKES = 6          # starting snake count; one skin per snake (wraps if > 8)
RESPAWN_INTERVAL  = 25  # snake-move ticks between respawn checks (~3 s at default speed)
RESPAWN_THRESHOLD = 5   # spawn new snakes when alive count drops below this
RESPAWN_AMOUNT    = 2   # how many snakes to spawn each respawn event

AI_SKINS = [
    {"head": (0,   255,  80),  "body": (0,   180,  50),  "glow": (0,   255,  80)},  # green
    {"head": (0,   240, 255),  "body": (0,   160, 200),  "glow": (0,   240, 255)},  # cyan
    {"head": (255,   0, 180),  "body": (180,   0, 120),  "glow": (255,   0, 180)},  # pink
    {"head": (255, 140,   0),  "body": (200,  90,   0),  "glow": (255, 140,   0)},  # orange
    {"head": (160,   0, 255),  "body": (110,   0, 200),  "glow": (160,   0, 255)},  # purple
    {"head": (255, 255,   0),  "body": (200, 200,   0),  "glow": (255, 255,   0)},  # yellow
    {"head": (255,  50,  50),  "body": (200,  20,  20),  "glow": (255,  50,  50)},  # red
    {"head": (0,   255, 180),  "body": (0,   200, 130),  "glow": (0,   255, 180)},  # teal
]
