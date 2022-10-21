import math

from menuclass import *
from lingotojson import *


class CE(menu_with_field):
    def __init__(self, surface: pg.surface.Surface, data):
        self.menu = "CE"
        super().__init__(surface, data, "CE")

        self.held = False
        self.heldindex = 0
        self.camoffset = pg.Vector2(0, 0)

        self.init()
        self.rfa()
        self.blit()
        self.resize()

    def blit(self):
        global mousp, mousp2, mousp1

        super().blit()
        self.rendercameras()
        self.labels[0].set_text(self.labels[0].originaltext % len(self.data["CM"]["cameras"]))

        if self.field.rect.collidepoint(pg.mouse.get_pos()) and len(self.data["CM"]["cameras"]) > 0:

            pos = [math.floor((pg.mouse.get_pos()[0] - self.field.rect.x) / self.size),
                   math.floor((pg.mouse.get_pos()[1] - self.field.rect.y) / self.size)]

            bp = pg.mouse.get_pressed(3)

            mpos = pg.Vector2(pg.mouse.get_pos()) / self.size * image1size
            if self.held and self.heldindex < len(self.data["CM"]["cameras"]):
                val = list(self.camoffset + mpos)
                val[0] = round(val[0], 4)
                val[1] = round(val[1], 4)
                val = makearr(val, "point")
                self.data["CM"]["cameras"][self.heldindex] = val

            if bp[0] == 1 and mousp and (mousp2 and mousp1):
                mousp = False
                if not self.held:
                    self.pickupcamera()
                else:
                    self.placecamera()

            elif bp[0] == 1 and not mousp and (mousp2 and mousp1):
                pass
            elif bp[0] == 0 and not mousp and (mousp2 and mousp1):
                mousp = True
                self.rfa()

            self.movemiddle(bp, pos)

    def pickupcamera(self):
        mpos = pg.Vector2(pg.mouse.get_pos()) / self.size * image1size
        closeindex = self.closestcameraindex()

        self.heldindex = closeindex
        self.held = True
        self.camoffset = pg.Vector2(toarr(self.data["CM"]["cameras"][self.heldindex], "point")) - mpos

    def placecamera(self):
        self.held = False

    def getcamerarect(self, cam):
        pos = pg.Vector2(toarr(cam, "point"))
        p = (pos / image1size) * self.size + self.field.rect.topleft + pg.Vector2(self.xoffset * self.size,
                                                                                  self.yoffset * self.size)
        return pg.Rect([p, [camw * self.size, camh * self.size]])

    def rendercameras(self):
        closest = self.closestcameraindex()
        for indx, cam in enumerate(self.data["CM"]["cameras"]):

            rect = self.getcamerarect(cam)
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


            if "quads" not in self.data["CM"]:
                self.data["CM"]["quads"] = []
                for _ in self.data["CM"]["cameras"]:
                    self.data["CM"]["quads"].append([[0, 0], [0, 0], [0, 0], [0, 0]])
            col = camera_notheld
            if indx == self.heldindex and self.held:
                col = camera_held

            quads = self.data["CM"]["quads"][indx]

            newquads = quads.copy()

            for i, q in enumerate(quads):
                n = [0, 0]
                nq = q[0] % 360
                n[0] = math.sin(math.radians(nq)) * q[1] * self.size * 5
                n[1] = -math.cos(math.radians(nq)) * q[1] * self.size * 5
                newquads[i] = n

            tl = pg.Vector2(rect.topleft) + pg.Vector2(newquads[0])
            tr = pg.Vector2(rect.topright) + pg.Vector2(newquads[1])
            br = pg.Vector2(rect.bottomright) + pg.Vector2(newquads[2])
            bl = pg.Vector2(rect.bottomleft) + pg.Vector2(newquads[3])

            if indx == closest and not self.held:
                quadindx = self.getquad(closest)

                vec = pg.Vector2([tl, tr, br, bl][quadindx])

                pg.draw.line(self.surface, camera_notheld, rect.center, vec, self.size // 3)

                rects = [rect.topleft, rect.topright, rect.bottomright, rect.bottomleft]
                pg.draw.line(self.surface, camera_held, rects[quadindx], vec, self.size // 3)

                pg.draw.circle(self.surface, camera_held, vec, self.size * 3, self.size // 3)

            pg.draw.polygon(self.surface, col, [tl, bl, br, tr], self.size // 3)

    def deletecamera(self):
        if len(self.data["CM"]["cameras"]) > 0 and self.heldindex < len(self.data["CM"]["cameras"]) and self.held:
            self.data["CM"]["cameras"].pop(self.heldindex)
            self.data["CM"]["quads"].pop(self.heldindex)
            self.held = False

    def addcamera(self):
        self.data["CM"]["cameras"].append(makearr([0, 0], "point"))
        self.data["CM"]["quads"].append([[0, 0], [0, 0], [0, 0], [0, 0]])
        self.heldindex = len(self.data["CM"]["cameras"]) - 1
        self.held = True
        self.camoffset = pg.Vector2(0, 0)

    def closestcameraindex(self):
        mpos = pg.Vector2(pg.mouse.get_pos())

        closeindex = 0
        dist = 10000

        for indx, cam in enumerate(self.data["CM"]["cameras"]):
            center = pg.Vector2(self.getcamerarect(cam).center)
            dist2 = center.distance_to(mpos)
            if dist2 < dist:
                dist = dist2
                closeindex = indx
        return closeindex

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

    def getquad(self, indx):
        mpos = pg.Vector2(pg.mouse.get_pos())
        rect = self.getcamerarect(self.data["CM"]["cameras"][indx])

        dist = [pg.Vector2(i).distance_to(mpos) for i in [rect.topleft, rect.topright, rect.bottomright, rect.bottomleft]]

        closest = dist.index(min(dist))

        return (closest)

    def addup(self):
        if not self.held:
            cam = self.closestcameraindex()
            quadindx = self.getquad(self.closestcameraindex())
            self.data["CM"]["quads"][cam][quadindx][1] = round(min(self.data["CM"]["quads"][cam][quadindx][1] + settings[self.menu]["addspeed"], 1), 4)

    def adddown(self): #ddddddddddd
        if not self.held:
            cam = self.closestcameraindex()
            quadindx = self.getquad(self.closestcameraindex())
            self.data["CM"]["quads"][cam][quadindx][1] = round(
                max(self.data["CM"]["quads"][cam][quadindx][1] - settings[self.menu]["addspeed"], 0), 4)

    def addleft(self):
        if not self.held:
            cam = self.closestcameraindex()
            quadindx = self.getquad(self.closestcameraindex())
            self.data["CM"]["quads"][cam][quadindx][0] = math.floor(self.data["CM"]["quads"][cam][quadindx][0] -
                                                          settings[self.menu]["rotatespeed"]) % 360

    def addright(self):
        if not self.held:
            cam = self.closestcameraindex()
            quadindx = self.getquad(self.closestcameraindex())
            self.data["CM"]["quads"][cam][quadindx][0] = math.ceil(self.data["CM"]["quads"][cam][quadindx][0] + settings[self.menu]["rotatespeed"]) % 360