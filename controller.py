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

    def on_canvas_click(self, x, y, button, modifiers):
        """
        When a spot on the canvas is clicked, this method is notified with x
        and y floating point coordinates.
        """
        #identify the right pixel

        if button == pyglet.window.mouse.LEFT:
            #make the right pixel black
            pass
        elif button == pyglet.window.mouse.RIGHT:
            #make the right pixel white
            pass
