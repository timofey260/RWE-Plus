from lingotojson import turntolingo
from menuclass import *
import random


class MN(MenuWithField):
    def __init__(self, process):
        super().__init__(process, "MN")
        tips = set(open(path + "tips.txt", "r").readlines())
        self.tips = list(tips)
        self.mousp = True
        self.mousp1 = True
        self.mousp2 = True
        self.tips.remove("\n")
        self.nexttip()
        self.resize()

    def blit(self):
        super().blit()
        if self.onfield:
            bp = self.getmouse
            self.movemiddle(bp)

    def tiles(self):
        self.drawtiles = not self.drawtiles
        self.rfa()

    def GE(self):
        self.sendtoowner("GE")

    def TE(self):
        self.sendtoowner("TE")

    def LE(self):
        self.sendtoowner("LE")

    def FE(self):
        self.sendtoowner("FE")

    def CE(self):
        self.sendtoowner("CE")

    def LP(self):
        self.sendtoowner("LP")

    def PE(self):
        self.sendtoowner("PE")

    def HK(self):
        self.sendtoowner("HK")

    def save(self):
        self.savef()

    def saveastxt(self):
        self.savef_txt()

    def saveas(self):
        self.saveasf()

    def render(self):
        self.savef()
        renderlevel(self.data)

    def quit(self):
        self.sendtoowner("quit")

    def nexttip(self):
        self.labels[0].set_text(self.returnkeytext(random.choice(self.tips).replace("\n", "").replace("\\n", "\n")))

    def report(self):
        report()

    def github(self):
        github()