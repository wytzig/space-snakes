import pygame
import random
import math
from settings import CELL, COLS, ROWS, NEON_GOLD


class Food:
    def __init__(self):
        self.pos = (0, 0)
        self.pulse = 0.0
        self.spawn([])

    def spawn(self, snake_body):
        while True:
            pos = (random.randint(0, COLS - 1), random.randint(0, ROWS - 1))
            if pos not in snake_body:
                self.pos = pos
                break

    def update(self):
        self.pulse = (self.pulse + 0.08) % (2 * math.pi)

    def draw(self, surface):
        gx, gy = self.pos
        cx = gx * CELL + CELL // 2
        cy = gy * CELL + CELL // 2
        radius = int(CELL * 0.35 + math.sin(self.pulse) * 2)

        for r, alpha in [(radius + 8, 25), (radius + 4, 55), (radius, 200)]:
            glow_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*NEON_GOLD, alpha), (r, r), r)
            surface.blit(glow_surf, (cx - r, cy - r))

        # Bright core
        pygame.draw.circle(surface, (255, 255, 180), (cx, cy), max(2, radius - 3))
