__author__ = 'cseebach'

import pyglet
from pyglet import gl

class CanvasView(pyglet.window.Window):

    def __init__(self, *args, **kwargs):
        super(CanvasView, self).__init__(*args, **kwargs)

        self.scale = kwargs.get("scale", 8)
        self.preview = None

    def set_canvas(self, canvas):
        self.canvas = canvas
        self.fit_to_canvas()

    def fit_to_canvas(self):
        new_w = self.canvas.width * self.scale
        new_h = self.canvas.height * self.scale
        self.set_size(new_w, new_h)

    def draw_canvas(self, canvas):
        texture = canvas.get_texture()
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER,
                           gl.GL_NEAREST)
        texture.width = canvas.width * self.scale
        texture.height = canvas.height * self.scale
        texture.blit(0, 0)

    def on_draw(self):
        self.clear()
        self.draw_canvas(self.canvas)
        if self.preview:
            self.draw_canvas(self.preview)

    def show_preview(self, canvas):
        self.preview = canvas

    def hide_preview(self):
        self.preview = None

class SlammerView(object):
    """
    The User Interface to the Pixel Slammer data.
    """

    def __init__(self):
        self.canvas = CanvasView(visible=False)

        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

    def push_handlers(self, handler):
        self.canvas.push_handlers(handler)