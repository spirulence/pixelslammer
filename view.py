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

    dispatches = ["on_canvas_press", "on_canvas_drag", "on_canvas_release",
                  "on_canvas_draw"]

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

    def on_expose(self):
        #need an empty method here to have pyglet redraw on unhide
        pass

    def on_draw(self):
        self.dispatch_event("on_canvas_draw")

    def on_mouse_press(self, x, y, buttons, modifiers):
        self.dispatch_event("on_canvas_press", x, y, buttons, modifiers)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.dispatch_event("on_canvas_drag", x, y, dx, dy, buttons, modifiers)

    def on_mouse_release(self, x, y, buttons, modifiers):
        self.dispatch_event("on_canvas_release", x, y, buttons, modifiers)

    def draw_canvas(self, canvas):
        texture = canvas.get_texture()
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER,
                           gl.GL_NEAREST)
        texture.width = canvas.width * self.scale
        texture.height = canvas.height * self.scale
        texture.blit(0, 0)

class ToolboxView(pyglet.window.Window):
    """
    A window that holds all the tools in the toolbox.
    """


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