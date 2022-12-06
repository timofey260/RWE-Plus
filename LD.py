from menuclass import *


class load(menu):
    def __init__(self, surface: pg.surface.Surface, data):
        super().__init__(surface, data, "LD")
        self.menu = "LD"
        self.surface = surface
        self.data = data
        self.message = ""
        self.init()

    def send(self, message):
        self.message = message

    def blit(self):
        super().blit(30)

    def open(self):
        self.message = "open"

    def new(self):
        self.message = "new"
