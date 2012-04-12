__author__ = 'cseebach'

import ctypes

import pyglet

def must_flush(to_wrap):
    def wrapped(self, *args, **kwargs):
        if self.dirty:
            self.flush_changes()
        return to_wrap(self, *args, **kwargs)
    return wrapped

class PixelArea(pyglet.image.ImageData):
    """
    Represents a drawing surface with pixel access.
    """

    def __init__(self, width, height, data=None):
        #noinspection PyCallingNonCallable,PyTypeChecker
        self.ctypes_data = (ctypes.c_ubyte * (width * height * 4))()
        if data:
            self.ctypes_data[:] = data
        super(PixelArea, self).__init__(width, height, "RGBA",
                                        ctypes.pointer(self.ctypes_data))
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
        Changes made with set_pixel are not actually seen until this method is
        called.
        """
        self.set_data("RGBA", self.width * 4, ctypes.pointer(self.ctypes_data))

    @must_flush
    def blit_to_texture(self, target, level, x, y, z, internalformat=None):
        super(PixelArea, self).blit_to_texture(target, level, x, y, z, internalformat)

    @must_flush
    def blit_into(self, source, x, y, z):
        super(PixelArea, self).blit_into(source, x, y, z)

    @must_flush
    def get_mipmapped_texture(self):
        return super(PixelArea, self).get_mipmapped_texture()

    @must_flush
    def blit(self, x, y, z=0, width=None, height=None):
        super(PixelArea, self).blit(x, y, z, width, height)

    @must_flush
    def create_texture(self, cls, rectangle=False, force_rectangle=False):
        return super(PixelArea, self).create_texture(cls, rectangle, force_rectangle)

    @must_flush
    def get_data(self, format, pitch):
        return super(PixelArea, self).get_data(format, pitch)

    @must_flush
    def get_image_data(self):
        return super(PixelArea, self).get_image_data()

    @must_flush
    def get_texture(self, rectangle=False, force_rectangle=False):
        return super(PixelArea, self).get_texture(rectangle, force_rectangle)

    @must_flush
    def get_region(self, x, y, width, height):
        return super(PixelArea, self).get_region(x, y, width, height)

    def copy(self):
        return PixelArea(self.width, self.height, data=self.ctypes_data)

    def save(self, *args, **kwargs):
        self.set_data("RGBA", self.width * 4, "".join(chr(i) for i in self.ctypes_data))
        super(PixelArea, self).save(*args, **kwargs)
        self.flush_changes()

    def erase(self):
        for i in xrange(len(self.ctypes_data)):
            self.ctypes_data[i] = 0
        self.dirty = True

class Tile(object):

    def __init__(self, width, height):
        self.pixel_area = PixelArea(width, height)
        self.rotation = 0
        self.flip_x = False
        self.flip_y = False

    def flip_x(self):
        self.flip_x = not self.flip_x

    def flip_y(self):
        self.flip_y = not self.flip_y

    def transform_coords(self, x, y):
        if self.flip_x:
            x = self.pixel_area.width - x
        if self.flip_y:
            y = self.pixel_area.height - y

        to_rotate = self.rotation
        while to_rotate > 0:
            x, y = y, x
            y = -y
            y += self.pixel_area.height
            to_rotate -= 90

        return x, y

    def set_pixel(self, x, y, color):
        real_x, real_y = self.transform_coords(x, y)
        self.pixel_area.set_pixel(real_x, real_y, color)

    def get_pixel(self, x, y):
        return self.pixel_area.get_pixel(*self.transform_coords(x, y))

    def get_texture(self):
        texture = self.pixel_area.get_texture()
        return texture.get_transform(flip_x=self.flip_x, flip_y=self.flip_y,
                                     rotate=self.rotation)

class TileCanvas(object):

    def __init__(self, tile_size, canvas_size, tiles_list):
        self.tile_size = tile_size
        self.canvas_size = canvas_size
        width, height = (tile_size[0]*canvas_size[0],
                         tile_size[1]*canvas_size[1])
        self.width, self.height = width, height

        self.tiles_list = tiles_list

        self.tiles = []
        for y in xrange(canvas_size[1]):
            self.tiles.append([])
            for x in xrange(canvas_size[0]):
                self.tiles[y].append(None)

    def set_pixel(self, x, y, color):
        tile_x, tile_y = x // self.tile_size[0], y // self.tile_size[1]
        pix_x, pix_y = x % self.tile_size[0], y % self.tile_size[1]

        tile = self.tiles[tile_y][tile_x]
        if not tile:
            tile = Tile(*self.tile_size)
            self.tiles_list.append(tile)
            self.tiles[tile_y][tile_x] = tile

        tile.set_pixel(pix_x, pix_y, color)

    def get_pixel(self, x, y):
        tile_x, tile_y = x // self.tile_size[0], y // self.tile_size[1]
        pix_x, pix_y = x % self.tile_size[0], y % self.tile_size[1]

        tile = self.tiles[tile_y][tile_x]
        if tile:
            return tile.get_pixel(pix_x, pix_y)
        else:
            return 0, 0, 0, 0

    def get_texture(self):
        texture = pyglet.image.Texture.create(self.tile_size[0]*self.canvas_size[0],
                                              self.tile_size[1]*self.canvas_size[1])
        for y in xrange(self.canvas_size[1]):
            for x in xrange(self.canvas_size[0]):
                tile = self.tiles[y][x]
                if tile:
                    tile_texture = tile.get_texture().get_image_data()
                    print tile_texture
                    tile_texture.blit_to_texture(texture, 0, x*self.tile_size[0],
                                                 y*self.tile_size[1], 0)
        return texture

    def get_tile(self, x, y):
        return x // self.tile_size[0], y // self.tile_size[1]

class SlammerModel(object):
    """
    Contains the data for the Pixel Slammer application.
    """

    def __init__(self, tile_size=(16,16), canvas_size=(4,4), copy=False):
        if not copy:
            self.tiles = []
            self.canvas = TileCanvas(tile_size, canvas_size, self.tiles)

    def copy(self):
        copy = SlammerModel(None, None, copy=True)

