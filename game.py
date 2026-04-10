import pygame
from settings import (
    COLS, ROWS, SPEED_NORMAL,
    STATE_MENU, STATE_PLAYING, STATE_PAUSED, STATE_GAMEOVER,
    DEFAULT_SKIN,
)
from snake import Snake, UP, DOWN, LEFT, RIGHT
from food import Food
from renderer import Starfield, HUD


class Game:
    def __init__(self, screen, fonts):
        self.screen = screen
        self.hud = HUD(*fonts)
        self.starfield = Starfield()
        self.state = STATE_MENU
        self.tick = 0
        self._touch_start = None
        self._reset()

    def _reset(self):
        self.snake = Snake(skin=DEFAULT_SKIN)
        self.food = Food()
        self.food.spawn(set(self.snake.body))
        self.move_timer = 0

    # --- Input ---
    def _handle_swipe(self, dx, dy):
        MIN_SWIPE = 0.05
        if abs(dx) < MIN_SWIPE and abs(dy) < MIN_SWIPE:
            return
        if self.state == STATE_MENU:
            self._reset()
            self.state = STATE_PLAYING
        elif self.state == STATE_PLAYING:
            if abs(dx) > abs(dy):
                self.snake.set_direction(RIGHT if dx > 0 else LEFT)
            else:
                self.snake.set_direction(DOWN if dy > 0 else UP)

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
                if k in (pygame.K_UP, pygame.K_w):
                    self.snake.set_direction(UP)
                elif k in (pygame.K_DOWN, pygame.K_s):
                    self.snake.set_direction(DOWN)
                elif k in (pygame.K_LEFT, pygame.K_a):
                    self.snake.set_direction(LEFT)
                elif k in (pygame.K_RIGHT, pygame.K_d):
                    self.snake.set_direction(RIGHT)
                elif k == pygame.K_p:
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

        self.snake.move()

        if not self.snake.alive:
            self.state = STATE_GAMEOVER
            return

        if self.snake.head() == self.food.pos:
            self.snake.score += 10
            self.snake.grow()
            self.food.spawn(set(self.snake.body))

    # --- Draw ---
    def draw(self):
        self.starfield.draw(self.screen)

        if self.state == STATE_MENU:
            self.hud.draw_menu(self.screen, self.tick)

        elif self.state in (STATE_PLAYING, STATE_PAUSED):
            self.hud.draw_grid(self.screen)
            self.food.draw(self.screen)
            self.snake.draw(self.screen)
            self.hud.draw_score(self.screen, self.snake.score)
            if self.state == STATE_PAUSED:
                self.hud.draw_pause(self.screen)

        elif self.state == STATE_GAMEOVER:
            self.hud.draw_grid(self.screen)
            self.food.draw(self.screen)
            self.snake.draw(self.screen)
            self.hud.draw_gameover(self.screen, self.snake.score, self.tick)

        # flip is handled by main() after scaling to the window
