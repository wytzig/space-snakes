import pygame
from settings import CELL

# Pre-allocated glow surfaces — CELL is a constant so sizes never change.
# Reused every frame; cleared with fill((0,0,0,0)) before each draw to avoid
# accumulating stale pixels.  Keyed by radius so lookup is O(1).
_glow_cache: dict = {}


def _glow_surf(radius: int) -> pygame.Surface:
    if radius not in _glow_cache:
        _glow_cache[radius] = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    return _glow_cache[radius]


def draw_snake_body(surface, body, skin):
    """Draw a snake given its body (list of (gx,gy) cells) and skin dict."""
    glow = skin["glow"]
    for i, (gx, gy) in enumerate(body):
        rect = pygame.Rect(gx * CELL, gy * CELL, CELL, CELL)
        color = skin["head"] if i == 0 else skin["body"]

        for radius in (CELL + 6, CELL + 3):
            surf = _glow_surf(radius)
            surf.fill((0, 0, 0, 0))
            alpha = 30 if radius == CELL + 6 else 60
            pygame.draw.rect(
                surf, (*glow, alpha),
                pygame.Rect(radius - CELL // 2, radius - CELL // 2, CELL, CELL),
                border_radius=4,
            )
            surface.blit(surf, (gx * CELL - (radius - CELL // 2), gy * CELL - (radius - CELL // 2)))

        pygame.draw.rect(surface, color, rect.inflate(-4, -4), border_radius=4)
        highlight = rect.inflate(-10, -10)
        if highlight.width > 0 and highlight.height > 0:
            bright = tuple(min(255, c + 80) for c in color)
            pygame.draw.rect(surface, bright, highlight, border_radius=2)


