import sys, pygame
import boxloop_em as bl
import numpy as np

pygame.init()

width, height = 800, 800
size = np.array([width, height])
plotextent = 0.5

def screen2plot((x, y)):
    xpixelsize = 2.*plotextent/float(width)
    ypixelsize = 2.*plotextent/float(height)
    y = height - y
    x -= 0.5*width
    y -= 0.5*height
    return x*xpixelsize, y*ypixelsize

def plot2screen((x, y)):
    xpixelsize = 2.*plotextent/float(width)
    ypixelsize = 2.*plotextent/float(height)
    x /= xpixelsize
    y /= ypixelsize
    x += 0.5*width
    y += 0.5*height
    y = height - y
    return int(round(x)), int(round(y))

black = 0, 0, 0
grey = 80, 80, 80
white = 255, 255, 255

screen = pygame.display.set_mode(size)

background = pygame.Surface(size)
background.fill(black)
pygame.draw.line(background, grey, (0, height/2), (width, height/2), 1)
pygame.draw.line(background, grey, (width/2, 0), (width/2, height), 1)
halftick = 0.002
tickspacing = 0.1
for xx in np.linspace(-plotextent, plotextent, int(round(2.*plotextent/tickspacing+1))):
    pygame.draw.line(background, grey, plot2screen((xx, -halftick)), plot2screen((xx, halftick)), 1)
for yy in np.linspace(-plotextent, plotextent, int(round(2.*plotextent/tickspacing+1))):
    pygame.draw.line(background, grey, plot2screen((-halftick, yy)), plot2screen((halftick, yy)), 1)

### PARAMETERS TO FIDDLE WITH ###
x = (0.0, 0.0)
p = (1.2, 0.7)
dt = 0.001
q = 0.9
update_every = 50
#################################

time = 0.
screen.blit(background, (0,0))
while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
        if event.type == pygame.KEYDOWN:
            if (event.key == pygame.K_ESCAPE or event.key == pygame.K_q):
                pygame.quit()
                sys.exit()

    #prev_x = tuple(x)

    for ii in range(update_every):
        prev_x = tuple(x)
        x, p = bl.sia4(x, p, time, dt, 2, q)
        time += dt

        pygame.draw.line(screen, white, plot2screen(prev_x), plot2screen(x), 1)

    pygame.display.flip()
