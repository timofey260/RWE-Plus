import traceback
from menuclass import *
from lingotojson import *
import random

blocks = [
    {"tiles": ["A"], "upper": "dense", "lower": "dense", "tall":1, "freq":5},
    {"tiles": ["B1"], "upper": "espaced", "lower": "dense", "tall": 1, "freq": 5},
    {"tiles": ["B2"], "upper": "dense", "lower": "espaced", "tall": 1, "freq": 5},
    {"tiles": ["B3"], "upper": "ospaced", "lower": "dense", "tall": 1, "freq": 5},
    {"tiles": ["B4"], "upper": "dense", "lower": "ospaced", "tall": 1, "freq": 5},
    {"tiles": ["C1"], "upper": "espaced", "lower": "espaced", "tall": 1, "freq": 5},
    {"tiles": ["C2"], "upper": "ospaced", "lower": "ospaced", "tall": 1, "freq": 5},
    {"tiles": ["E1"], "upper": "ospaced", "lower": "espaced", "tall": 1, "freq": 5},
    {"tiles": ["E2"], "upper": "espaced", "lower": "ospaced", "tall": 1, "freq": 5},
    {"tiles": ["F1"], "upper": "dense", "lower": "dense", "tall": 2, "freq": 1},
    {"tiles": ["F2"], "upper": "dense", "lower": "dense", "tall": 2, "freq": 1},
    {"tiles": ["F1", "F2"], "upper": "dense", "lower": "dense", "tall": 2, "freq": 5},
    {"tiles": ["F3"], "upper": "dense", "lower": "dense", "tall": 2, "freq": 5},
    {"tiles": ["F4"], "upper": "dense", "lower": "dense", "tall": 2, "freq": 5},
    {"tiles": ["G1", "G2"], "upper": "dense", "lower": "ospaced", "tall": 2, "freq": 5},
    {"tiles": ["I"], "upper": "espaced", "lower": "dense", "tall": 1, "freq": 4},
    {"tiles": ["J1"], "upper": "ospaced", "lower": "ospaced", "tall": 2, "freq": 1},
    {"tiles": ["J2"], "upper": "ospaced", "lower": "ospaced", "tall": 2, "freq": 1},
    {"tiles": ["J1", "J2"], "upper": "ospaced", "lower": "ospaced", "tall": 2, "freq": 2},
    {"tiles": ["J3"], "upper": "espaced", "lower": "espaced", "tall": 2, "freq": 1},
    {"tiles": ["J4"], "upper": "espaced", "lower": "espaced", "tall": 2, "freq": 1},
    {"tiles": ["J3", "J4"], "upper": "espaced", "lower": "espaced", "tall": 2, "freq": 2},
    {"tiles": ["B1", "I"], "upper": "espaced", "lower": "dense", "tall": 1, "freq": 2}
]


class TE(MenuWithField):

    def __init__(self, process):
        self.menu = "TE"
        self.tool = 0  # 0 - place, 1 - destroy, 2 - copy

        self.matshow = False

        self.items: ItemData = process.renderer.tiles
        p = json.load(open(path + "patterns.json", "r"))
        if "special" not in self.items.categories:
            self.items.append({"name": "special", "color": black, "items": p["patterns"]})
            for indx, pattern in enumerate(p["patterns"]):
                self.items[-1]["items"][indx]["cat"] = [len(self.items), indx + 1]
        self.blocks = p["blocks"]
        self.brushmode = False
        self.squarebrush = False

        self.tileimage = None
        self.tileimage2 = None
        self.mpos = [0, 0]
        self.cols = False

        self.lastfg = False
        self.brushsize = 1

        super().__init__(process, "TE", False)
        self.drawtiles = True
        self.set("materials 0", "Standard")
        self.labels[2].set_text("Default material: " + self.data["TE"]["defaultMaterial"])

        self.selector = widgets.Selector(self, self.items, "s1", "tiles.txt")
        self.selector.callback = self.selectorset
        self.patternoffset = [0, 0]
        self.patternoffset2 = [0, 0]

        self.rfa()
        #self.rebuttons()
        self.blit()
        self.resize()

    def brush(self):
        self.brushmode = True

    def pencil(self):
        self.brushmode = False

    def GE(self):
        self.sendtoowner("GE")

    def blit(self):
        #pg.draw.rect(self.surface, settings["TE"]["menucolor"], pg.rect.Rect(self.buttonslist[0].xy, [self.buttonslist[0].rect.w, len(self.buttonslist[:-1]) * self.buttonslist[0].rect.h + 1]))
        #for button in self.buttonslist:
        #    button.blitshadow()
        #for i, button in enumerate(self.buttonslist[:-1]):
        #    button.blit(sum(pg.display.get_window_size()) // 120)
        #self.buttonslist[-1].blit(sum(pg.display.get_window_size()) // 100)
        #cir = [self.buttonslist[self.toolindex].rect.x + 3, self.buttonslist[self.toolindex].rect.y + self.buttonslist[self.toolindex].rect.h / 2]
        #pg.draw.circle(self.surface, cursor, cir, self.buttonslist[self.toolindex].rect.h / 2)
        self.selector.blit()
        super().blit()
        mpos = self.mousepos
        if self.onfield and self.tileimage is not None:
            # cords = [math.floor(self.mousepos[0] / self.size) * self.size, math.floor(self.mousepos[1] / self.size) * self.size]
            # self.surface.blit(self.tools, pos, [curtool, graphics["tilesize"]])
            pos2 = self.pos2
            posoffset = self.posoffset
            fg = self.findparampressed("force_geometry")

            if self.tileimage["tp"] != "pattern":
                cposx = int(pos2.x) - int((self.tileimage["size"][0] * .5) + .5) * self.size + self.size
                cposy = int(pos2.y) - int((self.tileimage["size"][1] * .5) + .5) * self.size + self.size

                cposxo = int(posoffset.x) - int((self.tileimage["size"][0] * .5) + .5) + 1
                cposyo = int(posoffset.y) - int((self.tileimage["size"][1] * .5) + .5) + 1

                if posoffset != self.mpos or self.lastfg != fg:
                    self.cols = self.test_cols(cposxo, cposyo)
                    self.mpos = posoffset
                    self.lastfg = fg
                    self.labels[1].set_text(f"X: {posoffset.x}, Y: {posoffset.y}, Z: {self.layer + 1}")
                    if self.canplaceit(posoffset.x, posoffset.y, posoffset.x, posoffset.y):
                        self.labels[0].set_text(
                            "Tile: " + str(self.data["TE"]["tlMatrix"][int(posoffset.x)][int(posoffset.y)][self.layer]))

                bord = self.size // image1size + 1
                if self.cols and self.tool == 0:
                    pg.draw.rect(self.surface, canplace, [[cposx - bord, cposy - bord],
                                                          [self.tileimage["image"].get_width() + bord * 2,
                                                           self.tileimage["image"].get_height() + bord * 2]], bord)
                elif self.tool == 2:
                    pg.draw.rect(self.surface, blue, [[cposx - bord, cposy - bord],
                                                             [self.tileimage["image"].get_width() + bord * 2,
                                                              self.tileimage["image"].get_height() + bord * 2]], bord)
                else:
                    pg.draw.rect(self.surface, cannotplace, [[cposx - bord, cposy - bord],
                                                             [self.tileimage["image"].get_width() + bord * 2,
                                                              self.tileimage["image"].get_height() + bord * 2]], bord)
                if self.tool == 0:
                    self.surface.blit(self.tileimage["image"], [cposx, cposy])
                    self.printcols(cposxo, cposyo, self.tileimage)
            elif self.tileimage["ptype"] == "placer4":
                cposxo = int(posoffset.x) - int((self.tileimage["size"] * .5) + .5) + 1
                cposyo = int(posoffset.y) - int((self.tileimage["size"] * .5) + .5) + 1
                cposxo = cposxo // self.tileimage["size"] * self.tileimage["size"] + self.patternoffset[0]
                cposyo = cposyo // self.tileimage["size"] * self.tileimage["size"] + self.patternoffset[1]

                cposx = (cposxo + self.xoffset) * self.size + self.field.rect.x
                cposy = (cposyo + self.yoffset) * self.size + self.field.rect.y

                if self.findparampressed("move_patternoffset"):
                    self.patternoffset = [self.posoffset.x % self.tileimage["size"], self.posoffset.y % self.tileimage["size"]]
                    self.renderpatgrid()
                else:
                    pg.draw.rect(self.surface, canplace if self.tool == 0 else cannotplace, [[cposx - 2, cposy - 2],
                                                      [self.tileimage["size"] * self.size + 4,
                                                       self.tileimage["size"] * self.size + 4]], 2)
            else:
                cposxo = int(posoffset.x) - 2
                cposyo = int(posoffset.y) - 2
            bp = self.getmouse
            if self.brushmode:
                if self.squarebrush:
                    rect = pg.Rect([pos2, [self.brushsize * self.size, self.brushsize * self.size]])
                    pg.draw.rect(self.surface, select, rect, 3)
                else:
                    pg.draw.circle(self.surface, select, pos2+pg.Vector2(self.size/2), self.size * self.brushsize, 5)
            if bp[0] == 1 and self.mousp and (self.mousp2 and self.mousp1):
                self.mousp = False
                self.emptyarea()
            elif bp[0] == 1 and not self.mousp and (self.mousp2 and self.mousp1):
                # if (0 <= posoffset[0] < self.levelwidth) and (0 <= posoffset[1] < self.levelheight):
                #     pass
                if self.tileimage["tp"] != "pattern":
                    if self.tool == 0:
                        if self.brushmode:
                            self.brushpaint(pg.Vector2(cposxo, cposyo))
                        elif self.cols:
                            self.place(cposxo, cposyo, True)
                    elif self.tool == 1:
                        if self.brushmode:
                            self.brushdestroy(pg.Vector2(cposxo, cposyo))
                        else:
                            self.destroy(posoffset.x, posoffset.y)
                elif self.tileimage["tp"] == "pattern":
                    self.insertpattern_pen(cposxo, cposyo)
            elif bp[0] == 0 and not self.mousp and (self.mousp2 and self.mousp1):
                self.detecthistory(["TE", "tlMatrix"], not fg)
                if fg:
                    self.detecthistory(["GE"])
                self.fieldadd.fill(white)
                self.mousp = True
                self.renderer.tiles_render_area(self.area, self.layer)
                self.renderer.geo_render_area(self.area, self.layer)
                self.rfa()

            self.movemiddle(bp)

            if bp[2] == 1 and self.mousp2 and (self.mousp and self.mousp1):
                self.mousp2 = False
                self.rectdata = [posoffset, pg.Vector2(0, 0), pos2]
                self.emptyarea()
            elif bp[2] == 1 and not self.mousp2 and (self.mousp and self.mousp1):
                self.rectdata[1] = posoffset - self.rectdata[0]
                rect = self.vec2rect(self.rectdata[2], pos2)
                tx = f"{int(rect.w / self.size)}, {int(rect.h / self.size)}"
                widgets.fastmts(self.surface, tx, *mpos, white)
                pg.draw.rect(self.surface, select, rect, 5)
            elif bp[2] == 0 and not self.mousp2 and (self.mousp and self.mousp1):
                # self.rectdata = [self.rectdata[0], posoffset]
                rect = self.vec2rect(self.rectdata[0], posoffset)
                if self.tileimage["tp"] != "pattern" and self.tool != 2:
                    for x in range(int(rect.w)):
                        for y in range(int(rect.h)):
                            if self.tool == 0:
                                self.place(x + rect.x, y + rect.y)
                            elif self.tool == 1:
                                self.destroy(x + rect.x, y + rect.y)
                elif self.tool == 2:  # copy
                    history = []
                    for x in range(int(rect.w)):
                        for y in range(int(rect.h)):
                            xpos, ypos = x + rect.x, y + rect.y
                            block = self.data["TE"]["tlMatrix"][xpos][ypos][self.layer]
                            if block["tp"] == "material" or block["tp"] == "tileHead":
                                history.append([x, y, block])
                    pyperclip.copy(str(history))
                elif self.tool == 0 and self.tileimage["tp"] == "pattern":
                    self.insertpattern_rect(rect)
                self.detecthistory(["TE", "tlMatrix"])
                if fg:
                    self.detecthistory(["GE"])
                self.renderer.tiles_render_area(self.area, self.layer)
                self.renderer.geo_render_area(self.area, self.layer)
                self.rfa()
                self.mousp2 = True
        self.selector.blittooltip()
        if pg.key.get_pressed()[pg.K_LCTRL]:
            try:
                geodata: list = eval(pyperclip.paste())
                if type(geodata) != list:
                    return
                pos = self.field.rect.topleft + (self.pos * self.size if self.onfield else pg.Vector2(0, 0))
                geodata.sort(key=lambda x: x[0])
                sizex = geodata[-1][0] + 1
                geodata.sort(key=lambda y: y[1])
                sizey = geodata[-1][1] + 1
                rect = pg.Rect([pos, pg.Vector2(sizex, sizey) * self.size])
                pg.draw.rect(self.surface, select, rect, 5)
            except:
                pass

    def insertpattern_rect(self, rect):
        saved = self.tileimage
        savedtool = saved["nm"]
        savedcat = saved["category"]
        savedata = [self.selector.currentcategory, self.selector.currentitem, self.selector.show]
        match self.tileimage["ptype"]:
            case "patternbox":
                self.pattern_patternbox(rect)
            case "randchance":
                self.pattern_randchance(rect)
            case "placer4":
                for y in range(int(rect.h)):
                    for x in range(int(rect.w)):
                        self.pattern_placer4(x + rect.x, y + rect.y)
            case _:
                return
        self.selector.currentcategory, self.selector.currentitem, self.selector.show = savedata
        self.set(savedcat, savedtool)
        self.selector.recreate()

    def insertpattern_pen(self, xpos, ypos):
        saved = self.tileimage
        savedtool = saved["nm"]
        savedcat = saved["category"]
        savedata = [self.selector.currentcategory, self.selector.currentitem, self.selector.show]
        stool = self.tool
        match self.tileimage["ptype"]:
            case "placer4":
                self.pattern_placer4(xpos, ypos)
            case _:
                return
        self.selector.currentcategory, self.selector.currentitem, self.selector.show = savedata
        self.set(savedcat, savedtool)
        self.tool = stool
        self.selector.recreate()


    def pattern_placer4(self, xpos, ypos, init=True):
        if xpos < 0 or xpos > self.levelwidth or ypos < 0 or ypos > self.levelheight:
            return
        size = self.tileimage["size"]
        conf = self.tileimage["conf"]
        add = self.tileimage["addtiles"]
        allequal = self.tileimage.get("allequal", True)
        geocount = self.tileimage.get("count_geo_as_tile", [])
        geonotcount = self.tileimage.get("count_geo_as_nottile", [])
        tile = self.items[conf[""]]

        saved = self.tileimage
        savedtool = saved["nm"]
        savedcat = saved["category"]
        savedata = [self.selector.currentcategory, self.selector.currentitem, self.selector.show]
        stool = self.tool

        def gettile(xp, yp):
            if xp < 0 or xp > self.levelwidth or yp < 0 or yp > self.levelheight:
                return None
            if self.data.TE_data(xp, yp, self.layer)["tp"] == "tileBody":
                a = toarr(self.data.TE_data(xp, yp, self.layer)["data"][0], "point")
                return gettile(a[0] - 1, a[1] - 1)
            elif self.data.TE_data(xp, yp, self.layer)["tp"] == "tileHead":
                return self.items[self.data.TE_data(xp, yp, self.layer)["data"][1]]
            return None

        def isplaceretile(xp, yp) -> bool:
            if xp < 0 or xp > self.levelwidth or yp < 0 or yp > self.levelheight:
                return False
            geotile = self.data.GE_data(xp, yp, self.layer)[0]
            if geotile in geocount:
                return True
            elif geotile in geonotcount:
                return False
            tile = gettile(xp, yp)
            if tile is None:
                return False
            return tile["nm"] in conf.values() or tile["nm"] in add

        if self.tool == 0 or not init:
            self.set(tile["category"], tile["nm"], False, False)
            if not self.test_cols(xpos, ypos):
                return

            connectioncode = "N" if isplaceretile(xpos, ypos - size) else ""
            connectioncode += "E" if isplaceretile(xpos + size, ypos) else ""
            connectioncode += "S" if isplaceretile(xpos, ypos + size) else ""
            connectioncode += "W" if isplaceretile(xpos - size, ypos) else ""

            tile = self.items[conf[connectioncode]]
            self.set(tile["category"], tile["nm"], False, False)
            self.tileimage["image"] = pg.transform.scale(self.tileimage["image"],
                               [self.tileimage["image"].get_width() / spritesize * self.size,
                                self.tileimage["image"].get_height() / spritesize * self.size])
            if tile["size"][0] < size or tile["size"][1] < size:
                for xp in range(size // tile["size"][0]):
                    for yp in range(size // tile["size"][1]):
                        self.place(xpos + xp, ypos + yp, True)
            else:
                self.place(xpos, ypos, True)
        elif self.tool == 1:
            self.destroy(xpos, ypos, destroycolor=gray)
        if init:
            for i in col4:
                if isplaceretile(xpos + i[0] * size, ypos + i[1] * size):
                    if not allequal:
                        for xp in range(size):
                            for yp in range(size):
                                self.destroy(xpos + i[0] * size + xp, ypos + i[1] * size + yp, destroycolor=darkgray)
                    else:
                        self.destroy(xpos + i[0] * size, ypos + i[1] * size, destroycolor=darkgray)
                    self.selector.currentcategory, self.selector.currentitem, self.selector.show = savedata
                    self.set(savedcat, savedtool, False)
                    self.tool = stool
                    self.selector.recreate()
                    self.pattern_placer4(xpos + i[0] * size, ypos + i[1] * size, False)
        self.selector.currentcategory, self.selector.currentitem, self.selector.show = savedata
        self.set(savedcat, savedtool, False)
        self.tool = stool
        self.selector.recreate()



    def pattern_randchance(self, rect):
        existingblocks = []
        for k, v in self.tileimage["randconf"].items():
            item = self.items[k]
            if item is None:
                continue
            existingblocks.append([item, k, v])
        for y in range(int(rect.h)):
            for x in range(int(rect.w)):
                selecteditem = existingblocks[random.choices([i for i in range(len(existingblocks))], [i[2] for i in existingblocks])[0]][0]
                self.set(selecteditem["category"], selecteditem["nm"], False, False)
                self.place(x + rect.x, y + rect.y)

    def pattern_patternbox(self, rect):
        saved = self.tileimage
        for y in range(int(rect.h)):
            for x in range(int(rect.w)):
                if x == 0 and y == 0:
                    self.set(self.blocks["cat"], self.blocks["NW"], False, False)
                elif x == rect.w - 1 and y == 0:
                    self.set(self.blocks["cat"], self.blocks["NE"], False, False)
                elif x == 0 and y == rect.h - 1:
                    self.set(self.blocks["cat"], self.blocks["SW"], False, False)
                elif x == rect.w - 1 and y == rect.h - 1:
                    self.set(self.blocks["cat"], self.blocks["SE"], False, False)

                elif x == 0:
                    self.set(self.blocks["cat"], self.blocks["W"], False, False)
                elif y == 0:
                    self.set(self.blocks["cat"], self.blocks["N"], False, False)
                elif x == rect.w - 1:
                    self.set(self.blocks["cat"], self.blocks["E"], False, False)
                elif y == rect.h - 1:
                    self.set(self.blocks["cat"], self.blocks["S"], False, False)
                else:
                    continue
                self.place(x + rect.x, y + rect.y)
        skip = False
        lastch = random.choice(blocks)
        for y in range(1, int(rect.h) - 1):
            if skip:
                skip = False
                continue
            ch = random.choice(blocks)
            while ch["upper"] != lastch["lower"] or ch["tiles"] == lastch["tiles"]:
                ch = random.choice(blocks)
            if y == self.rectdata[1].y - 2 and ch["tall"] == 2:
                while ch["upper"] != lastch["lower"] or ch["tall"] == 2 or ch["tiles"] == lastch["tiles"]:
                    ch = random.choice(blocks)
            lastch = ch.copy()
            if ch["tall"] == 2:
                skip = True
            for x in range(1, int(rect.w) - 1):
                n = 0
                if len(ch["tiles"]) > 1:
                    n = x % len(ch["tiles"]) - 1
                self.set(saved["patcat"], saved["prefix"] + ch["tiles"][n], render=False)
                self.place(x + rect.x, y + rect.y)

    def togglebrush(self):
        self.squarebrush = not self.squarebrush

    def brushp(self):
        self.brushsize += 1

    def brushm(self):
        self.brushsize = max(self.brushsize-1, 1)

    def brushpaint(self, pos: pg.Vector2):
        if self.squarebrush:
            for xp in range(self.brushsize):
                for yp in range(self.brushsize):
                    vecx = int(pos.x) + xp
                    vecy = int(pos.y) + yp
                    self.place(vecx, vecy, True)
        else:
            for xp, xd in enumerate(self.data["GE"]):
                for yp, yd in enumerate(xd):
                    vec = pg.Vector2(xp, yp)
                    dist = pos.distance_to(vec)
                    if dist <= self.brushsize and self.area[xp][yp]:
                        self.place(int(vec.x), int(vec.y), True)

    def brushdestroy(self, pos: pg.Vector2):  # not optimal fix but today i'm lazy
        if self.squarebrush:
            for xp in range(self.brushsize):
                for yp in range(self.brushsize):
                    vecx = int(pos.x) + xp
                    vecy = int(pos.y) + yp
                    self.destroy(vecx, vecy)
        else:
            for xp, xd in enumerate(self.data["GE"]):
                for yp, yd in enumerate(xd):
                    vec = pg.Vector2(xp, yp)
                    dist = pos.distance_to(vec)
                    if dist <= self.brushsize and self.area[xp][yp]:
                        self.destroy(xp, yp)

    def cats(self):
        self.selector.categories()

    def pastedata(self):
        try:
            geodata = eval(pyperclip.paste())
            if type(geodata) != list or len(pyperclip.paste()) <= 2:
                print("Error pasting data!")
                return
            self.emptyarea()
            for block in geodata:
                blockx, blocky, data = block
                if data["tp"] == "material":
                    name = data["data"]
                else:
                    name = data["data"][1]
                cat = self.items[name]["category"]
                self.set(cat, name, False)
                # w, h = self.tileimage["size"]
                # px = blockx - int((w * .5) + .5) - 1
                # py = blocky - int((h * .5) + .5) - 1
                pa = pg.Vector2(0, 0)
                if self.field.rect.collidepoint(self.mousepos):
                    pa = self.pos
                self.place(blockx - self.xoffset + int(pa.x), blocky - self.yoffset + int(pa.y))
            else:
                self.selector.setcat(self.items.categories.index(cat))
            self.detecthistory(["TE", "tlMatrix"])
            self.renderer.tiles_render_area(self.area, self.layer)
            self.rfa()
        except:
            traceback.print_exc()
            log_to_load_log(traceback.format_exc(), True)
            print("Error pasting data!")

    def findcat(self, itemname):
        return self.items[itemname]["category"]

    def copytool(self):
        self.tool = 2

    def resize(self):
        super().resize()
        if hasattr(self, "field"):
            self.field.resize()
            self.renderfield()

    def renderfield(self):
        self.fieldadd = pg.transform.scale(self.fieldadd,
                                           [self.levelwidth * self.size, self.levelheight * self.size])
        self.fieldadd.fill(white)
        super().renderfield()
        if self.tileimage is not None and self.tileimage["tp"] != "pattern":
            self.tileimage["image"] = pg.transform.scale(self.tileimage2["image"], [self.size * self.tileimage2["size"][0],
                                                                                self.size * self.tileimage2["size"][1]])
            self.tileimage["image"].set_colorkey(white)

    def renderpatgrid(self):
        w, h = self.f.get_size()
        px = self.patternoffset[0] * self.size
        py = self.patternoffset[1] * self.size
        sx = int(self.field.rect.x + self.offset.x * self.size)
        sy = int(self.field.rect.y + self.offset.y * self.size)
        for x in range(sx, self.field.rect.bottomright[0], self.size * self.tileimage["size"]):
            pg.draw.line(self.surface, grid, [x + px, sy + py], [x + px, sy + h + py])
        for y in range(sy, self.field.rect.bottomright[1], self.size * self.tileimage["size"]):
            pg.draw.line(self.surface, grid, [sx + px, y + py], [sx + w + px, y + py])

    def lt(self):
        self.selector.left()

    def rt(self):
        self.selector.right()

    def dt(self):
        self.selector.down()

    def ut(self):
        self.selector.up()

    def changematshow(self):
        self.selector.catswap()

    def showfavs(self):
        self.selector.favourites()

    def selectorset(self, buttondata):
        self.set(buttondata["category"], buttondata["nm"])

    def addtofavs(self):
        self.selector.addtofavs()

    def set(self, cat, name, render=True, usefavs=True):
        self.tool = 0
        if usefavs and hasattr(self, "selector") and self.selector.show == "favs":
            i = self.selector._favourites[cat, name]
        else:
            i = self.items[cat, name]
        if hasattr(self, "selector"):
            self.selector.setbyname(name, fromfavs=usefavs, category=cat)
        if i is not None and i["nm"] == name:
            self.tileimage2 = i.copy()
            if self.tileimage2["tp"] != "pattern" and render:
                self.tileimage2["image"] = i["image"].copy()
                self.tileimage2["image"].set_alpha(100)
                self.tileimage = self.tileimage2.copy()
                self.tileimage["image"] = pg.transform.scale(self.tileimage2["image"],
                                                             [self.size * self.tileimage2["size"][0],
                                                              self.size * self.tileimage2["size"][1]])
                self.tileimage["image"].set_colorkey(white)
            else:
                self.tileimage = self.tileimage2.copy()
            if render:
                self.recaption()
            return

    def test_cols(self, x, y) -> bool:
        force_place = self.findparampressed("force_place")
        force_geo = self.findparampressed("force_geometry") or force_place
        w, h = self.tileimage["size"]
        sp = self.tileimage["cols"][0]
        sp2 = self.tileimage["cols"][1]
        px = x + int((w * .5) + .5) - 1  # center coordinates
        py = y + int((h * .5) + .5) - 1
        if px >= self.levelwidth or py >= self.levelheight or px < 0 or py < 0:
            return False
        #if x + w > self.levelwidth or y + h > self.levelheight or x < 0 or y < 0:
        #    return False
        if "material" in self.tileimage["tags"]:
            return (self.data["GE"][x][y][self.layer][0] not in [0] or force_geo) \
                and (self.data["TE"]["tlMatrix"][x][y][self.layer]["tp"] == "default"
                or force_place)
        for x2 in range(w):
            for y2 in range(h):
                csp = sp[x2 * h + y2]
                xpos = int(x + x2)
                ypos = int(y + y2)
                if xpos >= self.levelwidth or ypos >= self.levelheight or xpos < 0 or ypos < 0:
                    continue
                if csp != -1:
                    tp = self.data["TE"]["tlMatrix"][xpos][ypos][self.layer]["tp"]
                    if tp != "default" and (not force_place or tp == "tileHead"):
                        return False
                    if self.data["GE"][xpos][ypos][self.layer][0] != csp and not force_geo:
                        return False
                if sp2 != 0:
                    if self.layer + 1 <= 2:
                        csp2 = sp2[x2 * h + y2]
                        if csp2 != -1:
                            tp = self.data["TE"]["tlMatrix"][xpos][ypos][self.layer + 1]["tp"]
                            if tp != "default" and (not force_place or tp == "tileHead"):
                                return False
                            if self.data["GE"][xpos][ypos][self.layer + 1][0] != csp2 and not force_geo:
                                return False

        return True
        # self.data["TE"]

    def printcols(self, x, y, tile, prev=False):
        def printtile(sft, color):
            if prev:
                px = x2 * self.size + self.field.rect.x + sft
                py = y2 * self.size + self.field.rect.y + sft
            else:
                px = (x + x2 + self.xoffset) * self.size + self.field.rect.x + sft
                py = (y + y2 + self.yoffset) * self.size + self.field.rect.y + sft
            match csp:
                case 1:
                    pg.draw.rect(self.surface, color, [px, py, self.size, self.size], shift)
                case 0:
                    pg.draw.circle(self.surface, color, [px + self.size / 2, py + self.size / 2], self.size / 2, shift)
                case 2:
                    pg.draw.polygon(self.surface, color,
                                    [[px, py], [px, py + self.size], [px + self.size, py + self.size]], shift)
                case 3:
                    pg.draw.polygon(self.surface, color,
                                    [[px, py + self.size], [px + self.size, py + self.size], [px + self.size, py]],
                                    shift)
                case 4:
                    pg.draw.polygon(self.surface, color,
                                    [[px, py], [px, py + self.size], [px + self.size, py]], shift)
                case 5:
                    pg.draw.polygon(self.surface, color,
                                    [[px, py], [px + self.size, py + self.size], [px + self.size, py]], shift)

        w, h = tile["size"]
        sp = tile["cols"][0]
        sp2 = tile["cols"][1]
        shift = self.size // image1size + 1
        px = x + int((w * .5) + .5) - 1  # center coordinates
        py = y + int((h * .5) + .5) - 1
        if px >= self.levelwidth or py >= self.levelheight or px < 0 or py < 0:
            return
        # if self.findparampressed("movepreview"):
        #     if prev:
        #         pg.draw.rect(self.surface, black, [self.field.rect.x, self.field.rect.y, w * self.size, h * self.size], 0)
        #     else:
        #         px = (x + self.xoffset) * self.size + self.field.rect.x
        #         py = (y + self.yoffset) * self.size + self.field.rect.y
        #         pg.draw.rect(self.surface, black, [px, py, w * self.size, h * self.size], 0)
        if self.findparampressed("movepreview"):
            return
        for x2 in range(w):
            for y2 in range(h):
                try:
                    csp = sp[x2 * h + y2]
                except:
                    csp = -1
                printtile(0, layer1)
                if sp2 != 0:
                    try:
                        csp = sp2[x2 * h + y2]
                    except IndexError:
                        csp = -1
                    printtile(shift, layer2)

    def place(self, x, y, render=False):
        fg = self.findparampressed("force_geometry")
        w, h = self.tileimage["size"]
        px = x + int((w * .5) + .5) - 1 # center coordinates
        py = y + int((h * .5) + .5) - 1
        p = makearr(self.tileimage["cat"], "point")
        sp = self.tileimage["cols"][0]
        sp2 = self.tileimage["cols"][1]
        if not self.test_cols(x, y):
            return
        if px > self.levelwidth or py > self.levelheight or px < 0 or py < 0:
            return
        if render:
            self.fieldadd.blit(self.tileimage["image"], [x * self.size, y * self.size])
        for x2 in range(w):
            for y2 in range(h):
                try:
                    csp = sp[x2 * h + y2]
                except:
                    csp = -1
                xpos = int(x + x2)
                ypos = int(y + y2)
                if xpos >= self.levelwidth or ypos >= self.levelheight or xpos < 0 or ypos < 0:
                    continue
                if "material" in self.tileimage["tags"]:
                    self.area[xpos][ypos] = False
                    self.changedata(["TE", "tlMatrix", xpos, ypos, self.layer], {"tp": "material",
                                                                           "data": self.tileimage["nm"]})
                    # self.data["TE"]["tlMatrix"][xpos][ypos][self.layer] = {"tp": "material",
                    #                                                        "data": self.tileimage["nm"]}
                elif xpos == px and ypos == py:
                    self.area[xpos][ypos] = False
                    self.changedata(["TE", "tlMatrix", xpos, ypos, self.layer], {"tp": "tileHead",
                                                                           "data": [p, self.tileimage["nm"]]})
                    # self.data["TE"]["tlMatrix"][xpos][ypos][self.layer] = {"tp": "tileHead",
                    #                                                        "data": [p, self.tileimage["nm"]]}
                elif csp != -1:
                    p = makearr([px + 1, py + 1], "point")
                    # self.area[xpos][ypos] = False
                    self.changedata(["TE", "tlMatrix", xpos, ypos, self.layer], {"tp": "tileBody",
                                                                           "data": [p, self.layer + 1]})
                    # self.data["TE"]["tlMatrix"][xpos][ypos][self.layer] = {"tp": "tileBody",
                    #                                                        "data": [p, self.layer + 1]}
                if fg and csp != -1 or fg and "material" in self.tileimage["tags"]:
                    if csp == -1:
                        csp = 1
                    self.area[xpos][ypos] = False
                    self.changedata(["GE", xpos, ypos, self.layer, 0], csp)
                    # self.data["GE"][xpos][ypos][self.layer][0] = csp

                if sp2 != 0:
                    csp = sp2[x2 * h + y2]
                    if self.layer + 1 <= 2 and csp != -1:
                        p = makearr([px + 1, py + 1], "point")
                        self.changedata(["TE", "tlMatrix", xpos, ypos, self.layer + 1], {"tp": "tileBody",
                                                                                   "data": [p, self.layer + 1]})
                        # self.data["TE"]["tlMatrix"][xpos][ypos][self.layer + 1] = {"tp": "tileBody",
                        #                                                            "data": [p, self.layer + 1]}
                        if fg:
                            self.changedata(["GE", xpos, ypos, self.layer + 1, 0], csp)
                            # self.data["GE"][xpos][ypos][self.layer + 1][0] = csp
        self.mpos = 1
        #if fg:
        #    self.rfa()

    def sad(self):
        if "material" in self.tileimage["tags"]:
            self.changedata(["TE", "defaultMaterial"], self.tileimage["nm"])
            # self.data["TE"]["defaultMaterial"] = self.tileimage["nm"]
        self.labels[2].set_text("Default material: " + self.data["TE"]["defaultMaterial"])

    def cleartool(self):
        self.tool = 1

    def changetools(self):
        self.tool = abs(1 - self.tool)

    def findtile(self):
        nd = {}
        for catnum, item in enumerate(self.items.data):
            cat = self.items.categories[catnum]
            for i in item["items"]:
                nd[i["nm"]] = cat
        name = self.find(nd, "Select a tile")
        if name is None:
            return
        item = self.items[name]
        self.selector.setbyname(name)
        self.set(item["category"], name)

    def copytile(self):
        posoffset = self.posoffset
        if not 0 <= posoffset.x < self.levelwidth or not 0 <= posoffset.y < self.levelheight:
            return
        tile = self.data["TE"]["tlMatrix"][int(posoffset.x)][int(posoffset.y)][self.layer]

        match tile["tp"]:
            case "default":
                return
            case "material":
                name = tile["data"]
                tile = self.items[name]
                if tile is not None:
                    self.set(tile["category"], tile["nm"])
                    return
            case "tileBody":
                pos = toarr(tile["data"][0], "point")
                pos[0] -= 1
                pos[1] -= 1
                tile = self.data["TE"]["tlMatrix"][pos[0]][pos[1]][tile["data"][1] - 1]

        if tile["tp"] == "tileHead":
            tile = self.items[tile["data"][1]]
            if tile is not None:
                self.set(tile["category"], tile["nm"])
                return
        print("couldn't find tile")

    def detecthistory(self, path, savedata=True):
        if savedata and path == ['TE', 'tlMatrix']:
            super().detecthistory(path, savedata)
            return
        if len(self.historyChanges) <= 0 or len(self.historyChanges) <= 30 and not savedata:
            return
        elif len(self.historyChanges) <= 30 and savedata:
            self.updatehistory()
            return
        # no idea how it works but it works™
        xposes = []
        for i in self.historyChanges:
            if i[0][0] == path[0]:
                if i[0][len(path)] in xposes:
                    continue
                xposes.append(i[0][len(path)])
        beforerows = []
        afterrows = []
        for i in xposes:
            afterrows.append(self.data[*path, i])
            lastdata = PathDict(deepcopy(self.data[*path, i]))
            for indx, item in enumerate(self.historyChanges):
                if item[0][0] == path[0] and item[0][len(path)] == i:
                    lastdata[item[0][len(path)+1:]] = item[1][1]
                    # print(lastdata[item[0][len(path)+1:]])
                    self.historyChanges.remove(item)
            beforerows.append(lastdata.data)
        if savedata:
            self.historyChanges = []
        for indx, i in enumerate(xposes):
            self.historyChanges.append([[*path, i], [afterrows[indx], beforerows[indx]]])
        self.historyChanges.insert(0, [*path] if savedata else [])
        # print(self.historyChanges)
        self.addtohistory()

    def scroll_up(self):
        if self.findparampressed("brush_size_scroll"):
            self.brushp()
        else:
            super().scroll_up()

    def scroll_down(self):
        if self.findparampressed("brush_size_scroll"):
            self.brushm()
        else:
            super().scroll_down()

    @property
    def custom_info(self):
        try:
            return f"{super().custom_info} | Selected tile: {self.tileimage['nm']}"
        except TypeError:
            return super().custom_info
