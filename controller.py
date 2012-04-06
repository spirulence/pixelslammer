import pyglet

__author__ = 'cseebach'


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

    def get_canvas_pixel(self, x_ratio, y_ratio):
        canvas_w, canvas_h = self.model.canvas.get_size()
        tile_w, tile_h = self.model.canvas.get_tile_size()
        pix_x = int(x_ratio * canvas_w * tile_w)
        pix_y = int(y_ratio * canvas_h * tile_h)

        return pix_x, pix_y

    def plot(self, x, y, color):
        """
        Plot a pixel on the canvas in the specified color. If pixel specified
        is out of bounds, do nothing.
        """
        canvas_w, canvas_h = self.model.canvas.get_size()
        tile_w, tile_h = self.model.canvas.get_tile_size()

        max_x = canvas_w * tile_w
        max_y = canvas_h * tile_h
        if x < 0 or y < 0 or x >= max_x or y >= max_y:
            return

        tile_x, tile_y = x // tile_w, y // tile_h
        tile_pix_x, tile_pix_y = x % tile_w, y % tile_h

        tile = self.model.canvas.get_tile(tile_x, tile_y)
        tile.set_pixel(tile_pix_x, tile_pix_y, color)

    def on_canvas_click(self, x, y, buttons, modifiers):
        """
        When a spot on the canvas is clicked, this method is notified with x
        and y floating point coordinates.
        """
        #identify the right pixel
        pix_x, pix_y = self.get_canvas_pixel(x, y)

        if buttons & pyglet.window.mouse.LEFT:
            #turn it black
            self.plot(pix_x, pix_y, (0,0,0,255))
        elif buttons & pyglet.window.mouse.RIGHT:
            #turn it white
            self.plot(pix_x, pix_y, (255,255,255,255))

    def on_canvas_drag(self, start_x_ratio, start_y_ratio, end_x_ratio,
                       end_y_ratio, buttons, modifiers):
        """
        When the user drags the mouse starting in the canvas, this method is
        notified with x and y floating point coordinates for both start and
        end positions.

        Also happens to be an implementation of the Bresenham line algorithm.
        """
        if pyglet.window.mouse.LEFT & buttons:
            color = (0, 0, 0, 255)
        elif pyglet.window.mouse.RIGHT & buttons:
            color = (255, 255, 255, 255)
        else:
            return

        start_x, start_y = self.get_canvas_pixel(start_x_ratio, start_y_ratio)
        end_x, end_y = self.get_canvas_pixel(end_x_ratio, end_y_ratio)

        steep = abs(end_y - start_y) > abs(end_x - start_x)
        if steep:
            start_x, start_y = start_y, start_x
            end_x, end_y = end_y, end_x
        if start_x > end_x:
            start_x, end_x = end_x, start_x
            start_y, end_y = end_y, start_y
        delta_x = end_x - start_x
        delta_y = abs(end_y - start_y)
        error = delta_x / 2
        y = start_y
        if start_y < end_y:
            y_step = 1
        else:
            y_step = -1
        for x in xrange(start_x, end_x+1):
            if steep:
                self.plot(y, x, color)
            else:
                self.plot(x, y, color)
            error -= delta_y
            if error < 0:
                y += y_step
                error += delta_x
