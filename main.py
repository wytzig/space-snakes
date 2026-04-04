import sys
import pygame
from settings import SCREEN_W, SCREEN_H, FPS, TITLE

def load_fonts():
    pygame.font.init()
    # Try to use a built-in monospace font; swap for a .ttf in assets/fonts/ later
    try:
        font_large = pygame.font.Font(None, 72)
        font_small = pygame.font.Font(None, 32)
    except Exception:
        font_large = pygame.font.SysFont("monospace", 64, bold=True)
        font_small = pygame.font.SysFont("monospace", 28)
    return font_large, font_small


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    fonts = load_fonts()

    # Import here so pygame is already init'd
    from game import Game
    game = Game(screen, fonts)

    fullscreen = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and game.state == "menu":
                    running = False
                if event.key == pygame.K_f:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
                    game.screen = screen
            game.handle_event(event)

        game.update()
        game.draw()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
