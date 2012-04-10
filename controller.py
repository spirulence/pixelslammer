from collections import defaultdict
import math

import pyglet
import pyglet.window.key as keys

__author__ = 'cseebach'

class Tool(object):
    """
    A base class for each kind of tool available in Pixel Slammer.

    The Tool workflow:
        Create the tool you want to use.

        Send it input until the input accepting methods return an object that
        evaluates to False. Alternatively, check is_ready to determine when
        enough input has been sent.

        Call the do() method of the created tool. This can be done multiple
        times if you like. (Handy for undo/redo functionality)
    """

    def __init__(self, color):
        """Create a new Tool, and give it the color it should apply."""
        self.color = color
        self._is_ready = False

    def accept_press(self, x, y):
        """
        Send a mouse press to this tool. Returns the result of is_ready after this
        call is executed.
        """
        self._accept_press(x, y)
        return self.is_ready()

    def _accept_press(self, x, y):
        """
        Where the actual work of accepting the press information is done.
        """

    def accept_drag(self, start_x, start_y, end_x, end_y):
        """
        Send a mouse drag to this tool. Returns the result of is_ready after this
        call is executed.
        """
        self._accept_drag(start_x, start_y, end_x, end_y)
        return self.is_ready()

    def _accept_drag(self, start_x, start_y, end_x, end_y):
        """
        Where the actual work of accepting drag information is done.
        """

    def accept_release(self, x, y):
        """
        Send a mouse release to this tool. Returns the result of is_ready after this
        call is executed.
        """
        self._accept_release(x, y)
        return self.is_ready()

    def _accept_release(self, x, y):
        """
        Where the actual work of accepting releases is done.
        """

    def is_ready(self):
        """
        Returns True if this tool does not need any more information to form a
        complete call.
        """
        return self._is_ready

    def do(self, canvas):
        """
        Run the tool, with the information it has recieved so far, on the given canvas.
        """

def plot(canvas, x, y, color):
    """
    Change the color of a single pixel on the model's canvas.
    """
    if x<0 or y<0 or x>=canvas.width or y>=canvas.height:
        return
    canvas.set_pixel(x, y, color)

def raster_line(start_x, start_y, end_x, end_y):
    """
    Return a list of the coordinates that make up a line.

    Implements the Bresenham line algorithm.
    """
    steep = abs(end_y - start_y) > abs(end_x - start_x)
    if steep:
        start_x, start_y = start_y, start_x
        end_x, end_y = end_y, end_x
    if start_x > end_x:
        start_x, end_x = end_x, start_x
        start_y, end_y = end_y, start_y
    delta_x = end_x -start_x
    delta_y = abs(end_y - start_y)
    error = delta_x / 2
    y = start_y
    if start_y < end_y:
        y_step = 1
    else:
        y_step = -1

    to_plot = []
    for x in xrange(start_x, end_x+1):
        if steep:
            to_plot.append((y, x))
        else:
            to_plot.append((x, y))
        error -= delta_y
        if error < 0:
            y += y_step
            error += delta_x

    return to_plot

class Pencil(Tool):
    """
    A class for drawing simple lines and points on the canvas.
    """

    def __init__(self, color):
        super(Pencil, self).__init__(color)
        self.to_plot = set()

    def _accept_press(self, x, y):
        self.to_plot.add((x,y))

    def _accept_drag(self, start_x, start_y, end_x, end_y):
        self.to_plot.update(raster_line(start_x, start_y, end_x, end_y))

    def _accept_release(self, x, y):
        self.to_plot.add((x,y))
        self._is_ready = True

    def do(self, canvas):
        for x, y in self.to_plot:
            plot(canvas, x, y, self.color)

class Eraser(Pencil):
    """
    Erase some pixels.
    """

    #noinspection PyUnusedLocal
    def __init__(self, color):
        super(Eraser, self).__init__((0,0,0,0))

class DragTool(Tool):
    """
    A tool that accepts only one click, drag, and release before becoming
    ready.
    """

    def __init__(self, color):
        super(DragTool, self).__init__(color)
        self.start_x, self.start_y = None, None
        self.end_x, self.end_y = None, None

    def _accept_press(self, x, y):
        self.start_x, self.start_y = x, y

    def _accept_drag(self, start_x, start_y, end_x, end_y):
        self.end_x, self.end_y = end_x, end_y

    def _accept_release(self, x, y):
        self.end_x, self.end_y = x, y
        self._is_ready = True

class Line(DragTool):
    """
    Draw a line.
    """

    def do(self, canvas):
        if self.start_x is not None and self.end_x is not None:
            for x, y in raster_line(self.start_x, self.start_y, self.end_x,
                                    self.end_y):
                plot(canvas, x, y, self.color)

def round_up(number):
    return int(round(number))

def round_down(number):
    return -int(round(-number))

def ellipse_parametric_equation(angle, a, b, x_center, y_center):
    x = math.cos(angle) * a
    if x < 0:
        x = round_down(x + x_center)
    else:
        x = round_up(x + x_center)

    y = math.sin(angle) * b
    if y < 0:
        y = round_down(y + y_center)
    else:
        y = round_up(y + y_center)
    return x, y

def raster_ellipse(start_x, start_y, end_x, end_y):
    """
    Generate a set of points describing the outline of an ellipse specified by
    the given bounding box.

    I'd like this to handle ellipses with odd heights or widths a little better
    in the future.
    """
    if start_x > end_x:
        start_x, end_x = end_x, start_x
    if start_y > end_y:
        start_y, end_y = end_y, start_y

    center_y = (start_y + end_y)/2.0
    center_x = (start_x + end_x)/2.0
    x_radius = end_x - center_x
    y_radius = end_y - center_y

    num_segments = max(int(x_radius * y_radius)*2, 16)

    points = set()

    last_point = ellipse_parametric_equation(0, x_radius, y_radius, center_x,
                                             center_y)
    for i in xrange(1, num_segments + 1):
        angle = (float(i) / num_segments) * 2 * math.pi
        this_point = ellipse_parametric_equation(angle, x_radius, y_radius,
                                                 center_x, center_y)
        points.update(raster_line(last_point[0], last_point[1],
                                  this_point[0], this_point[1]))
        last_point = this_point

    return points

class HollowCircle(DragTool):
    """
    Draw a hollow circle.
    """
    def do(self, canvas):
        if self.start_x is not None and self.end_x is not None:
            for x, y, in raster_ellipse(self.start_x, self.start_y, self.end_x,
                                        self.end_y):
                plot(canvas, x, y, self.color)

def fill_ellipse(points):
    points_by_x = defaultdict(list)
    for x, y in points:
        points_by_x[x].append((x, y))

    additional_points = []
    for points_list in points_by_x.itervalues():
        points_list.sort()
        x, last_y = points_list[0]
        for x, y in points_list[1:]:
            if y - last_y > 1:
                for new_y in xrange(last_y+1, y):
                    additional_points.append((x, new_y))
            last_y = y

    return additional_points

class Circle(DragTool):
    """
    Draw a filled-in circle.
    """
    def do(self, canvas):
        if self.start_x is not None and self.end_x is not None:
            points = raster_ellipse(self.start_x, self.start_y, self.end_x,
                                    self.end_y)
            for x, y, in points:
                plot(canvas, x, y, self.color)
            for x, y in fill_ellipse(points):
                plot(canvas, x, y, self.color)

class Rectangle(DragTool):
    """
    Draw a rectangle.
    """
    def do(self, canvas):
        if self.start_x is not None and self.end_x is not None:
            start_x, start_y = self.start_x, self.start_y
            end_x, end_y = self.end_x, self.end_y
            if start_x > end_x:
                start_x, end_x = end_x, start_x
            if start_y > end_y:
                start_y, end_y = end_y, start_y

            for x in xrange(start_x, end_x+1):
                for y in xrange(start_y, end_y+1):
                    plot(canvas, x, y, self.color)

class HollowRectangle(DragTool):
    """
    Draw a hollow rectangle.
    """
    def do(self, canvas):
        if self.start_x is not None and self.end_x is not None:
            start_x, start_y = self.start_x, self.start_y
            end_x, end_y = self.end_x, self.end_y
            if start_x > end_x:
                start_x, end_x = end_x, start_x
            if start_y > end_y:
                start_y, end_y = end_y, start_y

            for x in xrange(start_x, end_x+1):
                plot(canvas, x, start_y, self.color)
                plot(canvas, x, end_y, self.color)
            for y in xrange(start_y, end_y+1):
                plot(canvas, start_x, y, self.color)
                plot(canvas, end_x, y, self.color)


class FloodFill(Tool):
    """
    Fill the areas adjacent to a selected pixel that are also that pixel's
    color in a different color.
    """

class KillEraser(Tool):
    """
    Erase an entire tile.
    """

class EyeDropper(Tool):
    """
    Pick a current color from one already on the canvas.
    """

class TilePlacer(Tool):
    """
    Place a tile from the tile list into a place on the canvas.
    """

class GlobalColorReplace(Tool):
    """
    Replace one color with another across the whole canvas.
    """

class LocalColorReplace(Tool):
    """
    Replace one color with another across one tile.
    """

class SlammerCtrl(object):
    """
    The Pixel Slammer business logic sitting in between the view and the model.
    """

    def __init__(self, model, view):
        """
        Create a new PixelSlammer controller. Supply the model and the view.
        """
        self.base_model = model
        self.model = model.copy()
        self.action_stack = []

        self.left_tool = Rectangle
        self.left_color = (0,255,0,255)

        self.right_tool = HollowRectangle
        self.right_color = (0,0,255,255)

        self.view = view
        self.view.push_handlers(self)
        self.view.canvas.set_canvas(self.model.canvas)
        self.view.canvas.set_visible()
        self.view.toolbox.set_visible()

    def should_push_new_action(self):
        return not self.action_stack or self.action_stack[-1].is_ready()

    def downscale_coords(self, x, y):
        scale = self.view.canvas.scale
        return x // scale, y // scale

    def on_canvas_press(self, x, y, buttons, modifiers):
        if self.should_push_new_action():
            self.push_new_action(buttons, modifiers)

        self.get_top_action().accept_press(*self.downscale_coords(x, y))

        self.run_action_if_ready()

    def on_canvas_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.should_push_new_action():
            self.push_new_action(buttons, modifiers)

        start_x, start_y = self.downscale_coords(x, y)
        end_x, end_y = self.downscale_coords(x-dx, y-dy)
        self.get_top_action().accept_drag(start_x, start_y, end_x, end_y)

        self.run_action_if_ready()

    def on_canvas_release(self, x, y, buttons, modifiers):
        if self.should_push_new_action():
            self.push_new_action(buttons, modifiers)

        self.get_top_action().accept_release(*self.downscale_coords(x, y))

        self.run_action_if_ready()

    def on_key_press(self, key, modifiers):
        if key == keys.Z and keys.MOD_CTRL & modifiers:
            self.undo()

    def action_incomplete(self):
        return self.action_stack and not self.get_top_action().is_ready()

    def on_canvas_draw(self):
        self.view.canvas.clear()
        if self.action_incomplete():
            preview_canvas = self.model.canvas.copy()
            self.get_top_action().do(preview_canvas)
            preview_canvas.flush_changes()
            self.view.canvas.draw_canvas(preview_canvas)
        else:
            self.view.canvas.draw_canvas(self.model.canvas)

    def undo(self):
        self.model = self.base_model.copy()
        self.action_stack.pop()
        for action in self.action_stack:
            action.do(self.model.canvas)
        self.model.canvas.flush_changes()
        self.view.canvas.set_canvas(self.model.canvas)

    def push_new_action(self, buttons, modifiers):
        if pyglet.window.mouse.LEFT & buttons:
            tool = self.left_tool
            color = self.left_color
        else:
            tool = self.right_tool
            color = self.right_color

        self.action_stack.append(tool(color))

    def get_top_action(self):
        return self.action_stack[-1]

    def run_action_if_ready(self):
        if self.get_top_action().is_ready():
            self.get_top_action().do(self.model.canvas)
            self.model.canvas.flush_changes()
