import pyglet

__author__ = 'cseebach'

def get_tile_and_pixel(canvas, x_ratio, y_ratio):
    canvas_w, canvas_h = canvas.get_size()
    tile_w, tile_h = canvas.get_tile_size()
    pix_x = int(x_ratio * canvas_w * tile_w)
    pix_y = int(y_ratio * canvas_h * tile_h)

    return pix_x // tile_h, pix_y // tile_h, pix_x % tile_w, pix_y % tile_h

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

    def on_canvas_click(self, x, y, button, modifiers):
        """
        When a spot on the canvas is clicked, this method is notified with x
        and y floating point coordinates.
        """
        #identify the right pixel
        tile_x, tile_y, pix_x, pix_y = get_tile_and_pixel(self.model.canvas, x, y)

        if button == pyglet.window.mouse.LEFT:
            #turn it black
            self.model.canvas.get_tile(tile_x, tile_y).set_pixel(pix_x, pix_y, (0,0,0,255))
        elif button == pyglet.window.mouse.RIGHT:
            #turn it white
            self.model.canvas.get_tile(tile_x, tile_y).set_pixel(pix_x, pix_y, (255,255,255,255))
