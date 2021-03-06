__author__ = 'cseebach'

from tkColorChooser import askcolor
import Tkinter

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

        self.draw_grid = True
        self.draw_borders = True

        self.highlighted_cell = None

    def set_canvas(self, canvas):
        self.canvas = canvas
        self.fit_to_canvas()
        self.tile_size = canvas.tile_size

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

    def on_mouse_motion(self, x, y, dx, dy):
        self.highlighted_cell = (x/self.scale)//self.tile_size[0], (y/self.scale)//self.tile_size[1]

    def draw_canvas(self, canvas):
        sprites, batch = canvas.get_sprites(self.scale)
        batch.draw()

        if self.highlighted_cell and self.draw_borders:
            h_x, h_y = self.highlighted_cell

            gl.glLineWidth(2.0)

            pyglet.graphics.draw(8, gl.GL_LINES,
                ("v2i", (h_x*self.scale*self.tile_size[0],
                         h_y*self.scale*self.tile_size[1],

                         h_x*self.scale*self.tile_size[0],
                         (h_y+1)*self.scale*self.tile_size[1],

                         h_x*self.scale*self.tile_size[0],
                         (h_y+1)*self.scale*self.tile_size[1],

                         (h_x+1)*self.scale*self.tile_size[0],
                         (h_y+1)*self.scale*self.tile_size[1],

                         (h_x+1)*self.scale*self.tile_size[0],
                         (h_y+1)*self.scale*self.tile_size[1],

                         (h_x+1)*self.scale*self.tile_size[0],
                         h_y*self.scale*self.tile_size[1],

                         (h_x+1)*self.scale*self.tile_size[0],
                         h_y*self.scale*self.tile_size[1],

                         h_x*self.scale*self.tile_size[0],
                         h_y*self.scale*self.tile_size[1],)),
                ("c3B", (0,0,0,255,255,255)*4))

pyglet.resource.path += ["res/normal", "res/alpha"]
pyglet.resource.reindex()

class ToolboxView(SelfRegistrant):
    """
    A window that holds all the tools in the toolbox.
    """

    dispatches = ["on_tool_selected", "on_scale_changed", "on_color_selected",
                  "on_bg_color_selected"]

    tool_icons = ["pencil.png", "eraser.png", "killeraser.png", "line.png",
                  "rectangle.png", "hollowrectangle.png", "circle.png",
                  "hollowcircle.png", "eyedropper.png", "tileplacer.png",
                  "fillbucket.png", "localreplace.png", "globalreplace.png",
                  "animation.png"]
    tool_alpha = [pyglet.resource.image("res/alpha/"+loc) for loc in tool_icons]
    tool_icons = [pyglet.resource.image("res/normal/"+loc) for loc in tool_icons]
    tool_w, tool_h = 32, 32
    tool_loc = [((tool_w+1) * i, 40) for i, icon in enumerate(tool_icons)]
    tools = zip(range(len(tool_icons)), tool_loc, tool_icons)

    highlight = pyglet.resource.image("res/highlight.png")

    swatch_w, swatch_h = 16, 16
    swatch_loc = [(66 + 17 * i, 0) for i in xrange(20)]
    swatch2_loc = [(66 + 17 * i, 17) for i in xrange(20)]

    arrow_w, arrow_h = 24, 24
    minus_loc = 17*20+65, 0
    minus = pyglet.resource.image("res/minus.png")
    plus_loc = minus_loc[0] + arrow_w + 1, minus_loc[1]
    plus = pyglet.resource.image("res/plus.png")

    tk_root = Tkinter.Tk()
    tk_root.iconify()

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("width", self.tool_loc[-1][0]+60)
        kwargs.setdefault("height", 72)
        super(ToolboxView, self).__init__(*args, **kwargs)

        self.highlighted = None

        self.palette = None

        self.left_tool = 0
        self.left_color = (0, 0, 0)

        self.right_tool = 0
        self.right_color = (128, 128, 128)

        self.background_color = (0, 0, 0)

        self.scale = 8

    def on_expose(self):
    #need an empty method here to have pyglet redraw on unhide
        pass

    def on_mouse_motion(self, x, y, dx, dy):
        for i, t_point, _ in self.tools:
            t_x, t_y = t_point
            if t_x <= x < t_x + self.tool_w:
                if t_y <= y < t_y + self.tool_h:
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
            swatch, index = self.get_palette_swatch(x, y)
            if pyglet.window.key.MOD_CTRL & modifers:
                self.palette[index] = askcolor()[0] or self.palette[index]
            elif pyglet.window.mouse.LEFT & buttons:
                self.dispatch_event("on_color_selected", swatch,
                                    "left")
                self.left_color = swatch
            else:
                self.dispatch_event("on_color_selected", swatch,
                                    "right")
                self.right_color = swatch
        elif self.scale_increased(x, y):
            self.scale += 1
            self.dispatch_event("on_scale_changed", self.scale)
        elif self.scale_decreased(x ,y):
            self.scale = max(1, self.scale - 1)
            self.dispatch_event("on_scale_changed", self.scale)
        elif x > self.tool_loc[-1][0] and y > self.tool_loc[-1][1]:
            new_bg_color = askcolor()[0]
            if new_bg_color:
                self.background_color = new_bg_color
                self.dispatch_event("on_bg_color_selected", new_bg_color)

    def scale_decreased(self, x, y):
        if self.minus_loc[0] < x < self.minus_loc[0] + self.arrow_w:
            if self.minus_loc[1] < y < self.minus_loc[1] + self.arrow_h:
                return True

    def scale_increased(self, x, y):
        if self.plus_loc[0] < x < self.plus_loc[0] + self.arrow_w:
            if self.plus_loc[1] < y < self.plus_loc[1] + self.arrow_h:
                return True

    def over_palette_swatch(self, x, y):
        for sw_x, sw_y in self.swatch_loc:
            if sw_x < x < sw_x + self.swatch_w:
                if sw_y < y < sw_y + self.swatch_h:
                    return True
        for sw_x, sw_y in self.swatch2_loc:
            if sw_x < x < sw_x + self.swatch_w:
                if sw_y < y < sw_y + self.swatch_h:
                    return True

    def get_palette_swatch(self, x, y):
        sw_x, sw_y = (x - 66) // 17, y // 17
        return self.palette[sw_x * 2 + sw_y], sw_x * 2 + sw_y

    def set_palette(self, palette):
        self.palette = palette

    def draw_palette(self):
        pyglet.graphics.draw(4, gl.GL_QUADS,
            ("v2i", (0, 0, 0, 33, 32, 33, 32, 0)),
            ("c3B", self.left_color*4))
        pyglet.graphics.draw(4, gl.GL_QUADS,
            ("v2i", (33, 0, 33, 33, 65, 33, 65, 0)),
            ("c3B", self.right_color*4))

        if self.palette:
            swatches = []
            for x, y in self.swatch_loc:
                swatches.extend((x, y, x, y+16, x+16, y+16, x+16, y))
            for x, y in self.swatch2_loc:
                swatches.extend((x, y, x, y+16, x+16, y+16, x+16, y))

            sw_color = []
            for color in self.palette[::2]:
                sw_color.extend(color*4)
            for color in self.palette[1::2]:
                sw_color.extend(color*4)

            pyglet.graphics.draw(4*len(self.palette), gl.GL_QUADS,
                ("v2i", swatches),
                ("c3B", sw_color))

        x, y = self.tool_loc[-1][0]+35, self.tool_loc[-1][1]
        pyglet.graphics.draw(4, gl.GL_QUADS,
            ("v2i", (x, y, x, y+32, x+32, y+32, x+32, y)),
            ("c3B", self.background_color*4))

        gl.glColor3ub(255,255,255)

    def on_draw(self):
        pyglet.gl.glClearColor(.25,.25,.25,1.0)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        self.clear()
        for i, location, icon in self.tools:
            icon.blit(*location)
            if self.highlighted == i:
                self.highlight.blit(*location)
        self.minus.blit(*self.minus_loc)
        self.plus.blit(*self.plus_loc)

        self.draw_palette()

        self.tool_alpha[self.left_tool].blit(0, 0)
        self.tool_alpha[self.right_tool].blit(33, 0)

class TilesetManagerView(SelfRegistrant):

    tile_select = pyglet.resource.image("res/tileselect.png")
    tile_delete = pyglet.resource.image("res/tiledelete.png")
    tile_number = pyglet.resource.image("res/tilenumber.png")
    minus = pyglet.resource.image("res/minus.png")
    plus = pyglet.resource.image("res/plus.png")

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