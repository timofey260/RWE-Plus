from menuclass import *


class EE(MenuWithField):
    def __init__(self, surface: pg.surface.Surface, renderer):
        super().__init__(surface, "EE", renderer)
        self.layer = 1 - self.data["WL"]["waterInFront"]
        self.wateroffset = 0
        self.count = False

        self.rfa()
        self.blit()
        self.resize()


    def water(self):
        self.data["WL"]["waterLevel"] = toarr(self.data["EX2"]["size"], "point")[1] // 2
        self.updatehistory([["WL", "waterLevel"]])

    def nowater(self):
        self.data["WL"]["waterLevel"] = -1
        self.updatehistory([["WL", "waterLevel"]])

    def blit(self):
        super().blit()
        self.fieldadd.fill(white)
        if self.data["WL"]["waterLevel"] != -1:
            height = len(self.data["GE"][0]) * self.size
            width = len(self.data["GE"]) * self.size

            top = height - ((wladd + self.data["WL"]["waterLevel"]) * self.size)

            h = height - top

            #rect = pg.Rect(self.xoffset * self.size, self.yoffset * self.size + top, width, h)
            s = pg.Surface([width, h])
            s.fill(blue)
            s.set_alpha(100)
            self.field.field.blit(s, [self.xoffset * self.size, self.yoffset * self.size + top])
        self.field.blit()
        super().blit(False)
        self.labels[0].set_text(self.labels[0].originaltext % self.data["WL"]["waterLevel"])
        self.labels[1].set_text(self.labels[1].originaltext % (1 - self.data["WL"]["waterInFront"] + 1))

        if self.field.rect.collidepoint(pg.mouse.get_pos()):
            pos = [math.floor((pg.mouse.get_pos()[0] - self.field.rect.x) / self.size),
                   math.floor((pg.mouse.get_pos()[1] - self.field.rect.y) / self.size)]

            posoffset = [pos[0] - self.xoffset, pos[1] - self.yoffset]

            bp = pg.mouse.get_pressed()

            if bp[0] == 1 and self.mousp and (self.mousp2 and self.mousp1):
                self.count = True
                self.mousp = False
                self.wateroffset = self.data["WL"]["waterLevel"] + posoffset[1]
            elif bp[0] == 1 and not self.mousp and (self.mousp2 and self.mousp1) and self.count:
                self.data["WL"]["waterLevel"] = max(self.wateroffset - posoffset[1], 0)
            elif bp[0] == 0 and not self.mousp and (self.mousp2 and self.mousp1):
                self.updatehistory([["WL", "waterLevel"]])
                self.mousp = True
                self.rfa()

            self.movemiddle(bp, pos)

    def swichlayers(self):
        self.layer = 1 - self.layer
        self.data["WL"]["waterInFront"] = 1 - self.layer
        self.updatehistory([["WL", "waterInFront"]])
        self.rfa()
