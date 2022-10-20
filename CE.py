from menuclass import *
from lingotojson import *

class CE(menu_with_field):
    def __init__(self, surface: pg.surface.Surface, data):
        self.menu = "CE"
        super().__init__(surface, data, "CE")

        self.held = False
        self.heldindex = 0
        self.camoffset = [0, 0]

        self.init()
        self.rfa()
        self.blit()
        self.resize()

    def blit(self):
        global mousp, mousp2, mousp1

        super().blit()
        self.rendercameras()

        if self.field.rect.collidepoint(pg.mouse.get_pos()):

            pos = [math.floor((pg.mouse.get_pos()[0] - self.field.rect.x) / self.size),
                   math.floor((pg.mouse.get_pos()[1] - self.field.rect.y) / self.size)]

            posoffset = [pos[0] - self.xoffset, pos[1] - self.yoffset]

            bp = pg.mouse.get_pressed(3)

            self.movemiddle(bp, pos)

    def rendercameras(self):
        for indx, cam in enumerate(self.data["CM"]["cameras"]):
            quads = self.data["CM"]["quads"][indx]

            pos = pg.Vector2(toarr(cam, "point"))
            p = (pos / 20) * self.size + self.field.rect.topleft + pg.Vector2(self.xoffset * self.size, self.yoffset * self.size)
            rect = pg.Rect([p, [camw * self.size, camh * self.size]])
            rect2 = pg.Rect(rect.x + self.size, rect.y + self.size, rect.w - self.size * 2, rect.h - self.size * 2)
            rect3 = pg.Rect(rect2.x + self.size * 8, rect2.y, rect2.w - self.size * 16, rect2.h)
            # print(camera_border, rect, self.size)
            pg.draw.rect(self.surface, camera_border, rect, max(self.size // 3, 1))
            pg.draw.rect(self.surface, camera_border, rect2, max(self.size // 4, 1))

            pg.draw.rect(self.surface, red, rect3, max(self.size // 3, 1))

            pg.draw.line(self.surface, camera_border, pg.Vector2(rect.center) - pg.Vector2(self.size * 5, 0),
                                                      pg.Vector2(rect.center) + pg.Vector2(self.size * 5, 0),
                         self.size // 3)

            pg.draw.line(self.surface, camera_border, pg.Vector2(rect.center) - pg.Vector2(0, self.size * 5),
                                                      pg.Vector2(rect.center) + pg.Vector2(0, self.size * 5),
                         self.size // 3)
            pg.draw.circle(self.surface, camera_border, rect.center, self.size * 3, self.size // 3)

            col = camera_notheld
            if indx == self.heldindex and self.held:
                col = camera_held
            # pg.draw.polygon(self.surface, col, [])

    def deletecamera(self):
        pass

    def addcamera(self):
        pass

    def resize(self):
        super().resize()

    def renderfield(self):
        self.fieldadd = pg.transform.scale(self.fieldadd,
                                           [len(self.data["GE"]) * self.size, len(self.data["GE"][0]) * self.size])
        self.fieldadd.fill(white)
        super().renderfield()

    def send(self, message):
        if message[0] == "-":
            getattr(self, message[1:])()
        match message:
            case "SU":
                self.size += 1
                self.renderfield()
            case "SD":
                if self.size - 1 != 0:
                    self.size -= 1
                    self.renderfield()
            case "left":
                self.xoffset += 1
            case "right":
                self.xoffset -= 1
            case "up":
                self.yoffset += 1
            case "down":
                self.yoffset -= 1
