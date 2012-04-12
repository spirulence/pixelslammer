__author__ = 'cseebach'

import ctypes

import pyglet

def must_flush(to_wrap):
    def wrapped(self, *args, **kwargs):
        if self.dirty:
            self.flush_changes()
        return to_wrap(self, *args, **kwargs)
    return wrapped

class Tile(pyglet.image.ImageData):
    """
    Represents a drawing surface with pixel access.
    """

    def __init__(self, width, height, data=None):
        #noinspection PyCallingNonCallable,PyTypeChecker
        self.ctypes_data = (ctypes.c_ubyte * (width * height * 4))()
        if data:
            self.ctypes_data[:] = data
        super(Tile, self).__init__(width, height, "RGBA", ctypes.pointer(self.ctypes_data))
        self.dirty = False

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
        self.dirty = True

    def flush_changes(self):
        """
        Changes made with set_pixel are not actually seen until this method is called.
        """
        self.set_data("RGBA", self.width * 4, ctypes.pointer(self.ctypes_data))

    @must_flush
    def blit_to_texture(self, target, level, x, y, z, internalformat=None):
        super(Tile, self).blit_to_texture(target, level, x, y, z, internalformat)

    @must_flush
    def blit_into(self, source, x, y, z):
        super(Tile, self).blit_into(source, x, y, z)

    @must_flush
    def get_mipmapped_texture(self):
        return super(Tile, self).get_mipmapped_texture()

    @must_flush
    def blit(self, x, y, z=0, width=None, height=None):
        super(Tile, self).blit(x, y, z, width, height)

    @must_flush
    def create_texture(self, cls, rectangle=False, force_rectangle=False):
        return super(Tile, self).create_texture(cls, rectangle, force_rectangle)

    @must_flush
    def get_data(self, format, pitch):
        return super(Tile, self).get_data(format, pitch)

    @must_flush
    def get_image_data(self):
        return super(Tile, self).get_image_data()

    @must_flush
    def get_texture(self, rectangle=False, force_rectangle=False):
        return super(Tile, self).get_texture(rectangle, force_rectangle)

    @must_flush
    def get_region(self, x, y, width, height):
        return super(Tile, self).get_region(x, y, width, height)

    def copy(self):
        return Tile(self.width, self.height, data=self.ctypes_data)

    def save(self, *args, **kwargs):
        self.set_data("RGBA", self.width * 4, "".join(chr(i) for i in self.ctypes_data))
        super(Tile, self).save(*args, **kwargs)
        self.flush_changes()

    def erase(self):
        for i in xrange(len(self.ctypes_data)):
            self.ctypes_data[i] = 0
        self.dirty = True

class Canvas(object):

    def __init__(self, tile_size, canvas_size, copy_from=None):
        self.tile_size = tile_size
        self.canvas_size = canvas_size
        width, height = (tile_size[0]*canvas_size[0],
                         tile_size[1]*canvas_size[1])
        self.width, self.height = width, height

        self.tiles = []
        for y in xrange(canvas_size[1]):
            self.tiles.append([])
            for x in xrange(canvas_size[0]):
                if copy_from:
                    tile = copy_from.tiles[y][x].copy()
                else:
                    tile = Tile(tile_size[0], tile_size[1])
                self.tiles[y].append(tile)

    def set_pixel(self, x, y, color):
        tile_x, tile_y = x // self.tile_size[0], y // self.tile_size[1]
        pix_x, pix_y = x % self.tile_size[0], y % self.tile_size[1]

        self.tiles[tile_y][tile_x].set_pixel(pix_x, pix_y, color)

    def get_pixel(self, x, y):
        tile_x, tile_y = x // self.tile_size[0], y // self.tile_size[1]
        pix_x, pix_y = x % self.tile_size[0], y % self.tile_size[1]

        return self.tiles[tile_y][tile_x].get_pixel(pix_x, pix_y)

    def copy(self):
        return Canvas(self.tile_size, self.canvas_size, copy_from=self)

    def get_texture(self):
        texture = pyglet.image.Texture.create(self.tile_size[0]*self.canvas_size[0],
                                              self.tile_size[1]*self.canvas_size[1])
        for y in xrange(self.canvas_size[1]):
            for x in xrange(self.canvas_size[0]):
                texture.blit_into(self.tiles[y][x], x*self.tile_size[0],
                                  y*self.tile_size[1], 0)
        return texture

    def get_tile(self, x, y):
        return x // self.tile_size[0], y // self.tile_size[1]

class SlammerModel(object):
    """
    Contains the data for the Pixel Slammer application.
    """

    def __init__(self, tile_size=(16,16), canvas_size=(4,4), canvas=None):
        self.canvas = canvas or Canvas(tile_size, canvas_size)

    def copy(self):
        return SlammerModel(None, None, canvas=self.canvas.copy())
