from menuclass import *


class EE(menu_with_field):
    def __init__(self, surface: pg.surface.Surface, data, items, props, propcolors):
        super().__init__(surface, data, "EE", items, props, propcolors)
        self.layer = 1 - self.data["WL"]["waterInFront"]
        self.wateroffset = 0

        self.init()
        self.rfa()
        self.blit()
        self.resize()


    def water(self):
        self.data["WL"]["waterLevel"] = toarr(self.data["EX2"]["size"], "point")[1] // 2

    def nowater(self):
        self.data["WL"]["waterLevel"] = -1

    def blit(self):
        super().blit()
        self.fieldadd.fill(white)
        if self.data["WL"]["waterLevel"] != -1:
            height = len(self.data["GE"][0]) * self.size
            width = len(self.data["GE"]) * self.size

            top = height - ((wladd + self.data["WL"]["waterLevel"]) * self.size)

            h = height - top

            rect = pg.Rect(0, top, width, h)
            pg.draw.rect(self.fieldadd, blue, rect)

        self.labels[0].set_text(self.labels[0].originaltext % self.data["WL"]["waterLevel"])
        self.labels[1].set_text(self.labels[1].originaltext % (1 - self.data["WL"]["waterInFront"] + 1))

        if self.field.rect.collidepoint(pg.mouse.get_pos()):
            pos = [math.floor((pg.mouse.get_pos()[0] - self.field.rect.x) / self.size),
                   math.floor((pg.mouse.get_pos()[1] - self.field.rect.y) / self.size)]

            posoffset = [pos[0] - self.xoffset, pos[1] - self.yoffset]

            bp = pg.mouse.get_pressed()

            if bp[0] == 1 and self.mousp and (self.mousp2 and self.mousp1):
                self.mousp = False
                self.wateroffset = self.data["WL"]["waterLevel"] + posoffset[1]
            elif bp[0] == 1 and not self.mousp and (self.mousp2 and self.mousp1):
                self.data["WL"]["waterLevel"] = max(self.wateroffset - posoffset[1], 0)
            elif bp[0] == 0 and not self.mousp and (self.mousp2 and self.mousp1):
                self.mousp = True
                self.rfa()

            self.movemiddle(bp, pos)

    def swichlayers(self):
        self.layer = 1 - self.layer
        self.data["WL"]["waterInFront"] = 1 - self.layer
        self.rfa()
