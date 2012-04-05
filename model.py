__author__ = 'cseebach'

from random import randint

import pyglet

class Tile(pyglet.image.ImageData):

    format = "RGBA"

    def __init__(self, tile_size):
        data = []
        for pix_num in xrange(tile_size[0] * tile_size[1]):
            data.append(chr(randint(0,255))+chr(randint(0,255))+chr(randint(0,255))+"\xff")
        super(Tile, self).__init__(tile_size[0], tile_size[1], self.format, "".join(data))

        self.drawn_on = False

    def set_pixel(self, x, y, color):
        pitch =  self.width * len(self.format)
        data = list(self.get_data(self.format, pitch))
        offset = pitch * y + len(self.format) * x
        data[offset:offset+len(self.format)] = [chr(c) for c in color]
        self.set_data(self.format, pitch, "".join(data))

class Canvas(object):
    """
    Represents a paintable canvas composed of individual tiles.
    """

    def __init__(self, tile_size, canvas_size):
        self.tile_size = tile_size
        self.canvas_size = canvas_size

        self.array = []
        for y in xrange(canvas_size[1]):
            self.array.append([])
            for x in xrange(canvas_size[0]):
                self.array[y].append(Tile(tile_size))

    def get_tile(self, x, y):
        return self.array[y][x]

    def get_size(self):
        return self.canvas_size

    def get_tile_size(self):
        return self.tile_size

class Palette(object):
    pass

class SlammerModel(object):
    """
    Contains the data for the Pixel Slammer application.
    """

    def __init__(self, tile_size=(16,16), canvas_size=(4,4)):
        self.canvas = Canvas(tile_size, canvas_size)
        self.init_palette()

    def init_palette(self):
        pass

    def get_canvas(self):
        return self.canvas


