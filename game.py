import math
import pygame
from settings import (
    STATE_MENU, STATE_PLAYING,
    SKINS, PLAYER_SKINS,
    NEON_PINK, SCREEN_W, SCREEN_H,
)
from snake import draw_snake_body
from food import draw_food_orbs
from renderer import Starfield, HUD
from client_net import ClientNet


class Game:
    def __init__(self, screen, fonts, net: ClientNet):
        self.screen = screen
        self.hud = HUD(*fonts)
        self.starfield = Starfield()
        self.net = net
        self.state = STATE_MENU
        self.tick = 0
        self._food_pulse = 0.0
        self._should_connect = False
        self._connecting = False
        self._touch_start = None
        self._connect_error = None

    # --- Input ---

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
                    self._should_connect = True
                    self._connect_error = None
            elif self.state == STATE_PLAYING:
                if k in (pygame.K_UP, pygame.K_w):
                    self.net.send_direction("UP")
                elif k in (pygame.K_DOWN, pygame.K_s):
                    self.net.send_direction("DOWN")
                elif k in (pygame.K_LEFT, pygame.K_a):
                    self.net.send_direction("LEFT")
                elif k in (pygame.K_RIGHT, pygame.K_d):
                    self.net.send_direction("RIGHT")

    def _handle_swipe(self, dx, dy):
        MIN_SWIPE = 0.05
        if abs(dx) < MIN_SWIPE and abs(dy) < MIN_SWIPE:
            return
        if self.state == STATE_MENU:
            self._should_connect = True
            self._connect_error = None
        elif self.state == STATE_PLAYING:
            if abs(dx) > abs(dy):
                self.net.send_direction("RIGHT" if dx > 0 else "LEFT")
            else:
                self.net.send_direction("DOWN" if dy > 0 else "UP")

    # --- Update (async for Pygbag) ---

    async def update(self):
        self.tick += 1
        self._food_pulse = (self._food_pulse + 0.08) % (2 * math.pi)
        self.starfield.update()
        self.net.poll()  # process buffered JS messages on emscripten

        if self._should_connect:
            self._should_connect = False
            self._connecting = True
            try:
                await self.net.connect()
                self.state = STATE_PLAYING
            except Exception as exc:
                self._connect_error = str(exc)
            finally:
                self._connecting = False

        if self.state == STATE_PLAYING and not self.net.is_connected():
            self.state = STATE_MENU

    # --- Draw ---

    def draw(self):
        self.starfield.draw(self.screen)

        if self.state == STATE_MENU:
            self.hud.draw_menu(self.screen, self.tick)
            status = self.net.connect_status if self._connecting else self._connect_error
            if status:
                color = (200, 200, 255) if self._connecting else NEON_PINK
                label = f"Could not connect: {status}" if self._connect_error and not self._connecting else status
                msg = self.hud.font_small.render(label, True, color)
                self.screen.blit(msg, (SCREEN_W // 2 - msg.get_width() // 2, SCREEN_H // 2 + 140))
            return

        state = self.net.get_state()
        if state is None:
            return   # waiting for first server tick

        self.hud.draw_grid(self.screen)

        foods = [tuple(f) for f in state.get("foods", [])]
        draw_food_orbs(self.screen, foods, self._food_pulse)

        for snake_data in state.get("snakes", []):
            if not snake_data.get("alive", True):
                continue   # skip snakes that failed to respawn this tick
            pid = snake_data["id"]
            body = [tuple(p) for p in snake_data["body"]]
            skin = SKINS[PLAYER_SKINS[pid % len(PLAYER_SKINS)]]
            draw_snake_body(self.screen, body, skin)

        scores = [(s["id"], s["score"]) for s in state.get("snakes", [])]
        self.hud.draw_scores(self.screen, scores, self.net.player_id)
