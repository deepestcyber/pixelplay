import base64
import socket

import pygame

global_zoom = 1


def scale_up(r):
    return tuple(n * global_zoom for n in r)


def scale_down(r):
    return tuple(n // global_zoom for n in r)


def get_screen(size=None, zoom=16, remote=None):
    """
    Return pygame Surface to be used for output.
    :param size: (w, h), resolution of your display. Defaults to (16, 24)
    :param zoom: Zoom factor for onscreen display. Defaults to 16. Set to 0 to disable display.
    :param remote: (host, port), host to connect to for Wall. Defaults to no remote host.
    :return: Surface to use for output.
    """
    global global_zoom
    global_zoom = zoom
    if size is None:
        size = (16, 24)
    # surface = pygame.Surface(size, depth=8*3, masks=(0xff0000, 0x00ff00, 0x0000ff, 0x000000))
    surface = pygame.Surface(size, depth=8 * 3)
    if zoom == 0:
        screen_size = (10, 10)
    else:
        screen_size = (size[0] * zoom, size[1] * zoom)
    screen = pygame.display.set_mode(screen_size)
    pixels = pygame.surfarray.pixels3d(surface)
    # screen.set_masks((0xff0000, 0x00ff00, 0x0000ff, 0x000000))
    # screen.set_masks((0x0000ff, 0x00ff00, 0xff0000, 0x000000))
    original_flip = pygame.display.flip

    def get_socket():
        # TODO: reconnect on error
        if remote is None:
            return None
        sock = None
        if sock is None:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(remote)
            return sock

    def new_flip():
        if zoom > 0:
            for y in range(size[1]):
                for x in range(size[0]):
                    rect = pygame.Rect(x * zoom, y * zoom, zoom, zoom)
                    # rect = pygame.Rect(scale_up((x, y, 1, 1)))
                    pygame.draw.rect(screen, surface.get_at((x, y)), rect)
        original_flip()
        sock = get_socket()
        if sock is not None:
            encoded = base64.b64encode(pixels.flatten("K"))
            sock.send(b"WL " + encoded + b"\n")

    pygame.display.flip = new_flip

    def new_get_surface():
        return surface

    pygame.display.get_surface = new_get_surface
    return surface


def from_commandline(parser=None):
    """
    Create screen surface from command line parameters.
    :param parser: (optinal) pre-configured argparse object to use.
    :return: (screen, parser)
    """
    if parser is None:
        import argparse
        parser = argparse.ArgumentParser()
    parser.add_argument("-H", "--host", default=None, type=str, dest="hostname",
                        help="specify hostname of extended pixelflut server (LED-wall)")
    parser.add_argument("-p", "--port", dest="portnum", default=1234,
                        type=int, help="port number on pixelflut host")
    parser.add_argument("--width", type=int, default=16,
                        help="Width of display in pixels")
    parser.add_argument("--height", type=int, default=24,
                        help="Height of display in pixels")
    parser.add_argument("-z", "--zoom", dest="zoom",
                        default=16, type=int, help="Zoom factor on local surface, 0 to disable")

    args = parser.parse_args()
    remote = None
    if args.hostname is not None:
        remote = (args.hostname, args.portnum)
    screen = get_screen(size=(args.width, args.height), remote=remote, zoom=args.zoom)
    return screen, args
