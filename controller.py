__author__ = 'cseebach'

class Tool(object):
    """
    A base class for each kind of tool available in Pixel Slammer.

    The Tool workflow:
        Create the tool you want to use.

        Send it input until the input accepting methods return an object that
        evaluates to False.

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
        Send a click to this tool. This method returns True if more input is
        needed.
        """

    def accept_drag(self, start_x, start_y, end_x, end_y):
        """
        Send a drag to this tool. This method returns True if more input is
        needed.
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

    def accept_click(self, x, y):
        self.style = "point"
        self.x = x
        self.y = y

    def accept_drag(self, start_x, start_y, end_x, end_y):
        self.style = "line"
        self.start_x, self.start_y = start_x, start_y
        self.end_x, self.end_y = end_x, end_y

    def do(self, model):
        if not self.style:
            raise (Tool.MoreInputNeeded,
                   "Pencil needs a click or a drag before do()")
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
        self.view = view
        self.view.push_handlers(self)
        self.view.canvas.set_canvas(model.get_canvas())

        self.current_tool = Pencil
        self.current_tool_instance = None
        self.current_color = (0,0,0,255)

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

    def on_canvas_click(self, x, y, buttons, modifiers):
        """
        When a spot on the canvas is clicked, this method is notified with x
        and y floating point coordinates.
        """
        #identify the right pixel
        pix_x, pix_y = self.get_canvas_pixel(x, y)

        if not self.current_tool_instance:
            self.current_tool_instance = self.current_tool(self.current_color)
        more_input = self.current_tool_instance.accept_click(pix_x, pix_y)
        if not more_input:
            self.current_tool_instance.do(self.model)
            self.current_tool_instance = None


    def on_canvas_drag(self, start_x_ratio, start_y_ratio, end_x_ratio,
                       end_y_ratio, buttons, modifiers):
        """
        When the user drags the mouse starting in the canvas, this method is
        notified with x and y floating point coordinates for both start and
        end positions.
        """

        start_x, start_y = self.get_canvas_pixel(start_x_ratio, start_y_ratio)
        end_x, end_y = self.get_canvas_pixel(end_x_ratio, end_y_ratio)

        if not self.current_tool_instance:
            self.current_tool_instance = self.current_tool(self.current_color)
        more_input = self.current_tool_instance.accept_drag(start_x, start_y,
                                                            end_x, end_y)
        if not more_input:
            self.current_tool_instance.do(self.model)
            self.current_tool_instance = None
