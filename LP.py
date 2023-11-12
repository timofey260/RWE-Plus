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

    "ltoplleft": pg.SYSTEM_CURSOR_SIZENWSE,
    "ltop": pg.SYSTEM_CURSOR_SIZENS,
    "ltoplright": pg.SYSTEM_CURSOR_SIZENESW,
    "lright": pg.SYSTEM_CURSOR_SIZEWE,
    "lbottomlright": pg.SYSTEM_CURSOR_SIZENWSE,
    "lbottom": pg.SYSTEM_CURSOR_SIZENS,
    "lbottomlleft": pg.SYSTEM_CURSOR_SIZENESW,
    "lleft": pg.SYSTEM_CURSOR_SIZEWE,
    "": pg.SYSTEM_CURSOR_ARROW
}

class LP(MenuWithField):
    def __init__(self, process):
        self.sliders = []
        self.tool = ""  # env, size
        super().__init__(process, "LP")
        for i in self.settings["sliders"]:
            self.sliders.append(widgets.Slider(
                self.surface,
                i[0], i[1], i[2],
                i[3][0], i[3][1], self.data[i[4][0]][i[4][1]], i[3][2]))

        self.lastdata = 0
        self.moveoffset = pg.Vector2(0, 0)
        self.heldpoint = ""
        self.border = [0, 0, self.levelwidth, self.levelheight]
        self.shadowmode = False
        self.shadowfield = None

        self.gw = self.levelwidth
        self.gh = self.levelheight
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
            self.labels[0].originaltext % (
            str(self.data["EX"]["defaultTerrain"] == 1), str(self.data["EX2"]["light"] == 1)))
        self.labels[1].set_text(
            self.labels[1].originaltext % (str(self.btiles), str([self.levelwidth, self.levelheight])))
        self.labels[2].set_text(
            self.labels[2].originaltext % (self.data["WL"]["waterLevel"], str(self.data["WL"]["waterInFront"]==1)))
        for n, i in enumerate(self.sliders):
            if self.data[self.settings["sliders"][n][4][0]][self.settings["sliders"][n][4][1]] != round(i.value): # dam it's big
                self.changedata([self.settings["sliders"][n][4][0], self.settings["sliders"][n][4][1]], round(i.value))
                # self.data[self.settings["sliders"][n][4][0]][self.settings["sliders"][n][4][1]] = round(i.value)

        if self.onfield:
            bp = self.getmouse
            mpos = pg.Vector2(pg.mouse.get_pos())
            posoffset = self.posoffset
            if self.tool == "env":
                self.setcursor(pg.SYSTEM_CURSOR_SIZENS)
            elif self.tool == "size":
                heldpoint, pos = self.get_nearest_held_point()
                self.setcursor(cursorlist[heldpoint if self.heldpoint == "" else self.heldpoint])
                p = (self.offset - pg.Vector2(self.border[0], self.border[1])) * self.size + self.field.rect.topleft
                rect = pg.Rect([p.x, p.y,
                                (self.border[2] + self.border[0]) * self.size,
                                (self.border[3] + self.border[1]) * self.size])
                pg.draw.rect(self.surface, red, rect, 5)
            else:
                self.setcursor()
            if bp[0] == 1 and self.mousp and (self.mousp2 and self.mousp1):
                self.mousp = False
                if self.tool == "env":
                    self.moveoffset.y = self.data["WL"]["waterLevel"] + int(posoffset.y)
                elif self.tool == "size":
                    self.heldpoint = heldpoint
                    self.moveoffset = pos
            elif bp[0] == 1 and not self.mousp and (self.mousp2 and self.mousp1):
                if self.tool == "env":
                    self.changedata(["WL", "waterLevel"], max(int(self.moveoffset.y - posoffset.y), 0))
                    # self.data["WL"]["waterLevel"] = max(int(self.moveoffset.y - posoffset.y), 0)
                elif self.tool == "size":
                    w = self.levelwidth
                    h = self.levelheight
                    chx = 0
                    chy = 0
                    if "btop" in self.heldpoint:
                        self.btiles[1] = min(max(int(self.moveoffset.y + posoffset.y), 0), h - self.btiles[3] - 1)
                        chy = self.btiles[1]
                    if "bbottom" in self.heldpoint:
                        self.btiles[3] = min(max(int(self.moveoffset.y - posoffset.y), 0), h - self.btiles[1] - 1)
                        chy = self.btiles[3]
                    if "bleft" in self.heldpoint:
                        self.btiles[0] = min(max(int(self.moveoffset.x + posoffset.x), 0), w - self.btiles[2] - 1)
                        chx = self.btiles[0]
                    if "bright" in self.heldpoint:
                        self.btiles[2] = min(max(int(self.moveoffset.x - posoffset.x), 0), w - self.btiles[0] - 1)
                        chx = self.btiles[2]

                    bx = (self.btiles[0]+self.btiles[2]+1)
                    by = (self.btiles[1]+self.btiles[3]+1)

                    if "ltop" in self.heldpoint:
                        self.border[1]= -min(int(self.moveoffset.y + posoffset.y), self.levelheight - by)
                        chy = self.border[1]
                    if "lbottom" in self.heldpoint:
                        self.border[3] = max(int(self.moveoffset.y + posoffset.y), by)
                        chy = self.border[3]
                    if "lleft" in self.heldpoint:
                        self.border[0] = -min(int(self.moveoffset.x + posoffset.x), self.levelwidth - bx)
                        chx = self.border[0]
                    if "lright" in self.heldpoint:
                        self.border[2] = max(int(self.moveoffset.x + posoffset.x), bx)
                        chx = self.border[2]

                    self.changedata(["EX2", "extraTiles"], self.btiles, False)
                    # self.data["EX2"]["extraTiles"] = self.btiles
                    widgets.fastmts(self.surface, f"X:{int(chx)}, Y:{int(chy)}", mpos.x, mpos.y, white)
            elif bp[0] == 0 and not self.mousp and (self.mousp2 and self.mousp1):
                if self.tool == "env":
                    self.updatehistory()
                if self.tool == "size":
                    if self.border != [0, 0, self.levelwidth, self.levelheight]:
                        self.cuteverydata(self.border)
                        self.border = [0, 0, self.levelwidth, self.levelheight]

                    self.updatehistory()
                    self.heldpoint = ""
                self.recaption()
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
        po = self.posoffset
        bt = self.btiles
        cx = self.levelwidth // 2
        cy = self.levelheight // 2
        wmp = self.levelwidth - po.x
        hmp = self.levelheight - po.y
        poses = [["btopbleft",     pg.Vector2(left,    top),     pg.Vector2(left-po.x,  top-po.y)],
                 ["bleft",         pg.Vector2(left,    centery), pg.Vector2(left-po.x,  centery)],
                 ["bbottombleft",  pg.Vector2(left,    bottom),  pg.Vector2(left-po.x,  bt[3]+po.y)],
                 ["btop",          pg.Vector2(centerx, top),     pg.Vector2(centerx,    top-po.y)],
                 ["bbottom",       pg.Vector2(centerx, bottom),  pg.Vector2(centerx,    bt[3]+po.y)],
                 ["btopbright",    pg.Vector2(right,   top),     pg.Vector2(bt[2]+po.x, top-po.y)],
                 ["bright",        pg.Vector2(right,   centery), pg.Vector2(bt[2]+po.x, centery)],
                 ["bbottombright", pg.Vector2(right,   bottom),  pg.Vector2(bt[2]+po.x, bt[3]+po.y)],

                 ["ltoplleft",     pg.Vector2(0,               0),                pg.Vector2(-po.x,   -po.y)],
                 ["lleft",         pg.Vector2(0,               cy),               pg.Vector2(-po.x,   cy)],
                 ["lbottomlleft",  pg.Vector2(0,               self.levelheight), pg.Vector2(-po.x,   hmp)],
                 ["ltop",          pg.Vector2(cx,              0),                pg.Vector2(cx,      -po.y)],
                 ["lbottom",       pg.Vector2(cx,              self.levelheight), pg.Vector2(centerx, hmp)],
                 ["ltoplright",    pg.Vector2(self.levelwidth, 0),                pg.Vector2(wmp,     -po.y)],
                 ["lright",        pg.Vector2(self.levelwidth, cy),               pg.Vector2(wmp,     centery)],
                 ["lbottomlright", pg.Vector2(self.levelwidth, self.levelheight), pg.Vector2(wmp,     hmp)]

                 ]
        nearestindex = 0
        nearestdistance = bignum
        nearestpos = poses[0][2]
        mpos = self.posoffset
        for index, item in enumerate(poses):
            pos = item[1]
            distance = mpos.distance_to(pos)
            if distance < nearestdistance:
                nearestpos = item[2]
                nearestindex = index
                nearestdistance = distance
        if nearestdistance > 10:
            return "", poses[0][2]
        return poses[nearestindex][0], nearestpos

    def resize(self):
        super().resize()
        for i in self.sliders:
            i.resize()

    def chparam(self, cat, name):
        self.changedata([cat, name], 1 - self.data[cat][name])
        # self.data[cat][name] = 1 - self.data[cat][name]
        self.updatehistory()

    def chinput(self, cat, name, inputdesc):
        try:
            i = self.askint(f"{inputdesc}({self.data[cat][name]})")
            self.changedata([cat, name], i)
            # self.data[cat][name] = i
        except ValueError:
            print("Invalid input!")

    def changeborder(self):
        self.chparam("EX", "defaultTerrain")

    def changelight(self):
        self.chparam("EX2", "light")

    def water(self):
        self.tool = "env"
        self.recaption()

    def sizing(self):
        self.tool = "size"
        self.recaption()

    def nowater(self):
        self.changedata(["WL", "waterLevel"], -1)
        # self.data["WL"]["waterLevel"] = -1
        self.updatehistory()

    def cuteverydata(self, data):
        x, y, w, h = data
        if x is None or y is None or w is None or h is None:
            print("Not changed")
            return
        self.cutdata(["GE"], x, y, w, h, [[1, []], [1, []], [1, []]])
        # self.data["GE"] = self.cutdata(x, y, w, h, self.data["GE"], [[1, []], [1, []], [1, []]])
        self.cuttiles(x, y, w, h)
        for num, effect in enumerate(self.data["FE"]["effects"]):
            self.cutdata(["FE", "effects", num, "mtrx"], x, y, w, h, 0)
            # self.data["FE"]["effects"][num]["mtrx"] = self.cutdata(x, y, w, h, effect["mtrx"], 0)
        self.recount()
        self.resizeprops(x, y, w, h)
        self.resizeimage(x, y, w, h)
        self.recount_image()
        self.changedata(["EX2", "size"], makearr([self.levelwidth, self.levelheight], "point"))
        # self.data["EX2"]["size"] = makearr([self.levelwidth, self.levelheight], "point")
        self.owner.manager.notify("Done!")
        self.updatehistory()
        self.savef()
        # self.renderer.data = self.data
        self.renderer.set_surface([image1size * self.levelwidth, image1size * self.levelheight])
        self.renderer.render_all(self.layer)

    def recount(self):
        self.gw = self.levelwidth
        self.gh = self.levelheight
        self.recount_image()

    def resizeimage(self, x, y, w, h):
        if self.shadowfield is not None:
            f2 = pg.surface.Surface(
                [(abs(x) + self.gw + ofsleft) * image1size, (abs(y) + self.gh + ofstop) * image1size])
            f2.fill(white)
            f2.blit(self.shadowfield, [x * image1size, y * image1size])
            self.shadowfield = f2.subsurface(
                pg.rect.Rect(0, 0, (self.gw + ofsleft) * image1size, (self.gh + ofstop) * image1size))
            lev = os.path.splitext(self.data["path"])[0] + ".png"
            pg.image.save(self.shadowfield, lev)

    def resizeprops(self, x, y, w, h):
        for indx, prop in enumerate(self.data["PR"]["props"]):
            quads = prop[3]
            newq = []
            c = 0
            for quad in quads:
                pos = toarr(quad, "point")
                pos[0] += x * spritesize
                pos[1] += y * spritesize
                newq.append(makearr(pos, "point"))
                if x > w * image1size and y > h * image1size:
                    c += 1
                if c == 4:
                    self.historypop(["PR", "props"], indx)
                    # self.data["PR"]["props"].pop(indx)
            if prop[4].get("points") is not None:
                newp = []
                for points in prop[4]["points"]:
                    p = toarr(points, "point")
                    p[0] += x * image1size
                    p[1] += y * image1size
                    newp.append(makearr(p, "point"))
                self.changedata(["PR", "props", indx, 4, "points"], newp)
                # self.data["PR"]["props"][indx][4]["points"] = newp
            self.changedata(["PR", "props", indx, 3], newq)
            # self.data["PR"]["props"][indx][3] = newq

    def cuttiles(self, x, y, w, h):
        self.cutdata(["TE", "tlMatrix"], x, y, w, h, [{"tp": "default", "data": 0},
                                                                        {"tp": "default", "data": 0},
                                                                        {"tp": "default", "data": 0}])
        for xp, xv in enumerate(self.data["TE"]["tlMatrix"]):
            for yp, yv in enumerate(xv):
                for layer, item in enumerate(yv):
                    if item["tp"] == "tileBody":
                        dat = toarr(item["data"][0], "point")
                        dat[0] -= x
                        dat[1] -= y
                        if dat[0] < 0 or dat[1] < 0 or dat[0] > self.levelwidth or dat[1] > self.levelheight:
                            self.changedata(["TE", "tlMatrix", xp, yp, layer], {"tp": "default", "data": 0})
                            # cutted[xp][yp][layer] = {"tp": "default", "data": 0}
                        else:
                            self.changedata(["TE", "tlMatrix", xp, yp, layer, "data", 0], makearr(dat, "point"))
                            # cutted[xp][yp][layer]["data"][0] = makearr(dat, "point")
        # self.changedata(["TE", "tlMatrix"], cutted)
        # self.data["TE"]["tlMatrix"] = cutted

    def waterlayer(self):
        self.changedata(["WL", "waterInFront"], 1 - self.data["WL"]["waterInFront"])
        # self.data["WL"]["waterInFront"] = 1 - self.data["WL"]["waterInFront"]
        self.updatehistory()

    def recount_image(self):
        try:
            lev = os.path.splitext(self.data["path"])[0] + ".png"
            self.shadowfield = loadimage(lev)
        except FileNotFoundError:
            self.shadowfield = None

    def cutdata(self, path, x, y, w, h, default_instance):
        # print(x, y, w, h, self.gw, self.gh, self.levelwidth, self.levelheight)
        arr = deepcopy(self.data[path])
        if x >= 0:
            for _ in range(x):
                # self.historyinsert(0, path, [deepcopy(default_instance) for _ in range( self.data[path][0] )])
                arr.insert(0, [deepcopy(default_instance) for _ in range(len(arr[0]))])
        else:
            # for _ in range(x):
            #     self.historypop(path, -1)
            arr = arr[-x:]

        if w != 0 and w != self.gw:
            if w < self.gw:
                # for _ in range(len(self.data[path]) - w):
                #     self.historypop(path, -1)
                arr = arr[:w]
            else:
                for _ in range(w - self.gw):
                    # self.historyappend(path, [deepcopy(default_instance) for _ in range(len(self.data[path][0]))])
                    arr.append([deepcopy(default_instance) for _ in range(len(arr[0]))])

        if y >= 0:
            for i in range(len(arr)):
                for _ in range(y):
                    # self.historyinsert([*path, i], deepcopy(default_instance), 0)
                    arr[i].insert(0, deepcopy(default_instance))
        else:
            for i in range(len(arr)):
                # for _ in range(y):
                #     self.historypop([*path, i], -1)
                arr[i] = arr[i][-y:]

        if h != 0 and h != self.gh:
            for i in range(len(arr)):
                if h < self.gh:
                    # for _ in range(len(self.data[path][i]) - h):
                    #     self.historypop([*path, i], -1)
                    arr[i] = arr[i][:h]
                else:
                    for _ in range(h - self.gh):
                        # self.historyappend([*path, i], deepcopy(default_instance))
                        arr[i].append(deepcopy(default_instance))
        self.changedata(path, arr, False)
        # return arr

    def cutmanually(self):
        try:
            x = self.askint(f"Add or subtract tiles from Left", True)
            y = self.askint(f"Add or subtract tiles from Top", False)
            w = self.askint(f"({self.levelwidth})Width", False)
            h = self.askint(f"({self.levelwidth})Height", False)
            self.cuteverydata([x, y, w, h])
        except ValueError:
            print("Error: non valid answer")

    def btilesmanually(self):
        try:
            x = self.askint(f"({self.btiles[0]})Left", True, self.btiles[0])
            y = self.askint(f"({self.btiles[1]})Top", False, self.btiles[1])
            w = self.askint(f"({self.btiles[2]})Right", False, self.btiles[2])
            h = self.askint(f"({self.btiles[3]})Bottom", False, self.btiles[3])
            self.changedata(["EX2", "extraTiles"], [x, y, w, h], False)
            # self.data["EX2"]["extraTiles"] = [x, y, w, h]
            self.btiles = self.data["EX2"]["extraTiles"]
        except ValueError:
            print("Error: non valid answer")


    @property
    def custom_info(self):
        return f"{super().custom_info} | Current tool: {self.tool} | Level size: {[self.levelwidth], self.levelheight} | Water level: {self.data['WL']['waterLevel']}"

    def onundo(self):
        self.border = [0, 0, self.levelwidth, self.levelheight]
        self.btiles = self.data["EX2"]["extraTiles"]
        self.gw = self.levelwidth
        self.gh = self.levelheight

    def onredo(self):
        self.onundo()
