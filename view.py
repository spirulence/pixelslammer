__author__ = 'cseebach'

import pyglet

class SelfRegistrant(pyglet.window.Window):

    dispatches = []

    def __init__(self, *args, **kwargs):
        super(SelfRegistrant, self).__init__(*args, **kwargs)

        for event_type in self.dispatches:
            self.register_event_type(event_type)

class CanvasView(SelfRegistrant):

    dispatches = ["on_canvas_click"]

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("visible", False)
        super(CanvasView, self).__init__(*args, **kwargs)

        self.scale = kwargs.get("scale", 8)

    def set_canvas(self, canvas):
        self.canvas = canvas
        self.fit_to_canvas()

    def fit_to_canvas(self):
        pass

class SlammerView(object):
    """
    The User Interface to the Pixel Slammer data.
    """

    def __init__(self):
        self.canvas = CanvasView()