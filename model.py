__author__ = 'cseebach'

from random import randint
import pickle

import pyglet

class Canvas(pyglet.image.ImageData):
    """
    Represents a paintable canvas composed of individual tiles.
    """

    input_color_format = "RGBA"

    def __init__(self, tile_size, canvas_size):
        self.tile_size = tile_size
        self.canvas_size = canvas_size

        width = tile_size[0] * canvas_size[0]
        height = tile_size[1] * canvas_size[1]
        data = "\x00\x00\x00\x00" * (width * height)
        super(Canvas, self).__init__(width, height, "RGBA", data)

    def set_pixel(self, x, y, color):
        cur_pitch = self.pitch
        cur_format = self.format
        format_len = len(cur_format)
        data = list(self.get_data(cur_format, cur_pitch))

        c_dict = dict(zip(self.input_color_format, color))
        new_pixel = [chr(c_dict[c]) for c in cur_format]

        offset = cur_pitch * y + format_len * x
        data[offset:offset+format_len] = new_pixel
        self.set_data(cur_format, cur_pitch, "".join(data))

class SlammerModel(object):
    """
    Contains the data for the Pixel Slammer application.
    """

    def __init__(self, tile_size=(16,16), canvas_size=(4,4)):
        self.canvas = Canvas(tile_size, canvas_size)

    def copy(self):
        return pickle.loads(pickle.dumps(self))
