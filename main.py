__author__ = 'cseebach'

import pyglet

from controller import SlammerCtrl
from model import SlammerModel
from view import SlammerView

def main():
    """
    Run the Pixel Slammer application
    """
    model = SlammerModel()
    view = SlammerView()
    ctrl = SlammerCtrl(model, view)

    pyglet.app.run()

if __name__ == "__main__":
    main()