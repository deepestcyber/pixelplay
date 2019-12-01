import math
import random

import pygame
import pixelplay

board = (
    "#####    #######",
    "#o..######....o#",
    "#.#........#.#.#",
    "#.#.######.#.#.#",
    "#......#...#.#.#",
    "#.####.#.###.#.#",
    "#.#............#",
    "#.#.#######.#.##",
    "#.......#...#.# ",
    "#.##### # ###.# ",
    "#..         #.# ",
    "#.## ### ## #.##",
    " ..  #mmmm#  .  ",
    "##.# ###### #.##",
    " #.#        #.# ",
    "##.# ###### #.##",
    "#o......#.....o#",
    "#.#.###.#.##.#.#",
    "#.#.....c....#.#",
    "#.#.########.#.#",
    "#.#.....#....#.#",
    "#.#####...####.#",
    "#.......#......#",
    "################",
)

stop = (0, 0)
up = (0, -1)
down = (0, 1)
left = (-1, 0)
right = (1, 0)

c_wall = pygame.Color(100, 100, 0)
c_dot = pygame.Color(50, 50, 80)
c_power = pygame.Color(100, 100, 240)
c_pax = pygame.Color(255, 255, 0)
# c_ghost = pygame.Color("red")
c_floor = pygame.Color(0, 0, 0)


def reverse_dir(dir):
    return dir[0] * -1, dir[1] * -1


def neigh(screen, pos, dir):
    x = (pos[0] + dir[0]) % screen.get_width()
    y = (pos[1] + dir[1]) % screen.get_height()
    return x, y


class Ghost:
    num = 0

    def __init__(self, home):
        self.dead = False
        self.dead_cnt = 0
        self.home = home
        self.pos = home
        self.dir = stop
        self.below = c_floor
        self.num = Ghost.num
        self.freq = 1.2 + 0.3*self.num
        self.amp = 0.1
        Ghost.num += 1
        if self.num == 1:
            self.hue = 340
        elif self.num == 2:
            self.hue = 20
        elif self.num == 3:
            self.hue = 320
        else:
            self.hue = 0
        self.delay_value = 3
        self.delay = self.num % self.delay_value

    def get_color(self, n=0, power=0):
        c = pygame.Color(0)
        if power > 30 or power % 3:
            h = 260
            s = 50 + 50 * math.sin(n * self.freq)
            v = 100
            c.hsva = h, s, v
        else:
            v = 100 * (1.0 - 2 * self.amp) + 100 * self.amp * math.sin(n * self.freq)
            c.hsva = self.hue, 100, v
        return c

    def _free_directions(self, screen, player, ghosts):
        ds = []
        for d in (up, down, left, right):
            dest = neigh(screen, self.pos, d)
            c = screen.get_at(dest)
            if c == c_wall:
                continue
            skip = False
            for g in ghosts:
                if dest == g.pos:
                    skip = True
            if skip:
                continue
            ds.append(d)
        return ds

    def die(self):
        self.dead = True
        self.dead_cnt = 200
        self.below = c_floor
        self.pos = self.home

    def revive(self, screen):
        if self.dead:
            if self.dead_cnt > 0:
                self.dead_cnt -= 1
            if self.dead_cnt <= 0:
                if screen.get_at(self.home) == c_floor:
                    self.pos = self.home
                    self.dead = False

    def move(self, screen, player, ghosts):
        if self.dead:
            return None
        if self.delay > 0:
            self.delay -= 1
            return None
        self.delay = self.delay_value
        ds = self._free_directions(screen, pygame, ghosts)
        if not ds:
            # no free directions
            self.dir = stop
            return None

        if self.dir == stop:
            self.dir = random.choice(ds)
#        elif self.dir in ds:
#            pass
        else:
            rev = reverse_dir(self.dir)
            if rev in ds:
                # no turnaround
                ds.remove(rev)
            if not ds:
                self.dir = stop
                return None
            # pick new direction:
            self.dir = random.choice(ds)
        self.pos = neigh(screen, self.pos, self.dir)
        return self.pos


def ghost_at(ghosts, pos):
    for g in ghosts:
        if g.pos == pos:
            return g
    return None


def main():
    pygame.init()
    pygame.mixer.quit()
    screen, parser = pixelplay.from_commandline()
    clock = pygame.time.Clock()

    running = True
    n = 0
    ghosts = []
    delay = 0
    invis = 0
    ku, kd, kl, kr = (False, False, False, False)
    dots = 0
    pos = (8, 10)
    INVIS_TIME = 180

    state = "reset"
    # loop
    while running:
        # frame rate
        clock.tick(20)

        # fetch events
        for event in pygame.event.get():
            # close button or something
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_UP:
                    ku = True
                elif event.key == pygame.K_DOWN:
                    kd = True
                elif event.key == pygame.K_LEFT:
                    kl = True
                elif event.key == pygame.K_RIGHT:
                    kr = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    ku = False
                elif event.key == pygame.K_DOWN:
                    kd = False
                elif event.key == pygame.K_LEFT:
                    kl = False
                elif event.key == pygame.K_RIGHT:
                    kr = False

        if state == "reset":
            print("RESET")
            ku, kd, kl, kr = (False, False, False, False)
            n = 0
            screen.fill(c_floor)
            dots = 0
            delay = 0
            invis = 0
            ghosts = []
            # parse board from def
            for y in range(screen.get_height()):
                for x in range(screen.get_width()):
                    c = board[y][x]
                    if c == "#":
                        screen.set_at((x, y), c_wall)
                    elif c == ".":
                        dots += 1
                        screen.set_at((x, y), c_dot)
                    elif c == "c":
                        pos = (x, y)
                    elif c == "o":
                        dots += 1
                        screen.set_at((x, y), c_power)
                    elif c == "m":
                        ghosts.append(Ghost((x, y)))
            state = "wait"
        elif state == "wait":
            for ghost in ghosts:
                screen.set_at(ghost.pos, ghost.get_color())
            screen.set_at(pos, c_pax)
            if ku or kd or kl or kr:
                print("GO")
                state = "run"
        elif state == "run":
            n += 1
            if invis:
                invis -= 1
            dest = None
            if delay:
                delay -= 1
            else:
                if ku:
                    dest = pos[0], (pos[1] - 1) % screen.get_height()
                elif kd:
                    dest = pos[0], (pos[1] + 1) % screen.get_height()
                elif kl:
                    dest = (pos[0] - 1) % screen.get_width(), pos[1]
                elif kr:
                    dest = (pos[0] + 1) % screen.get_width(), pos[1]
            if dest is not None:
                ghost = ghost_at(ghosts, dest)
                if ghost:
                    # eat what is below flor
                    at_dest = ghost.below
                else:
                    at_dest = screen.get_at(dest)
                if at_dest == c_wall:
                    # cannot enter walls
                    pass
                else:
                    if at_dest == c_power:
                        invis = INVIS_TIME
                    if at_dest == c_dot or at_dest == c_power:
                        dots -= 1
                        print("Dots:", dots)
                        if dots == 0:
                            print("WIN!")
                            state = "win"
                            continue
                    screen.set_at(pos, c_floor)
                    pos = dest
                    delay = 3

            screen.set_at(pos, c_pax)
            for ghost in ghosts:
                ghost.revive(screen)
                if ghost.dead:
                    continue
                prev = ghost.pos
                if prev == pos:
                    # player moved onto ghost
                    if invis:
                        print("nom 1")
                        ghost.die()
                        continue
                    else:
                        print("DIE 1!")
                        state = "die"
                dest = ghost.move(screen, pos, ghosts)
                if dest:
                    screen.set_at(prev, ghost.below)
                    below = screen.get_at(dest)
                    if below == c_pax:
                        below = c_floor
                    ghost.below = below
                if dest is None:
                    dest = prev
                if dest == pos:
                    # collide!
                    if invis:
                        print("nom 2")
                        ghost.die()
                    else:
                        print("DIE 2!")
                        state = "die"
                if not ghost.dead:
                    screen.set_at(dest, ghost.get_color(n, invis))
        else:
            print("invalid state", state)
            state = "reset"

        pygame.display.flip()


if __name__ == '__main__':
    main()
