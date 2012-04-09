from math import sqrt
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
        if self.start_x and self.end_x:
            for x, y in raster_line(self.start_x, self.start_y, self.end_x,
                                    self.end_y):
                plot(canvas, x, y, self.color)

def raster_4_ellipse_points(c_x, c_y, x, y):
    """
    Given a center point and x and y coordinates, return the four reflections
    of the coordinates across the center point.
    """
    coords = ((c_x + x, c_y + y), (c_x - x, c_y + y), (c_x - x, c_y - y),
              (c_x + x, c_y - y))
    new_coords = []
    for new_x, new_y in coords:
        new_coords.append(())

def raster_ellipse(start_x, start_y, end_x, end_y):
    """
    Generate a set of points describing the outline of an ellipse specified by
    the given bounding box.
    """
    if start_x > end_x:
        start_x, end_x = end_x, start_x
    if start_y > end_y:
        start_y, end_y = end_y, start_y
    center_x, center_y = start_x + end_x, start_y + end_y
    x_radius, y_radius = center_x - start_x*2, center_y - start_y*2

    points = set()

    # handle special cases
    if x_radius == 0 or y_radius == 0:
        for x in xrange(start_x, end_x+1):
            for y in xrange(start_y, end_y+1):
                points.add((x,y))
        return list(points)

    #this does twice as much work as it needs to, but it gets the job done
    semi_major = x_radius
    semi_minor = y_radius
    for x in xrange(x_radius+1):
        y = int(round(sqrt((1 - (float(x) / semi_major) ** 2) * semi_minor ** 2)))
        points.update(raster_4_ellipse_points(center_x, center_y, x, y))

    # ideally, these would stop iterating when the slope of the points passes 1
    semi_major = y_radius
    semi_minor = x_radius
    for y in xrange(y_radius+1):
        x = int(round(sqrt((1 - (float(y) / semi_major) ** 2) * semi_minor ** 2)))
        points.update(raster_4_ellipse_points(center_x, center_y, x, y))

    return list(points)

class HollowCircle(DragTool):
    """
    Draw a hollow circle.
    """
    def do(self, canvas):
        if self.start_x and self.end_x:
            for x, y, in raster_ellipse(self.start_x, self.start_y, self.end_x,
                                        self.end_y):
                plot(canvas, x, y, self.color)

class Circle(DragTool):
    """
    Draw a filled-in circle.
    """
    def do(self, canvas):
        if self.start_x and self.end_x:
            points = raster_ellipse(self.start_x, self.start_y, self.end_x,
                                    self.end_y)
            for x, y, in points:
                plot(canvas, x, y, self.color)
            for x, y in fill_ellipse(points):
                plot(canvas, x, y, self.color)

class Rectangle(Tool):
    """
    Draw a rectangle.
    """

class HollowRectangle(Tool):
    """
    Draw a hollow rectangle.
    """

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

        self.left_tool = Pencil
        self.left_color = (0,255,0,255)

        self.right_tool = HollowCircle
        self.right_color = (0,0,255,255)

        self.view = view
        self.view.push_handlers(self)
        self.view.canvas.set_canvas(self.model.canvas)
        self.view.canvas.set_visible()

    def should_push_new_action(self):
        return not self.action_stack or self.action_stack[-1].is_ready()

    def downscale_coords(self, x, y):
        scale = self.view.canvas.scale
        return x // scale, y // scale

    def on_mouse_press(self, x, y, buttons, modifiers):
        if self.should_push_new_action():
            self.push_new_action(buttons, modifiers)

        self.get_top_action().accept_press(*self.downscale_coords(x, y))

        self.run_action_if_ready()

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.should_push_new_action():
            self.push_new_action(buttons, modifiers)

        #print "drag from", start_x, start_y, "to", end_x, end_y
        start_x, start_y = self.downscale_coords(x, y)
        end_x, end_y = self.downscale_coords(x-dx, y-dy)
        self.get_top_action().accept_drag(start_x, start_y, end_x, end_y)

        self.run_action_if_ready()

    def on_mouse_release(self, x, y, buttons, modifiers):
        if self.should_push_new_action():
            self.push_new_action(buttons, modifiers)

        self.get_top_action().accept_release(*self.downscale_coords(x, y))

        self.run_action_if_ready()

    def on_key_press(self, key, modifiers):
        if key == keys.Z and keys.MOD_CTRL & modifiers:
            self.undo()

    def action_incomplete(self):
        return self.action_stack and not self.get_top_action().is_ready()

    def on_draw(self):
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
        print len(self.action_stack)

    def get_top_action(self):
        return self.action_stack[-1]

    def run_action_if_ready(self):
        if self.get_top_action().is_ready():
            self.get_top_action().do(self.model.canvas)
            self.model.canvas.flush_changes()
