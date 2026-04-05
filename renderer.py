import pygame
import random
import math
from settings import (
    SCREEN_W, SCREEN_H, CELL, COLS, ROWS,
    NEON_GREEN, NEON_CYAN, NEON_PINK, NEON_GOLD,
    WHITE, BLACK, DIM_PURPLE, STAR_DIM, STAR_BRIGHT,
    BACKGROUNDS, DEFAULT_BG,
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

    def draw_score(self, surface, score):
        text = self.font_small.render(f"SCORE  {score:05d}", True, NEON_CYAN)
        surface.blit(text, (12, 8))

    def draw_menu(self, surface, tick):
        # Title
        title = self.font_large.render("SPACE SNAKES", True, NEON_GREEN)
        tx = SCREEN_W // 2 - title.get_width() // 2
        surface.blit(title, (tx, SCREEN_H // 3))

        # Glow behind title
        glow = self.font_large.render("SPACE SNAKES", True, (*NEON_GREEN[:2], 30))

        # Pulsing prompt
        alpha = int(128 + 127 * math.sin(tick * 0.05))
        prompt = self.font_small.render("PRESS ENTER TO START", True, WHITE)
        prompt.set_alpha(alpha)
        px = SCREEN_W // 2 - prompt.get_width() // 2
        surface.blit(prompt, (px, SCREEN_H // 2 + 40))

        sub = self.font_small.render("ESC to quit   F fullscreen", True, STAR_DIM)
        surface.blit(sub, (SCREEN_W // 2 - sub.get_width() // 2, SCREEN_H // 2 + 90))

    def draw_gameover(self, surface, score, tick, winner_color=None):
        over = self.font_large.render("GAME OVER", True, NEON_PINK)
        surface.blit(over, (SCREEN_W // 2 - over.get_width() // 2, SCREEN_H // 3))

        score_color = winner_color if winner_color else NEON_GOLD
        sc = self.font_small.render(f"WINNER  {score:05d}", True, score_color)
        surface.blit(sc, (SCREEN_W // 2 - sc.get_width() // 2, SCREEN_H // 3 + 70))

        alpha = int(128 + 127 * math.sin(tick * 0.05))
        restart = self.font_small.render("R to restart   ESC for menu", True, WHITE)
        restart.set_alpha(alpha)
        surface.blit(restart, (SCREEN_W // 2 - restart.get_width() // 2, SCREEN_H // 2 + 60))

    def draw_scoreboard(self, surface, snakes):
        """Right-side scoreboard showing each snake's color swatch and score."""
        swatch = 14
        row_h  = 26
        x      = SCREEN_W - 170
        y      = 10
        for i, snake in enumerate(snakes):
            color = snake.skin["head"] if snake.alive else (55, 55, 55)
            pygame.draw.rect(surface, color, pygame.Rect(x, y + i * row_h + 3, swatch, swatch))
            label = f"S{i + 1}  {snake.score:05d}"
            txt = self.font_small.render(label, True, color)
            surface.blit(txt, (x + swatch + 6, y + i * row_h))

    def draw_pause(self, surface):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        surface.blit(overlay, (0, 0))
        txt = self.font_large.render("PAUSED", True, NEON_CYAN)
        surface.blit(txt, (SCREEN_W // 2 - txt.get_width() // 2, SCREEN_H // 2 - 40))

    def draw_corpses(self, surface, corpse_pellets):
        """Draw each dead-snake body cell as a small dim coloured dot."""
        for (gx, gy), color in corpse_pellets.items():
            cx = gx * CELL + CELL // 2
            cy = gy * CELL + CELL // 2
            r = max(2, CELL // 5)
            glow_surf = pygame.Surface((r * 2 + 6, r * 2 + 6), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*color, 40), (r + 3, r + 3), r + 3)
            pygame.draw.circle(glow_surf, (*color, 130), (r + 3, r + 3), r)
            surface.blit(glow_surf, (cx - r - 3, cy - r - 3))

    def draw_grid(self, surface):
        """Subtle grid lines for the playing field."""
        line_color = (255, 255, 255, 8)
        grid_surf = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        for x in range(0, SCREEN_W, CELL):
            pygame.draw.line(grid_surf, line_color, (x, 0), (x, SCREEN_H))
        for y in range(0, SCREEN_H, CELL):
            pygame.draw.line(grid_surf, line_color, (0, y), (SCREEN_W, y))
        surface.blit(grid_surf, (0, 0))
