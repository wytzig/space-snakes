import pygame
from settings import CELL, COLS, ROWS, SKINS, DEFAULT_SKIN

UP    = (0, -1)
DOWN  = (0,  1)
LEFT  = (-1, 0)
RIGHT = (1,  0)

OPPOSITES = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}


class Snake:
    def __init__(self, skin_name=DEFAULT_SKIN):
        cx, cy = COLS // 2, ROWS // 2
        self.body = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.direction = RIGHT
        self.next_dir  = RIGHT
        self.grow_pending = 0
        self.alive = True
        self.skin = SKINS[skin_name]

    # --- Input ---
    def set_direction(self, new_dir):
        if new_dir != OPPOSITES.get(self.direction):
            self.next_dir = new_dir

    # --- Update ---
    def move(self):
        self.direction = self.next_dir
        hx, hy = self.body[0]
        dx, dy = self.direction
        new_head = (hx + dx, hy + dy)

        # Wall collision
        if not (0 <= new_head[0] < COLS and 0 <= new_head[1] < ROWS):
            self.alive = False
            return

        # Self collision
        if new_head in self.body:
            self.alive = False
            return

        self.body.insert(0, new_head)
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()

    def grow(self, amount=1):
        self.grow_pending += amount

    def head(self):
        return self.body[0]

    # --- Render ---
    def draw(self, surface):
        for i, (gx, gy) in enumerate(self.body):
            rect = pygame.Rect(gx * CELL, gy * CELL, CELL, CELL)
            is_head = (i == 0)
            color = self.skin["head"] if is_head else self.skin["body"]
            glow  = self.skin["glow"]

            # Glow layers (outer to inner)
            for radius in (CELL + 6, CELL + 3):
                glow_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                alpha = 30 if radius == CELL + 6 else 60
                pygame.draw.rect(
                    glow_surf, (*glow, alpha),
                    pygame.Rect(radius - CELL // 2, radius - CELL // 2, CELL, CELL),
                    border_radius=4
                )
                surface.blit(glow_surf, (gx * CELL - (radius - CELL // 2), gy * CELL - (radius - CELL // 2)))

            # Solid body segment
            pygame.draw.rect(surface, color, rect.inflate(-4, -4), border_radius=4)

            # Bright center highlight
            highlight = rect.inflate(-10, -10)
            if highlight.width > 0 and highlight.height > 0:
                bright = tuple(min(255, c + 80) for c in color)
                pygame.draw.rect(surface, bright, highlight, border_radius=2)
