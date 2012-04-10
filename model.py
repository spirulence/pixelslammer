__author__ = 'cseebach'

import pickle
import ctypes

import pyglet
from pyglet import gl

class Tile(pyglet.image.ImageData):
    """
    Represents a drawing surface with pixel access.
    """

    # TODO autoflush changes on any access that requires it

    def __init__(self, width, height):
        #noinspection PyCallingNonCallable,PyTypeChecker
        self.ctypes_data = (ctypes.c_ubyte * (width * height * 4))()
        super(Tile, self).__init__(width, height, "RGBA", ctypes.pointer(self.ctypes_data))

    def get_pixel(self, x, y):
        """
        Get a pixel, as a sequence of 4 color components in RGBA order.

        Each color component is between 0 and 255.
        """
        pitch = self.width * 4
        offset = (y * pitch) + x * 4
        return self.ctypes_data[offset:offset+4]

    def set_pixel(self, x, y, color):
        """
        Set a pixel from a sequence of 4 color components in RGBA order.

        Each color component must be between 0 and 255.
        """
        pitch = self.width * 4
        offset = (y * pitch) + x * 4
        self.ctypes_data[offset:offset+4] = color

    def flush_changes(self):
        """
        Changes made with set_pixel are not actually seen until this method is called.
        """
        self.set_data("RGBA", self.width * 4, ctypes.pointer(self.ctypes_data))

    def copy(self):
        t = Tile(self.width, self.height)
        t.ctypes_data[:] = self.ctypes_data
        return t

    def save(self, *args, **kwargs):
        self.set_data("RGBA", self.width * 4, "".join(chr(i) for i in self.ctypes_data))
        super(Tile, self).save(*args, **kwargs)
        self.flush_changes()

class Canvas(object):

    def __init__(self, tile_size, canvas_size):
        self.tile_size = tile_size
        self.canvas_size = canvas_size
        width, height = (tile_size[0]*canvas_size[0],
                         tile_size[1]*canvas_size[1])
        self.tile = Tile(width, height)
        self.width, self.height = width, height

    def set_pixel(self, x, y, color):
        self.tile.set_pixel(x, y, color)

    def get_pixel(self, x, y):
        return self.tile.get_pixel(x, y)

    def flush_changes(self):
        self.tile.flush_changes()

    def copy(self):
        c = Canvas(self.tile_size, self.canvas_size)
        c.tile.ctypes_data[:] = self.tile.ctypes_data
        return c

    def get_texture(self):
        return self.tile.get_texture()

    def blit(self, x, y):
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        self.tile.blit(x, y)

class SlammerModel(object):
    """
    Contains the data for the Pixel Slammer application.
    """

    def __init__(self, tile_size=(16,16), canvas_size=(4,4), canvas=None):
        self.canvas = canvas or Canvas(tile_size, canvas_size)

    def copy(self):
        return SlammerModel(None, None, canvas=self.canvas.copy())
