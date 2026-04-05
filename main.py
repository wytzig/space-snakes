import sys
import pygame
from settings import SCREEN_W, SCREEN_H, FPS, TITLE


def load_fonts():
    pygame.font.init()
    try:
        font_large = pygame.font.Font(None, 72)
        font_small = pygame.font.Font(None, 32)
    except Exception:
        font_large = pygame.font.SysFont("monospace", 64, bold=True)
        font_small = pygame.font.SysFont("monospace", 28)
    return font_large, font_small


def main():
    pygame.init()

    # Resizable OS window — user can drag or maximise freely
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.RESIZABLE)
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    fonts = load_fonts()

    # Game always renders at the fixed logical resolution.
    # main() scales this canvas to fill whatever the window currently is.
    logical = pygame.Surface((SCREEN_W, SCREEN_H))

    from game import Game
    game = Game(logical, fonts)

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
                        # Native resolution fullscreen — logical canvas scales up to fill it
                        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.RESIZABLE)
            game.handle_event(event)

        game.update()
        game.draw()  # draws into logical; does NOT flip

        # Scale logical canvas to the current window size and present
        win_w, win_h = screen.get_size()
        pygame.transform.scale(logical, (win_w, win_h), screen)
        pygame.display.flip()

        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
