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
    [0, 0, 0, 1, 0, 0,],
    [1, 1, 0, 1, 1, 0,],
    [1, 1, 1, 1, 1, 1,],
    [0, 0, 1, 1, 1, 0,],
]

resource_tiles_1 = [
    [2, 2, 2,],
    [0, 0, 2,],
]

resource_tiles_2 = [
    [2, 2,],
    [2, 2,],
]


ui_root = ui.UIView(name='root')
ui_renderer = ui.UIRenderer(ui_root)

ui_cargo_view = ui.UIView(name='cargo_view')
ui_resource_view = ui.UIView(name='resource_view')

#ui_hex = ui.UIRegularHexagon(
#    x=320, y=200, name='hexagon', background_color=(32, 32, 32),
#    border_color=(64, 64, 64), border_width=4., side_length=48.)

ui_root.views.append(ui_resource_view)
ui_root.views.append(ui_cargo_view)


BACKGROUND_COLORS = [(32, 64, 32), (64, 32, 32), (32, 32, 64)]
BORDER_COLOR = (64, 64, 64)
HEX_SIDE_LENGTH = 48.


def make_hex(tile, x, y):
    if tile == 0:
        return None
    else:
        return ui.UIRegularHexagon(
            x=x, y=y,
            background_color=BACKGROUND_COLORS[tile - 1],
            border_color=BORDER_COLOR,
            border_width=4.,
            side_length=HEX_SIDE_LENGTH)


def make_hexes(tiles):
    hexes = []
    x = 0.
    y = 0.
    width = ui.UIRegularHexagon.get_width_for_side_length(HEX_SIDE_LENGTH)
    height = ui.UIRegularHexagon.get_height_for_side_length(HEX_SIDE_LENGTH)
    xstep = 0.5 * (width + HEX_SIDE_LENGTH)
    ystep = 0.5 * height
    ystart = 0.
    i, j = 0, 0
    for row in tiles:
        x = 0
        y = ystart
        for tile in row:
            hexagon = make_hex(tile, x, y)
            if hexagon:
                hexagon.user_data = (i, j)
                hexes.append(hexagon)
            x += xstep
            y -= ystep
            ystep = -ystep
            i += 1
        ystart -= height
        ystep = abs(ystep)
        i, j = 0, j + 1
    return hexes


def rotated(arr):
    return zip(*arr[::-1])


def get_offset(tiles):
    xoff, yoff = len(tiles[0]), len(tiles)
    x, y = 0, 0
    for row in tiles:
        for tile in row:
            if tile != 0:
                if x < xoff:
                    xoff, yoff = x, y
                break
            x += 1
        y += 1
        x = 0
    return xoff, yoff


def get_tile(tiles, x, y):
    if y < len(tiles) and x < len(tiles[y]):
        return tiles[y][x]
    else:
        return 0


def can_place(cargo, res, x, y):
    xoff, yoff = get_offset(res)

    x -= xoff
    y -= yoff

    if x < 0 or y < 0:
        return False

    #if len(res) + y > len(cargo) or len(res[0]) + x > len(cargo[0]):
    #    return False

    for i in range(len(res)):
        #print res[i]
        #print cargo[i+y][x:x+len(res[i])]
        for j in range(len(res[i])):
            if res[i][j] != 0 and get_tile(cargo, j + x, i + y) != 1:
                return False
        #print ''

    return True

def try_place(cargo, res, x, y):
    if can_place(cargo, res, x, y):
        xoff, yoff = get_offset(res)

        x -= xoff
        y -= yoff

        for i in range(len(res)):
            for j in range(len(res[i])):
                if res[i][j] != 0:
                    cargo[i + y][j + x] = res[i][j]


@window.event
def on_activate():
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDisable(GL_DEPTH_TEST)
    glClearColor(0., 0., 0., 0.)
    glClearDepth(1.)

    ui_cargo_view.views = make_hexes(cargo_tiles)
    ui_cargo_view.x = 100
    ui_cargo_view.y = 600

    ui_resource_view.views.extend(make_hexes(resource_tiles_1))


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
        x, y = hexa.user_data
        if can_place(cargo_tiles, resource_tiles_1, x, y):
            hexa.border_color = VALID_TILE_BORDER_COLOR
        else:
            hexa.border_color = INVALID_TILE_BORDER_COLOR


@window.event
def on_mouse_press(x, y, button, modifiers):
    if button == pyglet.window.mouse.LEFT:
        if HOVER_TILE:
            tx, ty = HOVER_TILE.user_data
            try_place(cargo_tiles, resource_tiles_1, tx, ty)
            ui_cargo_view.views = make_hexes(cargo_tiles)


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
