__author__ = 'cseebach'

import pyglet.window.key as keys

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

    class MoreInputNeeded(Exception):
        pass

    def __init__(self, color):
        """Create a new Tool, and give it the color it should apply."""
        self.color = color

    def accept_press(self, x, y):
        """
        Send a mouse press to this tool. Returns the result of is_ready after this
        call is executed.
        """

    def accept_drag(self, start_x, start_y, end_x, end_y):
        """
        Send a mouse drag to this tool. Returns the result of is_ready after this
        call is executed.
        """

    def accept_release(self, x, y):
        """
        Send a mouse release to this tool. Returns the result of is_ready after this
        call is executed.
        """

    def is_ready(self):
        """
        Returns True if this tool needs no more information to have do() be
        called.
        """

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

def draw_line(start_x, start_y, end_x, end_y):
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
        self.__is_ready = False

    def accept_press(self, x, y):
        self.to_plot.add((x,y))

    def accept_drag(self, start_x, start_y, end_x, end_y):
        self.to_plot.update(draw_line(start_x, start_y, end_x, end_y))

    def accept_release(self, x, y):
        self.to_plot.add((x,y))
        self.__is_ready = True
        return self.is_ready()

    def is_ready(self):
        return self.__is_ready

    def do(self, canvas):
        for x, y in self.to_plot:
            plot(canvas, x, y, self.color)


def action_responder(function):
    def wrapped(self, *args, **kwargs):
        if self.should_push_new_action():
            self.push_new_action()

        function(self, *args, **kwargs)

        preview_canvas = self.model.canvas.copy()
        self.get_top_action().do(preview_canvas)
        self.view.canvas.show_preview(preview_canvas)
        self.run_action_if_ready()

    return wrapped


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
        self.current_tool = Pencil
        self.current_color = (0,255,0,255)

        self.view = view
        self.view.push_handlers(self)
        self.view.canvas.set_canvas(self.model.canvas)
        self.view.canvas.set_visible()

    def get_canvas_pixel(self, x_ratio, y_ratio):
        """
        Given floating point coordinates between (0.0, 0.0) and (1.0, 1.0),
        find the integer coordinates that correspond.
        """
        canvas_w, canvas_h = self.model.canvas.width, self.model.canvas.height
        pix_x = int(x_ratio * canvas_w)
        pix_y = int(y_ratio * canvas_h)

        return pix_x, pix_y

    def should_push_new_action(self):
        return not self.action_stack or self.action_stack[-1].is_ready()

    @action_responder
    def on_mouse_press(self, x, y, buttons, modifiers):
        """
        When a spot on the canvas is clicked, this method is notified with x
        and y floating point coordinates.
        """
        #identify the right pixel
        scale = self.view.canvas.scale
        pix_x, pix_y = x//scale, y//scale
        #print "press at", pix_x, pix_y
        self.get_top_action().accept_press(pix_x, pix_y)

    @action_responder
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        """
        When the user drags the mouse starting in the canvas, this method is
        notified with x and y floating point coordinates for both start and
        end positions.
        """
        #identify start and end pixels
        scale = self.view.canvas.scale
        start_x, start_y = (x-dx)//scale, (y-dy)//scale
        end_x, end_y = x//scale, y//scale
        #print "drag from", start_x, start_y, "to", end_x, end_y
        self.get_top_action().accept_drag(start_x, start_y, end_x, end_y)

    @action_responder
    def on_mouse_release(self, x, y, buttons, modifiers):
        #identify the right pixel
        scale = self.view.canvas.scale
        pix_x, pix_y = x//scale, y//scale
        #print "release at", pix_x, pix_y
        self.get_top_action().accept_release(pix_x, pix_y)

    def on_key_press(self, key, modifiers):
        if key == keys.Z and keys.MOD_CTRL & modifiers:
            self.undo()

    def undo(self):
        self.model = self.base_model.copy()
        self.action_stack.pop()
        for action in self.action_stack:
            action.do(self.model.canvas)
        self.view.canvas.set_canvas(self.model.canvas)

    def push_new_action(self):
        self.action_stack.append(self.current_tool(self.current_color))
        #print len(self.action_stack)

    def get_top_action(self):
        return self.action_stack[-1]

    def run_action_if_ready(self):
        if self.get_top_action().is_ready():
            self.get_top_action().do(self.model.canvas)
            self.view.canvas.hide_preview()
