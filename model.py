__author__ = 'cseebach'

import pickle
import ctypes

import pyglet

def tile_unpickler(width, height, data):
    t = Tile(width, height)
    t.ctypes_data[:] = data
    return t


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

    #noinspection PyMethodOverriding
    def __reduce__(self):
        return tile_unpickler, (self.width, self.height, list(self.ctypes_data))

    def copy(self):
        t = Tile(self.width, self.height)
        t.ctypes_data[:] = self.ctypes_data
        return t

class SlammerModel(object):
    """
    Contains the data for the Pixel Slammer application.
    """

    def __init__(self, tile_size=(16,16), canvas_size=(4,4)):
        self.canvas = Tile(tile_size[0]*canvas_size[0],
                           tile_size[1]*canvas_size[1])

    def copy(self):
        return pickle.loads(pickle.dumps(self))
