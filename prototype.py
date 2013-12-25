import pyglet

import time
import math
import random

from pyglet.gl.gl import *
from pyglet.gl.glu import *
#from pyglet.gl.gl.glext_arb import *

# pyglet init

window_width = 1024
window_height = 768

fov = 45
clip_near = 1
clip_far = 8192

platform = pyglet.window.get_platform()
display = platform.get_default_display()
screen = display.get_default_screen()

template = pyglet.gl.Config(
    alpha_size=8,
    depth_size=16,
    double_buffer=True)
config = screen.get_best_config(template)

context = config.create_context(None)

window = pyglet.window.Window(
    width=window_width,
    height=window_height,
    caption='Black Market Prototype',
    resizable=False,
    fullscreen=False,
    visible=True,
    vsync=False,
    context=context)

fps_display = pyglet.clock.ClockDisplay()

# game stuff

random.seed(1337)

camera = (-50., 100., 250.)
center = (0., 0., 0.)
num_planets = 12
planet_sizes = [0.2 + random.random() * float(0.5 + 0.2 * i) for i in range(num_planets)]
planet_dist = [(d, 0.6 * d) for d in [float(10. + 10. * i + 2. * random.random()) for i in range(num_planets)]]
planet_speed = [1. * (0.1 + 2. * random.random()) for i in range(num_planets)]
planet_time_shift = [random.random() * 10. for i in range(num_planets)]
planet_color = [(random.random(), random.random(), random.random()) for i in range(num_planets)]

start_time = time.time()
last_update = 0

sphere = gluNewQuadric()


def draw_sphere(x, y, z, r, g, b, radius):
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(r, g, b)
    gluSphere(sphere, radius, 20, 20)
    glPopMatrix()


@window.event
def on_activate():
    # setup gl
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDepthFunc(GL_LEQUAL)


@window.event
def on_draw():
    global start_time
    global last_update

    window.clear()

    # update time
    now = time.time() - start_time
    if now < last_update:
        last_update = now
    frame_time = now - last_update
    last_update = now

    # clear screen
    glClearColor(0., 0., 0., 0.)
    glClearDepth(1.)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # 3d drawing
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fov, float(window_width) / window_height, clip_near, clip_far)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(
        camera[0], camera[1], camera[2],
        center[0], center[1], center[2],
        0, 1, 0)
    glEnable(GL_DEPTH_TEST)

    draw_sphere(0, 0, 0, 1, 1, 0, 5)

    for i in range(num_planets):
        size = planet_sizes[i]
        distx, disty = planet_dist[i]
        speed = planet_speed[i]
        time_shift = planet_time_shift[i]
        r, g, b = planet_color[i]
        #angle_shift = planet_angle_shift[i]
        t = speed * now + time_shift
        x, y = distx * math.cos(t), disty * math.sin(t)
        draw_sphere(x, 0, y, r, g, b, size)

    # ...

    # hud drawing
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, window_width, 0, window_height, 0, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glDisable(GL_DEPTH_TEST)

    # ...

    # draw fps
    fps_display.draw()


@window.event
def on_key_press(symbol, modifiers):
    pass


@window.event
def on_key_release(symbol, modifiers):
    pass


@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    pass


@window.event
def on_mouse_enter(x, y):
    pass


@window.event
def on_mouse_leave(x, y):
    pass


@window.event
def on_mouse_motion(x, y, dx, dy):
    pass


@window.event
def on_mouse_press(x, y, button, modifiers):
    pass


@window.event
def on_mouse_release(x, y, button, modifiers):
    pass


@window.event
def on_mouse_scroll(x, y, scroll_x, scroll_y):
    pass


@window.event
def on_resize(width, height):
    global window_width
    global window_height
    window_width = width
    window_height = height
    glViewport(0, 0, window_width, window_height)


def update(frame_time):
    pass

pyglet.clock.schedule_interval(update, 1. / 60.)

pyglet.app.run()
