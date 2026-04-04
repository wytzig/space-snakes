import pygame
from settings import (
    COLS, ROWS, CELL, FPS, SPEED_NORMAL,
    STATE_MENU, STATE_PLAYING, STATE_PAUSED, STATE_GAMEOVER,
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
        self._reset()

    def _reset(self):
        self.snake = Snake()
        self.food  = Food()
        self.score = 0
        self.move_timer = 0

    # --- Input ---
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            k = event.key
            if self.state == STATE_MENU:
                if k == pygame.K_RETURN:
                    self.state = STATE_PLAYING
                    self._reset()
            elif self.state == STATE_PLAYING:
                if k in (pygame.K_UP,    pygame.K_w): self.snake.set_direction(UP)
                if k in (pygame.K_DOWN,  pygame.K_s): self.snake.set_direction(DOWN)
                if k in (pygame.K_LEFT,  pygame.K_a): self.snake.set_direction(LEFT)
                if k in (pygame.K_RIGHT, pygame.K_d): self.snake.set_direction(RIGHT)
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
        if self.move_timer >= SPEED_NORMAL:
            self.move_timer = 0
            self.snake.move()

            if not self.snake.alive:
                self.state = STATE_GAMEOVER
                return

            if self.snake.head() == self.food.pos:
                self.score += 10
                self.snake.grow()
                self.food.spawn(self.snake.body)

    # --- Draw ---
    def draw(self):
        self.starfield.draw(self.screen)

        if self.state == STATE_MENU:
            self.hud.draw_menu(self.screen, self.tick)

        elif self.state in (STATE_PLAYING, STATE_PAUSED):
            self.hud.draw_grid(self.screen)
            self.food.draw(self.screen)
            self.snake.draw(self.screen)
            self.hud.draw_score(self.screen, self.score)
            if self.state == STATE_PAUSED:
                self.hud.draw_pause(self.screen)

        elif self.state == STATE_GAMEOVER:
            self.hud.draw_grid(self.screen)
            self.food.draw(self.screen)
            self.snake.draw(self.screen)
            self.hud.draw_gameover(self.screen, self.score, self.tick)

        pygame.display.flip()
