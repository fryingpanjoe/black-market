import pyglet

import time
import math
import random

from pyglet.gl.gl import *
from pyglet.gl.glu import *
#from pyglet.gl.gl.glext_arb import *

import ui

window_width = 1024
window_height = 768

fov = 45
clip_near = 1
clip_far = 8192

platform = pyglet.window.get_platform()
display = platform.get_default_display()
screen = display.get_default_screen()

config_template = pyglet.gl.Config(
    alpha_size=8,
    depth_size=24,
    double_buffer=True,
    sample_buffers=True,
    samples=8)

window = pyglet.window.Window(
    config=config_template,
    width=window_width,
    height=window_height,
    caption='Black Market Prototype',
    resizable=False,
    fullscreen=False,
    visible=True,
    vsync=False)

fps_display = pyglet.clock.ClockDisplay()

# game stuff

random.seed(1337)

start_time = time.time()
last_update = 0

ui_root = ui.UIView()
ui_renderer = ui.UIRenderer(ui_root)


cargo_template = [
    [1, 0, 0, 1, 1, 0,],
    [1, 1, 1, 1, 1, 0,],
    [0, 1, 1, 1, 1, 1,],
    [0, 0, 0, 1, 0, 0,],
]


resource_1 = [
    [2, 2, 2,],
    [0, 0, 2,],
]


BACKGROUND_COLOR = (32, 32, 32)
BORDER_COLORS = [(64, 64, 64), (64, 64, 255), (255, 64, 64)]


def make_hex(tile):
    if tile == 0:
        return None
    else:
        return ui.UIRegularHexagon(
            x=0, y=0,
            background_color=BACKGROUND_COLOR,
            border_color=BORDER_COLORS[tile - 1],
            border_width=4.,
            side_length=48.)


def make_hexes(tiles):
    return [make_hex(tile) for tile in tiles]


def rotated(arr):
    return zip(*arr[::-1])


def can_place(cargo, res, x, y):
    if len(res) + y > len(cargo):
        return False

    if len(res[0]) + x > len(carg[0]):
        return False

    for i in range(len(res)):
        for j in range(len(res[i])):
            if res[i][j] != 0 and cargo[i + y][j + x] != 1:
                return False

    return True


@window.event
def on_activate():
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDisable(GL_DEPTH_TEST)
    glClearColor(0., 0., 0., 0.)
    glClearDepth(1.)


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
    glClear(GL_COLOR_BUFFER_BIT)

    # hud drawing
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, window_width, 0, window_height, 0, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    ui_renderer.draw(window_width, window_height)

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
