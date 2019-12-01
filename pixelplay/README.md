Pixelplay is a little wrapper that lets you develop games for the 
deep cyber LED-Tetris-Wall using pygame easily. Only a single line of 
code needs to be adapted.

# Usage
Use pygame normally, but instead of `pygame.display.setmode()` use 
`pixelplay.get_screen()` or `pixelplay.from_commandline()`

    import pygame
    import pixelplay

    # initialise pygame    
    pygame.init()
    # need to shut down mixer. It get's started with pygame.init() and eats up 100% cpu
    pygame.mixer.quit()
    # here you would use `screen = pygame.display.setmode()` normally
    screen = pixelplay.get_screen()
    # [...]
    pygame.display.flip()
    
Now use `screen` as you normally would. Only use `pygame.display.flip()`, 
do not use `update_rects()`, it won't work!


## parsing command line parameters
Use `screen, parser = pixelplay.from_commandline()` have your program 
automatically parse the commandline and potentially connect to the 
given host for the wall. See example games for usage.

