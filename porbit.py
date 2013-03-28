import sys, pygame
import boxloop_em as bl
import numpy as np

#test

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

params = np.loadtxt("porbit_init.dat", dtype=str, delimiter="$$$")
for param in params:
   psplit = param.split("=")
   key = psplit[0].replace(" ", "")
   val = psplit[1].replace(" ", "")
   if key == "x": xpos = float(val)
   elif key == "y": ypos = float(val)
   elif key == "xvel": xvel = float(val)
   elif key == "yvel": yvel = float(val)
   elif key == "dt": dt = float(val)
   elif key == "q": q = float(val)
   elif key == "speed": update_every = int(val)
x = (xpos, ypos)
p = (xvel, yvel)

time = 0.
screen.blit(background, (0,0))
running = True
while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
        if event.type == pygame.KEYDOWN:
            if (event.key == pygame.K_ESCAPE or event.key == pygame.K_q):
                pygame.quit()
                sys.exit()
            if event.key == pygame.K_SPACE:
                if running: running = False
                else: running = True
            if event.key == pygame.K_UP:
                update_every += 10
            if event.key == pygame.K_DOWN:
                if update_every > 10:
                    update_every -= 10
                else:
                    update_every = 1
            if event.key == pygame.K_c:
                screen.blit(background, (0,0))

    if running:
        for ii in range(update_every):
            prev_x = tuple(x)
            x, p = bl.sia4(x, p, time, dt, 2, q)
            time += dt
            pygame.draw.line(screen, white, plot2screen(prev_x), plot2screen(x), 1)

    pygame.display.flip()
