import math
import pygame
from settings import (
    COLS, ROWS, SPEED_NORMAL,
    STATE_MENU, STATE_PLAYING, STATE_PAUSED, STATE_GAMEOVER,
    NUM_SNAKES, AI_SKINS,
)
from snake import Snake
from food import Food
from renderer import Starfield, HUD
from snake_ai import SnakeAI


def _spawn_positions(n):
    """Spread n starting positions evenly in a circle across the grid."""
    positions = []
    for i in range(n):
        angle = (2 * math.pi * i) / n - math.pi / 2  # start at top
        x = int(COLS // 2 + (COLS // 3) * math.cos(angle))
        y = int(ROWS // 2 + (ROWS // 3) * math.sin(angle))
        x = max(3, min(COLS - 4, x))
        y = max(1, min(ROWS - 2, y))
        positions.append((x, y))
    return positions


class Game:
    def __init__(self, screen, fonts):
        self.screen = screen
        self.hud = HUD(*fonts)
        self.starfield = Starfield()
        self.ai = SnakeAI()
        self.state = STATE_MENU
        self.tick = 0
        self._touch_start = None
        self._reset()

    def _reset(self):
        positions = _spawn_positions(NUM_SNAKES)
        self.snakes = [
            Snake(skin=AI_SKINS[i % len(AI_SKINS)], start_pos=positions[i])
            for i in range(NUM_SNAKES)
        ]
        self.food = Food()
        occupied = {pos for s in self.snakes for pos in s.body}
        self.food.spawn(occupied)
        self.move_timer = 0

    # --- Input ---
    def _handle_swipe(self, dx, dy):
        MIN_SWIPE = 0.05
        if abs(dx) < MIN_SWIPE and abs(dy) < MIN_SWIPE:
            return
        if self.state == STATE_MENU:
            self._reset()
            self.state = STATE_PLAYING

    def handle_event(self, event):
        if event.type == pygame.FINGERDOWN:
            self._touch_start = (event.x, event.y)
        elif event.type == pygame.FINGERUP:
            if self._touch_start is not None:
                dx = event.x - self._touch_start[0]
                dy = event.y - self._touch_start[1]
                self._handle_swipe(dx, dy)
                self._touch_start = None

        if event.type == pygame.KEYDOWN:
            k = event.key
            if self.state == STATE_MENU:
                if k == pygame.K_RETURN:
                    self._reset()
                    self.state = STATE_PLAYING
            elif self.state == STATE_PLAYING:
                if k == pygame.K_p:
                    self.state = STATE_PAUSED
            elif self.state == STATE_PAUSED:
                if k == pygame.K_p:
                    self.state = STATE_PLAYING
                if k == pygame.K_ESCAPE:
                    self.state = STATE_MENU
            elif self.state == STATE_GAMEOVER:
                if k == pygame.K_r:
                    self._reset()
                    self.state = STATE_PLAYING
                if k == pygame.K_ESCAPE:
                    self.state = STATE_MENU

    # --- Update ---
    def update(self):
        self.tick += 1
        self.starfield.update()
        self.food.update()

        if self.state != STATE_PLAYING:
            return

        self.move_timer += 1
        if self.move_timer < SPEED_NORMAL:
            return
        self.move_timer = 0

        # All occupied cells = alive AND dead snake bodies (dead bodies are solid obstacles)
        all_occupied = {pos for s in self.snakes for pos in s.body}

        # AI picks a direction for each snake
        for snake in self.snakes:
            if snake.alive:
                new_dir = self.ai.decide(snake, all_occupied, self.food.pos)
                snake.set_direction(new_dir)

        # Move all snakes
        for snake in self.snakes:
            if snake.alive:
                snake.move()

        # Cross-collision: head entered any snake's body (alive or dead)
        for snake in [s for s in self.snakes if s.alive]:
            head = snake.head()
            for other in self.snakes:
                if other is snake:
                    continue
                if head in other.body:
                    snake.alive = False
                    break

        # Food collection (first snake to reach food wins the pellet)
        for snake in [s for s in self.snakes if s.alive]:
            if snake.head() == self.food.pos:
                snake.score += 10
                snake.grow()
                occupied = {pos for s in self.snakes for pos in s.body}
                self.food.spawn(occupied)
                break

        # Respawn food if it ended up inside a dead snake body
        # (e.g. two snakes collided head-on exactly on the food cell)
        all_cells = {pos for s in self.snakes for pos in s.body}
        if self.food.pos in all_cells:
            self.food.spawn(all_cells)

        if not any(s.alive for s in self.snakes):
            self.state = STATE_GAMEOVER

    # --- Draw ---
    def draw(self):
        self.starfield.draw(self.screen)

        if self.state == STATE_MENU:
            self.hud.draw_menu(self.screen, self.tick)

        elif self.state in (STATE_PLAYING, STATE_PAUSED):
            self.hud.draw_grid(self.screen)
            self.food.draw(self.screen)
            for snake in self.snakes:
                snake.draw(self.screen)
            self.hud.draw_scoreboard(self.screen, self.snakes)
            if self.state == STATE_PAUSED:
                self.hud.draw_pause(self.screen)

        elif self.state == STATE_GAMEOVER:
            self.hud.draw_grid(self.screen)
            self.food.draw(self.screen)
            for snake in self.snakes:
                snake.draw(self.screen)
            winner = max(self.snakes, key=lambda s: s.score)
            self.hud.draw_gameover(self.screen, winner.score, self.tick,
                                   winner_color=winner.skin["head"])

        # flip is handled by main() after scaling to the window
