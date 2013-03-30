import sys, pygame
import boxloop_em as bl
import numpy as np

pygame.init()

width, height = 1200, 600
size = np.array([width, height])
box_w = box_h = height
box_size = np.array([box_w, box_h])
# how far into positive and negative the x and y axes of each plot go:
orbit_ext = [1.1, 1.1]
sect_ext = [1.1, 2.0]

def screen2plot((x, y), size, plotextents):
    xpixelsize = 2.*plotextents[0]/float(size[0])
    ypixelsize = 2.*plotextents[1]/float(size[1])
    y = size[1] - y
    x -= 0.5*size[0]
    y -= 0.5*size[1]
    return x*xpixelsize, y*ypixelsize

def plot2screen((x, y), size, plotextents):
    xpixelsize = 2.*plotextents[0]/float(size[0])
    ypixelsize = 2.*plotextents[1]/float(size[1])
    x /= xpixelsize
    y /= ypixelsize
    x += 0.5*size[0]
    y += 0.5*size[1]
    y = size[1] - y
    return int(round(x)), int(round(y))

black = 0, 0, 0
grey = 80, 80, 80
white = 255, 255, 255

screen = pygame.display.set_mode(size)

background = pygame.Surface(size)
background.fill(black)

orbit_box = pygame.Surface(box_size)
pygame.draw.rect(orbit_box, white, [0,0,box_w,box_h], 1)
sect_box = pygame.Surface(box_size)
pygame.draw.rect(sect_box, white, [0,0,box_w,box_h], 1)

def draw_axes(surface, plotextents):
    pygame.draw.line(surface, grey, (0, box_h/2), (box_w, box_h/2), 1)
    pygame.draw.line(surface, grey, (box_w/2, 0), (box_w/2, box_h), 1)
    halftick = 0.002
    tickspacing = 0.1
    for xx in np.linspace(-plotextents[0], plotextents[0],\
        int(round(2.*plotextents[0]/tickspacing+1))):
        pygame.draw.line(surface, grey, plot2screen((xx, -halftick),\
            box_size, plotextents), plot2screen((xx, halftick), box_size,\
            plotextents), 1)
    for yy in np.linspace(-plotextents[1], plotextents[1],\
        int(round(2.*plotextents[1]/tickspacing+1))):
        pygame.draw.line(surface, grey, plot2screen((-halftick, yy),\
            box_size, plotextents), plot2screen((halftick, yy), box_size,\
            plotextents), 1)

draw_axes(orbit_box, orbit_ext)
draw_axes(sect_box, sect_ext)

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
    elif key == "energy":
        en = float(val)
        yvel = np.sqrt(2.*en-np.log(0.15*0.15+xpos*xpos))        
x = (xpos, ypos)
p = (xvel, yvel)

time = 0.
screen.blit(background, (0,0))
screen.blit(orbit_box, (0,0))
screen.blit(sect_box, (width/2,0))
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
                screen.blit(orbit_box, (0,0))

    if running:
        for ii in range(update_every):
            prev_x = tuple(x)
            x, p = bl.sia4(x, p, time, dt, 2, q)
            time += dt
            pygame.draw.line(screen, white, plot2screen(prev_x, box_size, orbit_ext), plot2screen(x, box_size, orbit_ext), 1)
            if p[1] > 0. and x[1]*prev_x[1] <= 0.:
                sect_box.set_at(plot2screen((x[0],p[0]), box_size, sect_ext), white)
                screen.blit(sect_box, (width/2,0))

    pygame.display.flip()
