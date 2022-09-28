from menuclass import *


class load(menu):
    def __init__(self, surface: pg.surface.Surface, data):
        self.menu = "LD"
        self.surface = surface
        self.data = data
        self.init()

    def send(self, message):
        self.message = message

    def open(self):
        self.message = "open"

    def new(self):
        self.message = "new"
