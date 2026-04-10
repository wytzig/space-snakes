import sys
import asyncio
import pygame
from settings import SCREEN_W, SCREEN_H, FPS, TITLE, WS_URL, STATE_MENU


def load_fonts():
    pygame.font.init()
    try:
        font_large = pygame.font.Font(None, 72)
        font_small = pygame.font.Font(None, 32)
    except Exception:
        font_large = pygame.font.SysFont("monospace", 64, bold=True)
        font_small = pygame.font.SysFont("monospace", 28)
    return font_large, font_small


async def main():
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.RESIZABLE)
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    fonts = load_fonts()
    logical = pygame.Surface((SCREEN_W, SCREEN_H))

    from client_net import ClientNet
    from game import Game
    net = ClientNet(WS_URL)
    game = Game(logical, fonts, net)

    fullscreen = False
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and game.state == STATE_MENU:
                    running = False
                if event.key == pygame.K_f:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.RESIZABLE)
            game.handle_event(event)

        await game.update()
        game.draw()

        win_w, win_h = screen.get_size()
        pygame.transform.scale(logical, (win_w, win_h), screen)
        pygame.display.flip()

        clock.tick(FPS)
        await asyncio.sleep(0)   # yield to event loop (required by Pygbag)

    await net.close()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    asyncio.run(main())
