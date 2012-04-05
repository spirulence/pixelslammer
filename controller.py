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