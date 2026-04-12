import pygame
import random
import math
from settings import (
    SCREEN_W, SCREEN_H, CELL,
    NEON_GREEN,
    WHITE, STAR_DIM, STAR_BRIGHT,
    BACKGROUNDS, DEFAULT_BG,
    SKINS, PLAYER_SKINS,
)


class Starfield:
    def __init__(self, theme_name=DEFAULT_BG):
        cfg = BACKGROUNDS[theme_name]
        self.bg_color = cfg["bg_color"]
        self.stars = [
            {
                "x": random.randint(0, SCREEN_W),
                "y": random.randint(0, SCREEN_H),
                "speed": random.uniform(0.1, 0.5),
                "size":  random.choice([1, 1, 1, 2]),
                "color": random.choice([STAR_DIM, STAR_DIM, STAR_BRIGHT]),
            }
            for _ in range(cfg["star_count"])
        ]

    def update(self):
        for s in self.stars:
            s["y"] += s["speed"]
            if s["y"] > SCREEN_H:
                s["y"] = 0
                s["x"] = random.randint(0, SCREEN_W)

    def draw(self, surface):
        surface.fill(self.bg_color)
        for s in self.stars:
            pygame.draw.circle(surface, s["color"], (int(s["x"]), int(s["y"])), s["size"])


class HUD:
    def __init__(self, font_large, font_small):
        self.font_large = font_large
        self.font_small = font_small
        self._grid_surf = self._build_grid()

    @staticmethod
    def _build_grid():
        line_color = (255, 255, 255, 8)
        surf = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        for x in range(0, SCREEN_W, CELL):
            pygame.draw.line(surf, line_color, (x, 0), (x, SCREEN_H))
        for y in range(0, SCREEN_H, CELL):
            pygame.draw.line(surf, line_color, (0, y), (SCREEN_W, y))
        return surf

    def draw_scores(self, surface, scores, my_player_id):
        """Draw one score line per player, coloured by their snake skin."""
        y = 8
        for pid, score in scores:
            skin_name = PLAYER_SKINS[pid % len(PLAYER_SKINS)]
            color = SKINS[skin_name]["head"]
            marker = ">" if pid == my_player_id else " "
            text = self.font_small.render(f"{marker}P{pid + 1}  {score:05d}", True, color)
            surface.blit(text, (12, y))
            y += text.get_height() + 4

    def draw_menu(self, surface, tick):
        # Title
        title = self.font_large.render("SPACE SNAKES", True, NEON_GREEN)
        tx = SCREEN_W // 2 - title.get_width() // 2
        surface.blit(title, (tx, SCREEN_H // 3))

        # Pulsing prompt
        alpha = int(128 + 127 * math.sin(tick * 0.05))
        prompt = self.font_small.render("PRESS ENTER TO START", True, WHITE)
        prompt.set_alpha(alpha)
        px = SCREEN_W // 2 - prompt.get_width() // 2
        surface.blit(prompt, (px, SCREEN_H // 2 + 40))

        sub = self.font_small.render("ESC quit   F fullscreen   M mute", True, STAR_DIM)
        surface.blit(sub, (SCREEN_W // 2 - sub.get_width() // 2, SCREEN_H // 2 + 90))

    def draw_grid(self, surface):
        surface.blit(self._grid_surf, (0, 0))

    def draw_mute_button(self, surface, muted):
        """Draw a mute toggle button in the top-right corner. Returns the button Rect."""
        label = "M:OFF" if muted else "M:ON"
        color = STAR_DIM if muted else NEON_GREEN
        text = self.font_small.render(label, True, color)
        pad = 6
        w = text.get_width() + pad * 2
        h = text.get_height() + pad * 2
        rect = pygame.Rect(SCREEN_W - w - 8, 8, w, h)
        pygame.draw.rect(surface, (20, 20, 40), rect, border_radius=4)
        pygame.draw.rect(surface, color, rect, width=1, border_radius=4)
        surface.blit(text, (rect.x + pad, rect.y + pad))
        return rect
