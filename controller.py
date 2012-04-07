__author__ = 'cseebach'

import pyglet.window.key as keys

from model import Canvas

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

    def get_preview(self):
        """
        Return a preview of the modifications this tool will make.
        """

    def do(self, model):
        """
        Run the action associated with this tool on the specified model. Throws
        MoreInputNeeded if more input is needed.
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

    def get_preview(self):
        #determine max x and y
        x, y = zip(*self.to_plot)
        canvas = Canvas((max(x)+1, max(y)+1),(1,1))
        for x, y, in self.to_plot:
            plot(canvas, x, y, self.color)
        return canvas

    def is_ready(self):
        return self.__is_ready

    def do(self, model):
        if not self.is_ready():
            msg = "Pencil needs a mouse release before do()"
            raise Tool.MoreInputNeeded, msg
        else:
            for x, y in self.to_plot:
                plot(model.canvas, x, y, self.color)

class SlammerCtrl(object):
    """
    The Pixel Slammer business logic sitting in between the view and the model.
    """

    def __init__(self, model, view):
        """
        Create a new PixelSlammer controller. Supply the model and the view.
        """
        self.model = model
        self.updated_model = model.copy()
        self.action_stack = []
        self.current_tool = Pencil
        self.current_color = (0,255,0,255)

        self.view = view
        self.view.push_handlers(self)
        self.view.canvas.set_canvas(self.updated_model.canvas)

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

    def on_canvas_press(self, x, y, buttons, modifiers):
        """
        When a spot on the canvas is clicked, this method is notified with x
        and y floating point coordinates.
        """
        #identify the right pixel
        pix_x, pix_y = self.get_canvas_pixel(x, y)
        #print "press at", pix_x, pix_y

        if self.should_push_new_action():
            self.push_new_action()
        self.get_top_action().accept_press(pix_x, pix_y)
        self.view.canvas.show_preview(self.get_top_action().get_preview())
        self.run_action_if_ready()

    def on_canvas_drag(self, start_x_ratio, start_y_ratio, end_x_ratio,
                       end_y_ratio, buttons, modifiers):
        """
        When the user drags the mouse starting in the canvas, this method is
        notified with x and y floating point coordinates for both start and
        end positions.
        """
        #identify start and end pixels
        start_x, start_y = self.get_canvas_pixel(start_x_ratio, start_y_ratio)
        end_x, end_y = self.get_canvas_pixel(end_x_ratio, end_y_ratio)
        #print "drag from", start_x, start_y, "to", end_x, end_y

        if self.should_push_new_action():
            self.push_new_action()
        self.get_top_action().accept_drag(start_x, start_y, end_x, end_y)
        self.view.canvas.show_preview(self.get_top_action().get_preview())
        self.run_action_if_ready()

    def on_canvas_release(self, x, y, buttons, modifiers):
        #identify the right pixel
        pix_x, pix_y = self.get_canvas_pixel(x, y)
        #print "release at", pix_x, pix_y

        if self.should_push_new_action():
            self.push_new_action()
        self.get_top_action().accept_release(pix_x, pix_y)
        self.view.canvas.show_preview(self.get_top_action().get_preview())
        self.run_action_if_ready()

    def on_key_press(self, key, modifiers):
        if key == keys.Z and keys.MOD_CTRL & modifiers:
            self.undo()

    def undo(self):
        self.updated_model = self.model.copy()
        self.action_stack.pop()
        for action in self.action_stack:
            action.do(self.updated_model)
        self.view.canvas.set_canvas(self.updated_model.get_canvas())

    def push_new_action(self):
        self.action_stack.append(self.current_tool(self.current_color))
        #print len(self.action_stack)

    def get_top_action(self):
        return self.action_stack[-1]

    def run_action_if_ready(self):
        if self.get_top_action().is_ready():
            self.get_top_action().do(self.updated_model)
            self.view.canvas.hide_preview()
