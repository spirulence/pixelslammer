__author__ = 'cseebach'

import pyglet

class Tile(pyglet.image.ImageData):

    format = "RGBA"

    def __init__(self, tile_size):
        data = "\0" * (len(self.format) * tile_size[0] * tile_size[1])
        super(Tile, self).__init__(self, tile_size[0], tile_size[1], self.format, data)

        self.drawn_on = False

class Canvas(object):
    """
    Represents a paintable canvas composed of individual tiles.
    """

    def __init__(self, tile_size, canvas_size):
        self.tile_size = tile_size
        self.canvas_size = canvas_size

        self.array = []
        for y in canvas_size[1]:
            self.array.append([])
            for x in canvas_size[0]:
                self.array[y].append(Tile(tile_size))

    def get_tile(self, x, y):
        return self.array[y][x]

    def get_dimensions(self):
        return self.canvas_size

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


