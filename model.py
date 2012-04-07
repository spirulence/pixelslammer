__author__ = 'cseebach'

import pickle
import ctypes

import pyglet

def canvas_unpickler(tile_size, canvas_size, data):
    c = Canvas(tile_size, canvas_size)
    c.ctypes_data[:] = data
    return c

class Canvas(pyglet.image.ImageData):
    """
    Represents a paintable canvas composed of individual tiles.
    """

    def __init__(self, tile_size, canvas_size):
        self.tile_size = tile_size
        self.canvas_size = canvas_size

        width = tile_size[0] * canvas_size[0]
        height = tile_size[1] * canvas_size[1]
        #noinspection PyTypeChecker
        self.ctypes_type = ctypes.c_ubyte * (width * height * 4)
        #noinspection PyCallingNonCallable
        self.ctypes_data = self.ctypes_type()
        super(Canvas, self).__init__(width, height, "RGBA", ctypes.pointer(self.ctypes_data))

    def set_pixel(self, x, y, color):
        pitch = self.width * 4
        offset = (y * pitch) + x * 4
        self.ctypes_data[offset:offset+4] = color
        self.set_data("RGBA", pitch, ctypes.pointer(self.ctypes_data))

    def __reduce__(self):
        return canvas_unpickler, (self.tile_size, self.canvas_size, list(self.ctypes_data))

class SlammerModel(object):
    """
    Contains the data for the Pixel Slammer application.
    """

    def __init__(self, tile_size=(16,16), canvas_size=(4,4)):
        self.canvas = Canvas(tile_size, canvas_size)

    def copy(self):
        return pickle.loads(pickle.dumps(self))
