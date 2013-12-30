import pyglet

import time
import math
import random

from pyglet.gl.gl import *
from pyglet.gl.glu import *
#from pyglet.gl.gl.glext_arb import *

import ui
import hexagons

window_width = 1024
window_height = 768

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
    caption='Hexagon Matching Game',
    resizable=False,
    fullscreen=False,
    visible=True,
    vsync=False)

fps_display = pyglet.clock.ClockDisplay()

random.seed(1337)

start_time = time.time()
last_update = 0

cargo_tiles = [
    (-2,  2),
    (-2,  1), (-1,  1), (1,  1),
    (-1,  0), ( 0,  0), (1,  0), (2,  0),
              ( 0, -1), (1, -1), (2, -1),
                        (1, -2), (2, -2), (3, -2),
]

resource_tiles_1 = [
    (-1, 1), (0, 1), (1, 0), (1, -1),
]

resource_tiles_2 = [
    (-1, 1), (0, 1), (0, 0), (1, 0),
]

all_resource_tiles = [
    resource_tiles_1,
    resource_tiles_2,
]

resource_tiles = random.choice(all_resource_tiles)


ui_root = ui.UIView(name='root')
ui_renderer = ui.UIRenderer(ui_root)

ui_cargo_view = ui.UIView(name='cargo_view')
ui_resource_view = ui.UIView(name='resource_view')

ui_root.views.append(ui_resource_view)
ui_root.views.append(ui_cargo_view)


BACKGROUND_COLORS = [(32, 64, 32), (224, 224, 64), (32, 32, 64)]
BORDER_COLOR = (64, 64, 64)
HEX_SIDE_LENGTH = 48.


def make_hex(tile, x, y, tx, ty, side_length):
    if tile == 0:
        return None
    else:
        return ui.UIRegularHexagon(
            x=x, y=y,
            background_color=BACKGROUND_COLORS[tile - 1],
            border_color=BORDER_COLOR,
            border_width=4.,
            side_length=side_length,
            user_data=(tx, ty))


def make_hexes(tiles, tile_type, side_length):
    width = hexagons.side_length_to_width(side_length)
    height = hexagons.side_length_to_height(side_length)
    xstep = 0.5 * (width + side_length)
    ystep = 0.5 * height

    hexes = []

    for (tx, ty) in tiles:
        x = tx * xstep
        y = ty * height + tx * ystep
        hexes.append(make_hex(tile_type, x, y, tx, ty, side_length))

    return hexes


def rotated(tiles):
    return [hexagons.rot_qr((tx, ty)) for (tx, ty) in tiles]


def can_place(cargo, res, x, y):
    return all((tx + x, ty + y) in cargo for (tx, ty) in res)


def try_place(cargo, res, x, y):
    if can_place(cargo, res, x, y):
        return True
    else:
        return False


@window.event
def on_activate():
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDisable(GL_DEPTH_TEST)
    glClearColor(0., 0., 0., 0.)
    glClearDepth(1.)

    ui_cargo_view.views = make_hexes(cargo_tiles, 1, HEX_SIDE_LENGTH)
    ui_cargo_view.x = window_width // 2
    ui_cargo_view.y = window_height // 2

    ui_resource_view.views = make_hexes(
        resource_tiles, 2, HEX_SIDE_LENGTH / 2.)


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

    #for view in ui_cargo_view.views:
    #    x, y = view.user_data
    #    if can_place(cargo_tiles, resource_tiles_1, x, y):
    #        view.background_color = (64, 64, 255)
    #    else:
    #        view.background_color = (255, 64, 64)

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


HOVER_TILE = None
HOVER_TILE_PREV_COLOR = None
HOVER_TILE_BORDER_COLOR = (128, 128, 128)
VALID_TILE_BORDER_COLOR = (64, 255, 64)
INVALID_TILE_BORDER_COLOR = (255, 64, 64)

@window.event
def on_mouse_motion(x, y, dx, dy):
    global HOVER_TILE
    global HOVER_TILE_PREV_COLOR

    ui_resource_view.x = x
    ui_resource_view.y = y

    hexa = ui_cargo_view.intersect(x, y)

    if HOVER_TILE != hexa:
        if HOVER_TILE:
            HOVER_TILE.border_color = HOVER_TILE_PREV_COLOR
        if hexa:
            ui_cargo_view.bring_to_front(hexa)
            HOVER_TILE_PREV_COLOR = hexa.border_color
            hexa.border_color = HOVER_TILE_BORDER_COLOR
    HOVER_TILE = hexa

    if hexa:
        tx, ty = hexa.user_data
        if can_place(cargo_tiles, resource_tiles, tx, ty):
            hexa.border_color = VALID_TILE_BORDER_COLOR
        else:
            hexa.border_color = INVALID_TILE_BORDER_COLOR


@window.event
def on_mouse_press(x, y, button, modifiers):
    global resource_tiles

    if button == pyglet.window.mouse.LEFT:
        if HOVER_TILE:
            tx, ty = HOVER_TILE.user_data
            if try_place(cargo_tiles, resource_tiles, tx, ty):
                ui_cargo_view.views = make_hexes(
                    cargo_tiles, 1, HEX_SIDE_LENGTH)

                resource_tiles = random.choice(all_resource_tiles)
                ui_resource_view.views = make_hexes(
                    resource_tiles, 2, HEX_SIDE_LENGTH / 2.)

    elif button == pyglet.window.mouse.RIGHT:
        resource_tiles = rotated(resource_tiles)
        ui_resource_view.views = make_hexes(
            resource_tiles, 2, HEX_SIDE_LENGTH / 2.)



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
    #if ui_hex.intersect(MX, MY):
    #    ui_hex.border_color = (64, 64, 255)
    #else:
    #    ui_hex.border_color = (255, 64, 64)
    pass


pyglet.clock.schedule_interval(update, 1. / 60.)

pyglet.app.run()
