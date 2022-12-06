from lingotojson import turntolingo
from menuclass import *


class MN(menu):
    def __init__(self, surface: pg.surface.Surface, data):
        super().__init__(surface, data, "MN")

    def GE(self):
        self.message = "GE"

    def TE(self):
        self.message = "TE"

    def LE(self):
        self.message = "LE"

    def LS(self):
        self.message = "LS"

    def FE(self):
        self.message = "FE"

    def CE(self):
        self.message = "CE"

    def LP(self):
        self.message = "LP"

    def EE(self):
        self.message = "EE"

    def PE(self):
        self.message = "PE"

    def save(self):
        self.message = "save"

    def saveastxt(self):
        self.message = "savetxt"

    def render(self):
        render(self.data)

    def quit(self):
        self.message = "quit"
