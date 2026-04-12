import sys
import asyncio
import pygame
from settings import SCREEN_W, SCREEN_H, FPS, TITLE, WS_URL, STATE_MENU, MUSIC_PATH, MUSIC_VOLUME


def load_fonts():
    pygame.font.init()
    try:
        font_large = pygame.font.Font(None, 72)
        font_small = pygame.font.Font(None, 32)
    except Exception:
        font_large = pygame.font.SysFont("monospace", 64, bold=True)
        font_small = pygame.font.SysFont("monospace", 28)
    return font_large, font_small


def _start_music():
    """Load and loop background music. Silently skips if file missing or mixer unavailable."""
    try:
        pygame.mixer.music.load(MUSIC_PATH)
        pygame.mixer.music.set_volume(MUSIC_VOLUME)
        pygame.mixer.music.play(-1)
    except Exception:
        pass


async def main():
    pygame.mixer.pre_init(44100, -16, 2, 2048)
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

    # Music must start after a user gesture — browsers block autoplay before that.
    # _music_started: written in the event loop below, never reset (one-shot).
    _music_started = False

    fullscreen = False
    running = True

    while running:
        for event in pygame.event.get():
            if not _music_started and event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                _start_music()
                _music_started = True
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
        pygame.mixer.music.set_volume(0.0 if game.muted else MUSIC_VOLUME)

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
