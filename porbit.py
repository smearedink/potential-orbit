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
yellow = 255, 255, 0
magenta = 255, 0, 255

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
    elif key == "speed_increment": speed_increment = int(val)
    elif key == "energy":
        en = float(val)
        yvel = np.sqrt(2.*en-xvel*xvel-np.log(0.15*0.15+xpos*xpos))        
x = (xpos, ypos)
p = (xvel, yvel)

screen = pygame.display.set_mode(size)

background = pygame.Surface(size)
background.fill(black)

orbit_box_bg = pygame.Surface(box_size)
sect_box_bg = pygame.Surface(box_size)

def draw_axes(surface, plotextents):
    pygame.draw.line(surface, grey, (0, box_h/2), (box_w, box_h/2), 1)
    pygame.draw.line(surface, grey, (box_w/2, 0), (box_w/2, box_h), 1)
    halftick_pixels = 2
    halftick_x = halftick_pixels * 2.*plotextents[1]/box_h
    halftick_y = halftick_pixels * 2.*plotextents[0]/box_w
    tickspacing = 0.1
    for xx in np.linspace(-plotextents[0], plotextents[0],\
        int(round(2.*plotextents[0]/tickspacing+1.))):
        pygame.draw.line(surface, grey, plot2screen((xx, -halftick_x),\
            box_size, plotextents), plot2screen((xx, halftick_x), box_size,\
            plotextents), 1)
    for yy in np.linspace(-plotextents[1], plotextents[1],\
        int(round(2.*plotextents[1]/tickspacing+1.))):
        pygame.draw.line(surface, grey, plot2screen((-halftick_y, yy),\
            box_size, plotextents), plot2screen((halftick_y, yy), box_size,\
            plotextents), 1)

def potential(x, y, q):
    return 0.5*np.log(0.15*0.15+x*x+y*y/(q*q))

xg, yg = np.meshgrid(np.linspace(-orbit_ext[0], orbit_ext[0], width/2), np.linspace(-orbit_ext[1], orbit_ext[1], height))
# create grid that varies between 0 and <255 (ie, still grey at max)
potl = potential(xg, yg, q)
potl -= np.min(potl)
potl /= np.max(potl)
potl *= 100
potl = 100 - potl
potl = np.transpose(np.round(potl).astype(int))

#draw_axes(orbit_box_bg, orbit_ext)
pygame.surfarray.blit_array(orbit_box_bg, np.dstack((potl,potl,potl)))
draw_axes(sect_box_bg, sect_ext)

pygame.draw.rect(orbit_box_bg, white, [0,0,box_w,box_h], 1)
pygame.draw.rect(sect_box_bg, white, [0,0,box_w,box_h], 1)

orbit_box = pygame.Surface(size)
orbit_box.blit(orbit_box_bg, (0,0))
sect_box = pygame.Surface(size)
sect_box.blit(sect_box_bg, (0,0))

time = 0.
screen.blit(background, (0,0))
screen.blit(orbit_box, (0,0))
screen.blit(sect_box, (width/2,0))
running = True
trails = True
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
                update_every += speed_increment
            if event.key == pygame.K_DOWN:
                if update_every > speed_increment:
                    update_every -= speed_increment
                else:
                    update_every = 1
            if event.key == pygame.K_c:
                orbit_box.blit(orbit_box_bg, (0,0))
            if event.key == pygame.K_t:
                if trails:
                    trails = False
                    orbit_box.blit(orbit_box_bg, (0,0))
                else: trails = True
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                sect_x = event.pos[0] - width/2
                sect_y = event.pos[1]
                sect_co = screen2plot((sect_x, sect_y), box_size, sect_ext)
                if (sect_co[0] > -sect_ext[0])\
                    and (sect_co[0] < sect_ext[0])\
                    and (sect_co[1] > -sect_ext[1])\
                    and (sect_co[1] < sect_ext[1]):
                    xpos = sect_co[0]
                    xvel = sect_co[1]
                    yvelsq = 2.*en-xvel*xvel-np.log(0.15*0.15+xpos*xpos)
                    if yvelsq < 0:
                        print "You are trying to select an x,xdot pair that is inaccessible at the current energy."
                    else:
                        x = (xpos, 0.)
                        prev_x = tuple(x)
                        p = (xvel, np.sqrt(yvelsq))
                        orbit_box.blit(orbit_box_bg, (0,0))

    if running:
        for ii in range(update_every):
            prev_x = tuple(x)
            x, p = bl.sia4(x, p, time, dt, 2, q)
            time += dt
            screen_x = plot2screen(x, box_size, orbit_ext)
            if trails:
                pygame.draw.line(orbit_box, white, plot2screen(prev_x, box_size, orbit_ext), screen_x, 1)
            screen.blit(orbit_box, (0,0))
            pygame.draw.circle(screen, magenta, screen_x, 4)
            if p[1] > 0. and x[1]*prev_x[1] <= 0.:
                #sect_box.set_at(plot2screen((x[0],p[0]), box_size, sect_ext), white)
                screen_coords = plot2screen((x[0],p[0]), box_size, sect_ext)
                pygame.draw.rect(sect_box, white, [screen_coords[0], screen_coords[1], 2, 2], 1)
            screen.blit(sect_box, (width/2,0))

    pygame.display.flip()
