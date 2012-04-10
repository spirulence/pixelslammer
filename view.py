__author__ = 'cseebach'

import os.path

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

pyglet.resource.path += ["res/normal", "res/alpha"]
pyglet.resource.reindex()

class ToolboxView(SelfRegistrant):
    """
    A window that holds all the tools in the toolbox.
    """

    dispatches = ["on_tool_selected", "on_scale_changed", "on_color_selected"]

    tool_icons = ["pencil.png", "eraser.png", "killeraser.png", "line.png",
                  "circle.png", "hollowcircle.png", "rectangle.png",
                  "hollowrectangle.png", "tileplacer.png", "localreplace.png",
                  "globalreplace.png", "animation.png"]
    tool_alpha = [pyglet.resource.image("res/alpha/"+loc) for loc in tool_icons]
    tool_icons = [pyglet.resource.image("res/normal/"+loc) for loc in tool_icons]
    tool_w, tool_h = 32, 32
    tool_loc = [((tool_w+1) * i, 40) for i, icon in enumerate(tool_icons)]
    tools = zip(range(len(tool_icons)), tool_loc, tool_icons)

    highlight = pyglet.resource.image("res/highlight.png")

    arrow_w, arrow_h = 24, 24
    left_arrow_loc = (tool_w+1)*len(tool_loc)+5, 0
    left_arrow = pyglet.resource.image("res/leftarrow.png")
    right_arrow_loc = left_arrow_loc[0] + arrow_w + 1, left_arrow_loc[1]
    right_arrow = pyglet.resource.image("res/rightarrow.png")

    def __init__(self, *args, **kwargs):
        super(ToolboxView, self).__init__(*args, **kwargs)

        self.highlighted = None

        self.left_tool = 0
        self.left_color = (0, 128, 0)

        self.right_tool = 0
        self.right_color = (128, 0, 0)

    def on_expose(self):
    #need an empty method here to have pyglet redraw on unhide
        pass

    def on_mouse_motion(self, x, y, dx, dy):
        for i, t_point, _ in self.tools:
            t_x, t_y = t_point
            if x >= t_x and x < t_x + self.tool_w:
                if y >= t_y and y < t_y + self.tool_h:
                    self.highlighted = i
                    break
        else:
            self.highlighted = None

    def on_mouse_release(self, x, y, buttons, modifers):
        if self.highlighted is not None:
            if pyglet.window.mouse.LEFT & buttons:
                self.dispatch_event("on_tool_selected", self.highlighted,
                                    "left")
                self.left_tool = self.highlighted
            else:
                self.dispatch_event("on_tool_selected", self.highlighted,
                                    "right")
                self.right_tool = self.highlighted
        elif self.over_palette_swatch(x, y):
            swatch = self.get_palette_swatch(x, y)
            if pyglet.window.mouse.LEFT & buttons:
                self.dispatch_event("on_color_selected", swatch.color,
                                    "left")
                self.left_color = swatch.color
            else:
                self.dispatch_event("on_color_selected", swatch.color,
                                    "right")
                self.right_color = swatch.color


    def draw_palette(self):
        pyglet.graphics.draw(4, gl.GL_QUADS,
            ("v2i", (0, 0, 0, 32, 32, 32, 32, 0)),
            ("c3B", self.left_color*4))
        pyglet.graphics.draw(4, gl.GL_QUADS,
            ("v2i", (33, 0, 33, 32, 65, 32, 65, 0)),
            ("c3B", self.right_color*4))



        gl.glColor4ub(255,255,255,255)

    def on_draw(self):
        self.clear()
        for i, location, icon in self.tools:
            icon.blit(*location)
            if self.highlighted == i:
                self.highlight.blit(*location)
        self.left_arrow.blit(*self.left_arrow_loc)
        self.right_arrow.blit(*self.right_arrow_loc)

        self.draw_palette()

        self.tool_alpha[self.left_tool].blit(0, 0)
        self.tool_alpha[self.right_tool].blit(33, 0)


class SlammerView(object):
    """
    The User Interface to the Pixel Slammer data.
    """

    def __init__(self):
        self.canvas = CanvasView(visible=False)
        self.toolbox = ToolboxView(visible=False)

        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

    def push_handlers(self, handler):
        self.canvas.push_handlers(handler)
        self.toolbox.push_handlers(handler)