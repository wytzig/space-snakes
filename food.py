import pygame
import math
from settings import CELL, NEON_GOLD


def draw_food_orbs(surface, positions, pulse):
    """Draw glowing food orbs at each (gx, gy) position in positions."""
    radius_base = int(CELL * 0.35 + math.sin(pulse) * 2)
    for gx, gy in positions:
        cx = gx * CELL + CELL // 2
        cy = gy * CELL + CELL // 2
        r = radius_base
        for draw_r, alpha in [(r + 8, 25), (r + 4, 55), (r, 200)]:
            glow_surf = pygame.Surface((draw_r * 2, draw_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*NEON_GOLD, alpha), (draw_r, draw_r), draw_r)
            surface.blit(glow_surf, (cx - draw_r, cy - draw_r))
        pygame.draw.circle(surface, (255, 255, 180), (cx, cy), max(2, r - 3))


