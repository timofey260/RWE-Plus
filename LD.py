from menuclass import *

class load(Menu):
    def __init__(self, surface: pg.surface.Surface, renderer):
        super().__init__(surface, renderer, "LD")

    def send(self, message):
        self.message = message

    def blit(self):
        super().blit(30)

    def open(self):
        self.message = "open"

    def new(self):
        self.message = "new"
