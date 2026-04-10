import pygame
import math
from settings import CELL, NEON_GOLD

# Pre-allocated glow surfaces keyed by radius.  The pulse animation produces
# a small fixed set of radii each session; caching eliminates per-frame
# Surface allocation (previously ~3 allocs per food item per frame at 60 FPS).
_glow_cache: dict = {}


def _glow_surf(radius: int) -> pygame.Surface:
    if radius not in _glow_cache:
        _glow_cache[radius] = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    return _glow_cache[radius]


def draw_food_orbs(surface, positions, pulse):
    """Draw glowing food orbs at each (gx, gy) position in positions."""
    radius_base = int(CELL * 0.35 + math.sin(pulse) * 2)
    for gx, gy in positions:
        cx = gx * CELL + CELL // 2
        cy = gy * CELL + CELL // 2
        r = radius_base
        for draw_r, alpha in [(r + 8, 25), (r + 4, 55), (r, 200)]:
            surf = _glow_surf(draw_r)
            surf.fill((0, 0, 0, 0))
            pygame.draw.circle(surf, (*NEON_GOLD, alpha), (draw_r, draw_r), draw_r)
            surface.blit(surf, (cx - draw_r, cy - draw_r))
        pygame.draw.circle(surface, (255, 255, 180), (cx, cy), max(2, r - 3))


