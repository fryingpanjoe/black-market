import uuid
import math
import itertools

from pyglet.gl.gl import *
from pyglet.gl.glu import *

import pyglet.graphics

import hexagons


class UIEventHandler(object):

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        pass

    def on_resize(self, width, height):
        pass

    def on_mouse_enter(self, x, y):
        pass

    def on_mouse_leave(self, x, y):
        pass

    def on_mouse_motion(self, x, y, dx, dy):
        pass

    def on_mouse_press(self, x, y, button, modifiers):
        pass

    def on_mouse_release(self, x, y, button, modifiers):
        pass

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        pass


class UIRenderer(object):

    def __init__(self, root_view):
        self.root_view = root_view

    def draw(self, screen_width, screen_height):
        #glViewport(0, 0, screen_width, screen_height)

        #glMatrixMode(GL_PROJECTION)
        #glPushMatrix()
        #glLoadIdentity()

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        self.root_view.pre_draw()
        self.root_view.draw()
        self.root_view.post_draw()

        glPopMatrix()

        #glMatrixMode(GL_PROJECTION)
        #glPopMatrix()


class DNDContext(object):

    def __init__(self, x=0, y=0, dragged=None, hover=None):
        self.x = x
        self.y = y
        self.dragged = dragged
        self.hover = hover


class UIView(object):

    def __init__(self, x=0, y=0, name=None, is_enabled=True, is_visible=True,
                 is_selected=False, can_click=True, can_toggle=False,
                 can_drag=False, can_drop=False, user_data=None, **kwargs):
        self.uuid = uuid.uuid4()
        self.x = x
        self.y = y
        self.name = name
        self.is_hover = False
        self.is_enabled = is_enabled
        self.is_visible = is_visible
        self.is_selected = is_selected
        self.can_click = can_click
        self.can_toggle = can_toggle
        self.can_drag = can_drag
        self.can_drop = can_drop
        self.user_data = user_data
        self.views = []

    def pre_draw(self):
        #print 'pre_draw', self.name

        glPushMatrix()
        glTranslatef(self.x, self.y, 0.)

    def draw(self):
        #print 'draw', self.name

        if not self.is_visible:
            return

        for view in reversed(self.views):
            view.pre_draw()
            view.draw()
            view.post_draw()

    def post_draw(self):
        #print 'post_draw', self.name

        glPopMatrix()

    def bring_to_front(self, view):
        if view in self.views:
            self.views.remove(view)
            self.views.insert(0, view)

    def intersect(self, x, y):
        relx = x - self.x
        rely = y - self.y
        for view in self.views:
            if view.intersect(relx, rely):
                return view
        return None

    def on_drag(self, dnd_context):
        pass

    def on_drag_start(self, dnd_context):
        pass

    def on_drag_stop(self, dnd_context):
        pass

    def on_drop(self, dnd_context):
        pass


class UIHexagon(UIView):

    def __init__(self, *args, **kwargs):
        super(UIHexagon, self).__init__(*args, **kwargs)

        self.background_color = kwargs.get('background_color', (0, 0, 0))
        self.border_color = kwargs.get('border_color', (255, 255, 255))
        self.border_width = kwargs.get('border_width', 4.)
        self.hexagon = kwargs['hexagon']
        self.icon_blit = kwargs.get('icon_blit', False)
        self.icon_image = kwargs.get('icon_image', None)

        if self.icon_image:
            self.icon_image.anchor_x = self.icon_image.width
            self.icon_image.anchor_y = self.icon_image.height

        self.outer_vbo = self.make_hexagon_vbo(self.hexagon, 0.)
        self.inner_vbo = self.make_hexagon_vbo(self.hexagon, -self.border_width)
        self.icon_quad = self.make_quad_vbo(self.hexagon)

    def draw(self):
        super(UIHexagon, self).draw()

        glColor3ub(*self.border_color)
        self.outer_vbo.draw(GL_TRIANGLE_STRIP)

        glColor3ub(*self.background_color)
        self.inner_vbo.draw(GL_TRIANGLE_STRIP)

        if self.icon_image:
            glColor3f(1, 1, 1)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            if self.icon_blit:
                self.icon_image.blit(self.x, self.y, 0.)
            else:
                tex = self.icon_image.get_texture()
                glEnable(tex.target)
                glBindTexture(tex.target, tex.id)
                self.icon_quad.draw(GL_TRIANGLE_STRIP)
                glDisable(tex.target)
            glDisable(GL_BLEND)

    def intersect(self, x, y):
        self.hexagon.x = self.x
        self.hexagon.y = self.y

        if self.hexagon.intersect_point(x, y):
            return self
        else:
            return None

    @property
    def width(self):
        return self.hexagon.half_width * 2.

    @property
    def height(self):
        return self.hexagon.height * 2.

    @staticmethod
    def make_hexagon_vbo(hexagon, border):
        """Make hexagon inscribed in an ellipse"""

        # vertex layout
        #
        #   2---1
        #  /     \
        # 3       0
        #  \     /
        #   4---5

        verts = list(itertools.chain(*hexagon.get_vertices_ccw(border=border)))

        # tri strip
        return pyglet.graphics.vertex_list_indexed(
            6,
            [3, 4, 2, 5, 1, 0],
            ('v2f/static', verts))

    @staticmethod
    def make_quad_vbo(hexagon):
        """Make quad inscribed in an ellipse"""

        # vertex layout
        #
        # 1---0
        # |   |
        # 2---3

        verts = hexagon.get_vertices_ccw()
        verts = [verts[1], verts[2], verts[4], verts[5]]
        verts = list(itertools.chain(*verts))
        uvs = [
            1, 1,
            0, 1,
            0, 0,
            1, 0,
        ]

        # tri strip
        return pyglet.graphics.vertex_list_indexed(
            4,
            [1, 2, 0, 3],
            ('v2f/static', verts), ('t2f/static', uvs))


class UIRegularHexagon(UIHexagon):

    def __init__(self, *args, **kwargs):
        side_length = kwargs.get('side_length', 50.)

        kwargs['hexagon'] = hexagons.Hexagon.from_side_length(side_length)

        super(UIRegularHexagon, self).__init__(*args, **kwargs)


class UIHexagonGrid(UIView):

    def __init__(self, *args, **kwargs):
        super(UIHexagonGrid, self).__init__(*args, **kwargs)

        self.width = kwargs.get('width', 1)
        self.height = kwargs.get('height', 1)

    def draw(self):
        super(UIHexagonGrid, self).draw()
