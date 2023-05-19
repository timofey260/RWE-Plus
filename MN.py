from lingotojson import turntolingo
from menuclass import *
import random


class MN(MenuWithField):
    def __init__(self, surface: pg.surface.Surface, renderer: Renderer):
        super().__init__(surface, "MN", renderer)
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
        mpos = pg.Vector2(pg.mouse.get_pos())
        if self.field.rect.collidepoint(mpos):

            pos = self.pos
            bp = pg.mouse.get_pressed(3)

            self.movemiddle(bp, pos)

    def tiles(self):
        self.drawtiles = not self.drawtiles
        self.rfa()

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
        self.savef()

    def saveastxt(self):
        self.savef_txt()

    def saveas(self):
        self.saveasf()

    def render(self):
        self.savef()
        renderlevel(self.data)

    def quit(self):
        self.message = "quit"

    def nexttip(self):
        self.labels[0].set_text(self.returnkeytext(random.choice(self.tips).replace("\n", "").replace("\\n", "\n")))