import math

from menuclass import *
from lingotojson import *

error = settings["global"]["snap_error"] # snap error

class CE(menu_with_field):
    def __init__(self, surface: pg.surface.Surface, data):
        self.menu = "CE"
        super().__init__(surface, data, "CE")

        self.held = False
        self.heldindex = 0
        self.drawcameras = True
        self.camoffset = pg.Vector2(0, 0)

        self.init()
        self.rfa()
        self.blit()
        self.resize()

    def blit(self):
        super().blit()
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
                for indx, camera in enumerate(self.data["CM"]["cameras"]):
                    if indx == self.heldindex:
                        continue
                    xpos, ypos = toarr(camera, "point")
                    valx, valy = val
                    if xpos - error < valx < xpos + error:
                        val[0] = xpos
                    if ypos - error < valy < ypos + error:
                        val[1] = ypos
                val = makearr(val, "point")
                self.data["CM"]["cameras"][self.heldindex] = val

            if bp[0] == 1 and self.mousp and (self.mousp2 and self.mousp1):
                self.mousp = False
                if not self.held:
                    self.pickupcamera()
                else:
                    self.placecamera()
            elif bp[0] == 1 and not self.mousp and (self.mousp2 and self.mousp1):
                pass
            elif bp[0] == 0 and not self.mousp and (self.mousp2 and self.mousp1):
                self.mousp = True
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
        return getcamerarect(self, cam)

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
            self.data["CM"]["quads"][cam][quadindx][1] = round(min(self.data["CM"]["quads"][cam][quadindx][1] + self.settings["addspeed"], 1), 4)

    def adddown(self): #ddddddddddd
        if not self.held:
            cam = self.closestcameraindex()
            quadindx = self.getquad(self.closestcameraindex())
            self.data["CM"]["quads"][cam][quadindx][1] = round(
                max(self.data["CM"]["quads"][cam][quadindx][1] - self.settings["addspeed"], 0), 4)

    def addleft(self):
        if not self.held:
            cam = self.closestcameraindex()
            quadindx = self.getquad(self.closestcameraindex())
            self.data["CM"]["quads"][cam][quadindx][0] = math.floor(self.data["CM"]["quads"][cam][quadindx][0] -
                                                          self.settings["rotatespeed"]) % 360

    def addright(self):
        if not self.held:
            cam = self.closestcameraindex()
            quadindx = self.getquad(self.closestcameraindex())
            self.data["CM"]["quads"][cam][quadindx][0] = math.ceil(self.data["CM"]["quads"][cam][quadindx][0] + self.settings["rotatespeed"]) % 360