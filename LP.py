import widgets
from menuclass import *

cursorlist = {
    "btopbleft": pg.SYSTEM_CURSOR_SIZENWSE,
    "btop": pg.SYSTEM_CURSOR_SIZENS,
    "btopbright": pg.SYSTEM_CURSOR_SIZENESW,
    "bright": pg.SYSTEM_CURSOR_SIZEWE,
    "bbottombright": pg.SYSTEM_CURSOR_SIZENWSE,
    "bbottom": pg.SYSTEM_CURSOR_SIZENS,
    "bbottombleft": pg.SYSTEM_CURSOR_SIZENESW,
    "bleft": pg.SYSTEM_CURSOR_SIZEWE,

    "topleft": pg.SYSTEM_CURSOR_SIZENWSE,
    "top": pg.SYSTEM_CURSOR_SIZENS,
    "topright": pg.SYSTEM_CURSOR_SIZENESW,
    "right": pg.SYSTEM_CURSOR_SIZEWE,
    "bottomright": pg.SYSTEM_CURSOR_SIZENWSE,
    "bottom": pg.SYSTEM_CURSOR_SIZENS,
    "bottomleft": pg.SYSTEM_CURSOR_SIZENESW,
    "left": pg.SYSTEM_CURSOR_SIZEWE,
    "": pg.SYSTEM_CURSOR_ARROW
}

class LP(MenuWithField):
    def __init__(self, surface: pg.surface.Surface, renderer: Renderer):
        self.sliders = []
        super().__init__(surface, "LP", renderer)
        for i in self.settings["sliders"]:
            self.sliders.append(widgets.slider(
                self.surface,
                i[0], i[1], i[2],
                i[3][0], i[3][1], self.data[i[4][0]][i[4][1]], i[3][2]))

        self.lastdata = 0
        self.tool = "size"  # env, size
        self.layer = 1 - self.data["WL"]["waterInFront"]
        self.moveoffset = pg.Vector2(0, 0)
        self.heldpoint = ""
        self.resize()

    def blit(self):
        super().blit()
        if self.data["WL"]["waterLevel"] != -1:
            height = self.levelheight * self.size
            width = self.levelwidth * self.size
            top = height - ((wladd + self.data["WL"]["waterLevel"]) * self.size)
            h = height - top + 1
            s = pg.Surface([width, h])
            s.fill(blue)
            s.set_alpha(100)
            self.field.field.blit(s, [self.xoffset * self.size, self.yoffset * self.size + top])
        self.field.blit()
        Menu.blit(self)
        for i in self.sliders:
            i.blit()
        self.labels[0].set_text(
            self.labels[0].originaltext % self.settings["nmd" + str(self.data["EX"]["defaultTerrain"])])
        self.labels[1].set_text(self.labels[1].originaltext % self.settings["nml" + str(self.data["EX2"]["light"])])
        for n, i in enumerate(self.sliders):
            self.data[self.settings["sliders"][n][4][0]][self.settings["sliders"][n][4][1]] = round(i.value)

        if self.onfield:
            bp = self.getmouse
            mpos = pg.Vector2(pg.mouse.get_pos())
            posoffset = self.posoffset
            if self.tool == "env":
                self.setcursor(pg.SYSTEM_CURSOR_SIZENS)
            elif self.tool == "size":
                heldpoint, pos = self.get_nearest_held_point()
                self.setcursor(cursorlist[heldpoint])
            else:
                self.setcursor()
            if bp[0] == 1 and self.mousp and (self.mousp2 and self.mousp1):
                self.mousp = False
                if self.tool == "env":
                    self.moveoffset.y = self.data["WL"]["waterLevel"] + int(posoffset.y)
                elif self.tool == "size":
                    self.heldpoint = heldpoint
                    self.moveoffset = pos - posoffset
            elif bp[0] == 1 and not self.mousp and (self.mousp2 and self.mousp1):
                if self.tool == "env":
                    self.data["WL"]["waterLevel"] = max(int(self.moveoffset.y - posoffset.y), 0)
                elif self.tool == "size":
                    w = self.levelwidth
                    h = self.levelheight
                    chx = 0
                    chy = 0
                    if self.heldpoint.find("btop") != -1:
                        self.btiles[1] = min(max(int(self.moveoffset.y + posoffset.y), 0), h - self.btiles[3] - 1)
                        chy = self.btiles[1]
                    if self.heldpoint.find("bbottom") != -1:
                        self.btiles[3] = min(max(int(self.moveoffset.y - posoffset.y + h), 0), h - self.btiles[1] - 1)
                        chy = self.btiles[3]
                    if self.heldpoint.find("bleft") != -1:
                        self.btiles[0] = min(max(int(self.moveoffset.x + posoffset.x), 0), w - self.btiles[2] - 1)
                        chx = self.btiles[0]
                    if self.heldpoint.find("bright") != -1:
                        self.btiles[2] = min(max(int(self.moveoffset.x - posoffset.x + w), 0), w - self.btiles[0] - 1)
                        chx = self.btiles[2]
                    self.data["EX2"]["extraTiles"] = self.btiles
                    widgets.fastmts(self.surface, f"{int(chx)}, {int(chy)}", mpos.x, mpos.y, white)
            elif bp[0] == 0 and not self.mousp and (self.mousp2 and self.mousp1):
                if self.tool == "env":
                    self.updatehistory([["WL", "waterLevel"]])
                if self.tool == "size":
                    self.heldpoint = ""
                self.mousp = True
                self.rfa()
            self.movemiddle(bp)

    def get_nearest_held_point(self):
        top = self.btiles[1]
        bottom = self.levelheight - self.btiles[3]
        left = self.btiles[0]
        right = self.levelwidth - self.btiles[2]
        centerx = (right - left) // 2 + left
        centery = (bottom - top) // 2 + top
        poses = [["btopbleft", left, top],
                 ["bleft", left, centery],
                 ["bbottombleft", left, bottom],
                 ["btop", centerx, top],
                 ["bbottom", centerx, bottom],
                 ["btopbright", right, top],
                 ["bright", right, centery],
                 ["bbottombright", right, bottom],

                 ["topleft", 0, 0],
                 ["left", 0, self.levelheight // 2],
                 ["bottomleft", 0, self.levelheight],
                 ["top", self.levelwidth // 2, 0],
                 ["bottom", self.levelwidth // 2, self.levelheight],
                 ["topright", self.levelwidth, 0],
                 ["right", self.levelwidth, self.levelheight // 2],
                 ["bottomright", self.levelwidth, self.levelheight]
                 ]
        nearestindex = 0
        nearestdistance = bignum
        nearestpos = pg.Vector2(poses[0][1], poses[0][2])
        mpos = self.posoffset
        for index, item in enumerate(poses):
            pos = pg.Vector2(item[1], item[2])
            distance = mpos.distance_to(pos)
            if distance < nearestdistance:
                nearestpos = pos
                nearestindex = index
                nearestdistance = distance
        return poses[nearestindex][0], nearestpos

    def resize(self):
        super().resize()
        for i in self.sliders:
            i.resize()

    def chparam(self, cat, name):
        self.data[cat][name] = 1 - self.data[cat][name]
        self.updatehistory([[cat, name]])

    def chinput(self, cat, name, inputdesc):
        try:
            i = self.askint(f"{inputdesc}({self.data[cat][name]})")
            self.data[cat][name] = i
        except ValueError:
            print("Invalid input!")

    def changeborder(self):
        self.chparam("EX", "defaultTerrain")

    def changelight(self):
        self.chparam("EX2", "light")

    def water(self):
        self.tool = "env"

    def sizing(self):
        self.tool = "size"

    def nowater(self):
        self.data["WL"]["waterLevel"] = -1
        self.updatehistory([["WL", "waterLevel"]])
