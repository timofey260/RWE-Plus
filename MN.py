from lingotojson import turntolingo
from menuclass import *
import random


class MN(menu_with_field):
    def __init__(self, surface: pg.surface.Surface, data, items, props, propcolors):
        super().__init__(surface, data, "MN", items, props, propcolors)
        tips = set(open(path + "tips.txt", "r").readlines())
        self.items = items
        self.tips = list(tips)
        self.mousp = True
        self.mousp1 = True
        self.mousp2 = True
        self.tips.remove("\n")
        self.nexttip()
        self.rfa()
        self.resize()

    def blit(self):
        super().blit()
        if self.field.rect.collidepoint(pg.mouse.get_pos()):
            mpos = pg.Vector2(pg.mouse.get_pos())

            pos = [math.floor((mpos.x - self.field.rect.x) / self.size),
                   math.floor((mpos.y - self.field.rect.y) / self.size)]
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
        render(self.data)

    def quit(self):
        self.message = "quit"

    def nexttip(self):
        self.labels[0].set_text(self.returnkeytext(random.choice(self.tips).replace("\n", "").replace("\\n", "\n")))