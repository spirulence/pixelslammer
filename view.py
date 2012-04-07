__author__ = 'cseebach'

import pyglet
from pyglet import gl

class SelfRegistrant(pyglet.window.Window):

    dispatches = []

    def __init__(self, *args, **kwargs):
        super(SelfRegistrant, self).__init__(*args, **kwargs)

        for event_type in self.dispatches:
            self.register_event_type(event_type)

class CanvasView(SelfRegistrant):

    dispatches = ["on_canvas_press", "on_canvas_drag", "on_canvas_release"]

    def __init__(self, *args, **kwargs):
        super(CanvasView, self).__init__(*args, **kwargs)

        self.scale = kwargs.get("scale", 6)

    def set_canvas(self, canvas):
        self.canvas = canvas
        self.fit_to_canvas()

    def fit_to_canvas(self):
        canvas_w, canvas_h = self.canvas.get_size()
        tile_w, tile_h = self.canvas.get_tile_size()
        new_w = canvas_w * tile_w * self.scale
        new_h = canvas_h * tile_h * self.scale
        self.set_size(new_w, new_h)

    def on_draw(self):
        self.clear()

        canvas_w, canvas_h = self.canvas.get_size()
        tile_w, tile_h = self.canvas.get_tile_size()
        scaled_w, scaled_h = tile_w * self.scale, tile_h * self.scale

        for y in xrange(canvas_h):
            for x in xrange(canvas_w):
                texture = self.canvas.get_tile(x,y).get_texture()
                gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER,
                                   gl.GL_NEAREST)
                texture.width = scaled_w
                texture.height = scaled_h
                texture.blit(x * scaled_w, y * scaled_h)

    def on_mouse_press(self, x, y, buttons, modifiers):
        window_w, window_h = self.get_size()
        x_ratio = float(x)/window_w
        y_ratio = float(y)/window_h
        self.dispatch_event("on_canvas_press", x_ratio, y_ratio, buttons,
                            modifiers)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        window_w, window_h = self.get_size()
        start_x = float(x - dx)/window_w
        start_y = float(y - dy)/window_h
        end_x = float(x)/window_w
        end_y = float(y)/window_h
        self.dispatch_event("on_canvas_drag", start_x, start_y, end_x, end_y,
                            buttons, modifiers)

    def on_mouse_release(self, x, y, buttons, modifiers):
        window_w, window_h = self.get_size()
        x_ratio = float(x)/window_w
        y_ratio = float(y)/window_h
        self.dispatch_event("on_canvas_release", x_ratio, y_ratio, buttons,
                            modifiers)

class SlammerView(object):
    """
    The User Interface to the Pixel Slammer data.
    """

    def __init__(self):
        self.canvas = CanvasView()

        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

    def push_handlers(self, handler):
        self.canvas.push_handlers(handler)