# -*- coding: UTF-8 -*-
import argparse
import random

import pygame
import pixelplay


def hsv(r, g, b, a=255):
    c = pygame.Color(int(r), int(g), int(b), int(a))
    h, s, v, _ = c.hsva
    return int(h), int(s), int(v)


def place_food(pa, pos):
    w, h, d = pa.shape
    while True:
        x = random.randrange(w)
        if x == pos[0]:
            continue
        y = random.randrange(h)
        if y == pos[1]:
            continue
        H, S, V = hsv(*pa[x, y])
        if S > 10:
            # hit snake, re-roll
            continue
        pa[x, y] = (0xff, 0xff, 0xff)
        return


def main():
    # start and init pygame:
    pygame.init()
    # need to shut down mixer. It get's started with pygame.init() and eats up 100% cpu
    pygame.mixer.quit()

    parser = argparse.ArgumentParser(description="Coral Snake for LED Tetris Wall")
    parser.add_argument("-d", "--dev", action="store_true", help="Activate development mode")
    #parser = optparse.OptionParser("usage: %prog [options]")
    #parser.add_option("-H", "--host", dest="hostname",
    #                  default=None, type="string",
    #                  help="specify hostname of extended pixelflut server (LED-wall)")

    # instead of pygame.display.setmode() we use a wrapper, supplied by pixelplay
    # pixelplay.get_screen() will just build a screen
    # pixelplay.from_commandline() will parse parameters for remote host
    screen, args = pixelplay.from_commandline(parser)

    dev_on = args.dev

    print("Coral Snake for LED Tetris Wall")
    print("===============================")
    print("Your head is red. Eat the white dots. Do not bite yourself!")
    print("'up', 'down', 'left', 'right' to move.")
    print("'Esc' for exit")
    print("'r' for reset")
    if dev_on:
        print("Dev mode is activated!")
        print("'l' to grow")
        print("'w' to just win")
    print("\nNow et those noms!")

    pygame.display.set_caption("Coral Snake")
    # frame rate controller:
    clock = pygame.time.Clock()
    running = True

    dir_stop = 0, 0
    dir_up = 0, -1
    dir_down = 0, 1
    dir_left = -1, 0
    dir_right = 1, 0
    w, h = (16, 24)
    pos = (8, 3)
    start_pos = (8, 3)
    cur_dir = dir_stop
    state = "reset"
    # generate numpy array that grants direct pixel access:
    pa = pygame.surfarray.pixels3d(screen)
    # player color:
    pl = pygame.Color("red")
    pl.set_length(3)
    l = 10
    while running:
        # delay to respect frame rate
        clock.tick(20)

        # fetch and process all events:
        for event in pygame.event.get():
            # close button or something
            if event.type == pygame.QUIT:
                running = False
            # button pressed
            if event.type == pygame.KEYDOWN:
                # escape, let's quit
                if event.key == pygame.K_ESCAPE:
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                elif event.key == pygame.K_UP:
                    if not cur_dir == dir_down:
                        cur_dir = dir_up
                elif event.key == pygame.K_DOWN:
                    if not cur_dir == dir_up:
                        cur_dir = dir_down
                elif event.key == pygame.K_LEFT:
                    if not cur_dir == dir_right:
                        cur_dir = dir_left
                elif event.key == pygame.K_RIGHT:
                    if not cur_dir == dir_left:
                        cur_dir = dir_right
                elif event.key == pygame.K_l:
                    l += 5
                elif event.key == pygame.K_r:
                    state = "reset"
                elif event.key == pygame.K_w:
                    state = "win"
                    l = 0
            if event.type == pygame.MOUSEBUTTONDOWN:
                # mouse events -- need to down-scale position to internal surface
                # but then again, mouse does not make sense with the wall
                print(pixelplay.scale_down(event.pos))

        if state == "reset":
            # reset board:
            print("RESET")
            screen.fill(pygame.Color(0))
            pos = start_pos
            cur_dir = (0, 0)
            place_food(pa, pos)
            l = 3
            state = "run"
        elif state == "die":
            if l < max(w, h):
                pygame.draw.circle(screen, 0xffffff, pos, l)
                l += 1
            else:
                state = "reset"
        elif state == "win":
            tlen = h*2 + w*2 - 4
            if l == 0:
                pa[:, :, :] //= 4
            p = l % tlen
            c = pygame.Color(0)
            for x in range(w):
                c.hsva = int(360 * p / tlen), 100, 100, 100
                screen.set_at((x, 0), c)
                p = (p - 1) % tlen
            for y in range(h-1):
                c.hsva = int(360 * p / tlen), 100, 100, 100
                screen.set_at((w-1, y+1), c)
                p = (p - 1) % tlen
            for x in range(w-1):
                c.hsva = int(360 * p / tlen), 100, 100, 100
                screen.set_at((w-x-2, h-1), c)
                p = (p - 1) % tlen
            for y in range(h-2):
                c.hsva = int(360 * p / tlen), 100, 100, 100
                screen.set_at((0, h-y-2), c)
                p = (p - 1) % tlen
            l += 1
        elif state == "run":
            # move body forward:
            for y in range(h):
                for x in range(w):
                    c = pygame.Color(int(pa[x, y, 0]), int(pa[x, y, 1]), int(pa[x, y, 2]))
                    (_h, _s, _v, _a) = [int(f) for f in c.hsva]
                    _h = (_h + 3) % 360
                    if _h > l * 3:
                        _s, _v = 0, 0
                    c.hsva = (_h, _s, _v, _a)
                    c.set_length(3)
                    pa[x, y] = c.r, c.g, c.b
            # move head:
            pos = ((pos[0] + cur_dir[0]) % w, (pos[1] + cur_dir[1]) % h)
            # check head destination:
            dest_col = hsv(*pa[pos[0], pos[1]])
            if dest_col[1] > 0:
                if cur_dir != dir_stop:
                    # hit pix with snake body
                    print("DIE!")
                    l = 0
                    state = "die"
            elif dest_col[2] > 30:
                # hit food
                print("nom")
                place_food(pa, pos)
                l += 3
            if l >= 100:
                print("WIN!")
                state = "win"
                l = 0
            # draw head to new position:
            pa[pos[0], pos[1], :] = pl
        else:
            # invalid state
            print("invalid state:", state)
            state = "reset"

        # use flip(), do not use update rects (won't work)
        pygame.display.flip()


if __name__ == '__main__':
    main()
