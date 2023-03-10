from menuclass import *

class load(menu):
    def __init__(self, surface: pg.surface.Surface, data):
        super().__init__(surface, data, "LD")

    def send(self, message):
        self.message = message

    def blit(self):
        super().blit(30)

    def open(self):
        self.message = "open"

    def new(self):
        self.message = "new"
