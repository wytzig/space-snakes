import math
import random
import pygame
from settings import (
    COLS, ROWS, SPEED_NORMAL,
    STATE_MENU, STATE_PLAYING, STATE_PAUSED, STATE_GAMEOVER,
    NUM_SNAKES, AI_SKINS,
    RESPAWN_INTERVAL, RESPAWN_THRESHOLD, RESPAWN_AMOUNT,
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


def _find_free_spawn(occupied):
    """Pick a random head position where the 3-cell starting body fits without overlap."""
    for _ in range(300):
        x = random.randint(3, COLS - 4)
        y = random.randint(1, ROWS - 2)
        if (x, y) not in occupied and (x - 1, y) not in occupied and (x - 2, y) not in occupied:
            return (x, y)
    return None  # grid too full to place a snake


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
        self.corpse_pellets = {}  # (x, y) -> RGB color
        occupied = {pos for s in self.snakes for pos in s.body}
        self.food.spawn(occupied)
        self.move_timer = 0
        self.respawn_timer = 0

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

        # Only alive bodies block movement — dead bodies become corpse food
        all_occupied = {pos for s in self.snakes if s.alive for pos in s.body}

        # AI picks a direction for each snake
        for snake in self.snakes:
            if snake.alive:
                new_dir = self.ai.decide(snake, all_occupied, self.food.pos, self.corpse_pellets)
                snake.set_direction(new_dir)

        # Move all snakes
        for snake in self.snakes:
            if snake.alive:
                snake.move()

        # Cross-collision: head entered another ALIVE snake's body
        for snake in [s for s in self.snakes if s.alive]:
            head = snake.head()
            for other in self.snakes:
                if other is snake or not other.alive:
                    continue
                if head in other.body:
                    snake.alive = False
                    break

        # Dump newly dead snakes' bodies into corpse pellets and clear them
        for snake in self.snakes:
            if not snake.alive and snake.body:
                color = snake.skin["body"]
                for pos in snake.body:
                    self.corpse_pellets[pos] = color
                snake.body = []

        # Food collection (first alive snake to reach food wins the pellet)
        for snake in [s for s in self.snakes if s.alive]:
            if snake.head() == self.food.pos:
                snake.score += 10
                snake.grow()
                occupied = {pos for s in self.snakes if s.alive for pos in s.body}
                occupied |= set(self.corpse_pellets.keys())
                self.food.spawn(occupied)
                break

        # Corpse eating: alive snakes gain 2 pts and grow for each corpse cell eaten
        for snake in [s for s in self.snakes if s.alive]:
            head = snake.head()
            if head in self.corpse_pellets:
                del self.corpse_pellets[head]
                snake.score += 2
                snake.grow()

        # Respawn food if it ended up on a corpse or alive snake body
        all_cells = {pos for s in self.snakes if s.alive for pos in s.body}
        all_cells |= set(self.corpse_pellets.keys())
        if self.food.pos in all_cells:
            self.food.spawn(all_cells)

        # Periodically respawn snakes when the arena gets quiet
        self.respawn_timer += 1
        if self.respawn_timer >= RESPAWN_INTERVAL:
            self.respawn_timer = 0
            alive = sum(1 for s in self.snakes if s.alive)
            if alive < RESPAWN_THRESHOLD:
                occupied = {pos for s in self.snakes if s.alive for pos in s.body}
                occupied |= set(self.corpse_pellets.keys())
                skin_idx = len(self.snakes)  # keep cycling through distinct colors
                for _ in range(RESPAWN_AMOUNT):
                    pos = _find_free_spawn(occupied)
                    if pos is None:
                        break
                    new_snake = Snake(skin=AI_SKINS[skin_idx % len(AI_SKINS)], start_pos=pos)
                    occupied |= set(new_snake.body)
                    self.snakes.append(new_snake)
                    skin_idx += 1

        if not any(s.alive for s in self.snakes):
            self.state = STATE_GAMEOVER

    # --- Draw ---
    def draw(self):
        self.starfield.draw(self.screen)

        if self.state == STATE_MENU:
            self.hud.draw_menu(self.screen, self.tick)

        elif self.state in (STATE_PLAYING, STATE_PAUSED):
            self.hud.draw_grid(self.screen)
            self.hud.draw_corpses(self.screen, self.corpse_pellets)
            self.food.draw(self.screen)
            for snake in self.snakes:
                snake.draw(self.screen)
            self.hud.draw_scoreboard(self.screen, self.snakes)
            if self.state == STATE_PAUSED:
                self.hud.draw_pause(self.screen)

        elif self.state == STATE_GAMEOVER:
            self.hud.draw_grid(self.screen)
            self.hud.draw_corpses(self.screen, self.corpse_pellets)
            self.food.draw(self.screen)
            for snake in self.snakes:
                snake.draw(self.screen)
            winner = max(self.snakes, key=lambda s: s.score)
            self.hud.draw_gameover(self.screen, winner.score, self.tick,
                                   winner_color=winner.skin["head"])

        # flip is handled by main() after scaling to the window
