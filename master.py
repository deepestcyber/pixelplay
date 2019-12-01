import os

import pygame
from fluter import Fluter

games = [
    ("coralsnake.py", "Coral Snake"),
    ("coralsnake.py", "Coral Snake, God Mode", "-d --iddqd"),
    ("paxman.py", "Pax-Man"),
    (None, )
]


def main():
    host = "localhost"
    Fluter(host=host)
    pygame.init()
    pygame.mixer.quit()
    pygame.key.set_repeat(200, 50)
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Game Selection")

    clock = pygame.time.Clock()
    running = True

    font_big = pygame.font.SysFont("comicsansms", 22)
    font = pygame.font.SysFont("comicsansms", 18)
    pos = 0
    while running:
        screen.fill(pygame.Color(10, 50, 50))
        text = font_big.render("Select game and press enter or start:", True, pygame.Color("white"))
        screen.blit(text, (10, 5))
        sx = 15
        sy = 5 + text.get_height() + 5
        for n, game in enumerate(games):
            if game[0] is None:
                raw_text = "exit game selector"
            else:
                raw_text = game[0]
                if len(game) > 1 and game[1]:
                    raw_text = game[1]
            c = pygame.Color("yellow" if pos == n else 0xaaaaaa)
            text = font.render(raw_text, True, c)
            screen.blit(text, (sx, sy + 20 * n))
        pygame.display.flip()

        clock.tick(15)

        for event in pygame.event.get():
            # close button or something
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    pos = (pos + 1) % len(games)
                elif event.key == pygame.K_UP:
                    pos = (pos - 1) % len(games)
                elif event.key == pygame.K_RETURN:
                    game = games[pos]
                    if game[0] is None:
                        running = False
                    else:
                        os.system("python {game} -H {host} {parm}".format(
                            game=game[0],
                            parm=game[2] if len(game) > 2 and game[2] else "",
                            host=host,
                        ))


if __name__ == '__main__':
    main()
