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

    class MoreInputNeeded(Exception):
        pass

    def __init__(self, color):
        """Create a new Tool, and give it the color it should apply."""
        self.color = color

    def accept_click(self, x, y):
        """
        Send a click to this tool. Returns the result of is_ready after this
        call is executed.
        """

    def accept_drag(self, start_x, start_y, end_x, end_y):
        """
        Send a drag to this tool. Returns the result of is_ready after this
        call is executed.
        """

    def is_ready(self):
        """
        Returns True if this tool needs no more information to have do() be
        called.
        """

    def do(self, model):
        """
        Run the action associated with this tool on the specified model. Throws
        MoreInputNeeded if more input is needed.
        """

def plot(model, x, y, color):
    """
    Change the color of a single pixel on the model's canvas.
    """
    canvas_w, canvas_h = model.canvas.get_size()
    tile_w, tile_h = model.canvas.get_tile_size()

    max_x = canvas_w * tile_w
    max_y = canvas_h * tile_h
    if x < 0 or y < 0 or x >= max_x or y >= max_y:
        return

    tile_x, tile_y = x // tile_w, y // tile_h
    tile_pix_x, tile_pix_y = x % tile_w, y % tile_h

    tile = model.canvas.get_tile(tile_x, tile_y)
    tile.set_pixel(tile_pix_x, tile_pix_y, color)

def draw_line(model, start_x, start_y, end_x, end_y, color):
    """
    Draw a line on the model's canvas in the specified color.
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
    for x in xrange(start_x, end_x+1):
        if steep:
            plot(model, y, x, color)
        else:
            plot(model, x, y, color)
        error -= delta_y
        if error < 0:
            y += y_step
            error += delta_x

class Pencil(Tool):
    """
    A class for drawing simple lines and points on the canvas.
    """

    def __init__(self, color):
        super(Pencil, self).__init__(color)
        self.style = None
        self.__is_ready = False

    def accept_click(self, x, y):
        self.style = "point"
        self.x = x
        self.y = y
        self.__is_ready = True
        return self.is_ready()

    def accept_drag(self, start_x, start_y, end_x, end_y):
        self.style = "line"
        self.start_x, self.start_y = start_x, start_y
        self.end_x, self.end_y = end_x, end_y
        self.__is_ready = True
        return self.is_ready()

    def is_ready(self):
        return self.__is_ready

    def do(self, model):
        if not self.style:
            msg = "Pencil needs a click or a drag before do()"
            raise Tool.MoreInputNeeded, msg
        elif self.style == "point":
            plot(model, self.x, self.y, self.color)
        elif self.style == "line":
            draw_line(model, self.start_x, self.start_y, self.end_x,
                      self.end_y, self.color)

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
        self.current_color = (0,0,0,255)

        self.view = view
        self.view.push_handlers(self)
        self.view.canvas.set_canvas(self.updated_model.get_canvas())

    def get_canvas_pixel(self, x_ratio, y_ratio):
        """
        Given floating point coordinates between (0.0, 0.0) and (1.0, 1.0),
        find the integer coordinates that correspond.
        """
        canvas_w, canvas_h = self.model.canvas.get_size()
        tile_w, tile_h = self.model.canvas.get_tile_size()
        pix_x = int(x_ratio * canvas_w * tile_w)
        pix_y = int(y_ratio * canvas_h * tile_h)

        return pix_x, pix_y

    def should_push_new_action(self):
        return not self.action_stack or self.action_stack[-1].is_ready()

    def on_canvas_click(self, x, y, buttons, modifiers):
        """
        When a spot on the canvas is clicked, this method is notified with x
        and y floating point coordinates.
        """
        #identify the right pixel
        pix_x, pix_y = self.get_canvas_pixel(x, y)

        if self.should_push_new_action():
            self.push_new_action()
        self.get_top_action().accept_click(pix_x, pix_y)
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

        if self.should_push_new_action():
            self.push_new_action()
        self.get_top_action().accept_drag(start_x, start_y, end_x, end_y)
        self.run_action_if_ready()

    def push_new_action(self):
        self.action_stack.append(self.current_tool(self.current_color))

    def get_top_action(self):
        return self.action_stack[-1]

    def run_action_if_ready(self):
        if self.get_top_action().is_ready():
            self.get_top_action().do(self.updated_model)
