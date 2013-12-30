import math

SIN_60 = math.sin(math.pi / 3.)
COS_60 = 0.5


def side_length_to_width(side_length):
    return side_length + 2. * COS_60 * side_length


def side_length_to_height(side_length):
    return 2. * SIN_60 * side_length


class Hexagon(object):
    """Representation of a flat-top hexagon"""

    @classmethod
    def from_side_length(cls, side_length, *args, **kwargs):
        height = 2. * SIN_60 * side_length
        top_width = side_length
        total_width = side_length + 2. * COS_60 * side_length
        return cls(height, top_width, total_width, *args, **kwargs)

    @classmethod
    def from_width_height(cls, width, height, *args, **kwargs):
        top_width = width * SIN_60
        total_width = width
        return cls(height, top_width, total_width, *args, **kwargs)

    @classmethod
    def from_ellipse(cls, radius_horz, radius_vert, *args, **kwargs):
        height = radius_vert * SIN_60
        top_width = radius_horz
        total_width = 2. * radius_horz
        return cls(height, top_width, total_width, *args, **kwargs)

    @classmethod
    def from_circle(cls, radius, *args, **kwargs):
        return cls.from_ellipse(radius, radius, *args, **kwargs)

    def __init__(self, height, top_width, total_width, x=0., y=0.):
        self.x = x
        self.y = y
        self.half_height = height / 2.
        self.half_top_width = top_width / 2.
        self.half_width = total_width / 2.

    def intersect_point(self, x, y):
        dx = abs(x - self.x)
        dy = abs(y - self.y)
        w = self.half_width
        h = self.half_height
        return dx < w and dy < h and dy < (h * (1 - dx / w))

    def get_vertices_ccw(self, border=0):
        # vertex layout
        #
        #   2---1
        #  /     \
        # 3       0
        #  \     /
        #   4---5

        s = (self.half_width + border) / self.half_width 
        hw = self.half_width + border
        tw = self.half_top_width * s
        hh = self.half_height + border
        return [
            ( hw,  0.),
            ( tw,  hh),
            (-tw,  hh),
            (-hw,  0.),
            (-tw, -hh),
            ( tw, -hh),
        ]
