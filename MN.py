from lingotojson import turntolingo
from menuclass import *
import random


class MN(menu):
    def __init__(self, surface: pg.surface.Surface, data):
        super().__init__(surface, data, "MN")
        tips = set(open(path + "tips.txt", "r").readlines())
        self.tips = list(tips)
        self.tips.remove("\n")
        self.nexttip()

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

    def HK(self):
        self.message = "HK"

    def save(self):
        self.message = "save"

    def saveastxt(self):
        self.message = "savetxt"

    def saveas(self):
        self.message = "saveas"

    def render(self):
        render(self.data)

    def quit(self):
        self.message = "quit"

    def nexttip(self):
        self.labels[0].set_text(self.returnkeytext(random.choice(self.tips).replace("\n", "").replace("\\n", "\n"), True))