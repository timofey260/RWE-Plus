from menuclass import *
from lingotojson import *


class TE(menu_with_field):

    def __init__(self, surface: pg.surface.Surface, data, items):
        self.menu = "TE"
        self.tool = False # 0  place, 1 - destroy

        self.items = items
        self.buttonslist = []
        self.currentcategory = 0
        self.toolindex = 0

        self.tileimage = None
        self.tileimage2 = None
        self.mpos = [0, 0]
        self.cols = False

        super().__init__(surface, data, "TE")
        self.set("material", "Standard")
        self.init()
        self.labels[2].set_text("Default material: " + self.data["TE"]["defaultMaterial"])
        self.rebuttons()
        self.rfa()
        self.blit()
        self.resize()

    def rfa(self):
        self.renderfield_all(rendersecond=True, items=self.items)

    def blit(self):
        global mousp, mousp2, mousp1

        self.buttonslist[-1].blit(sum(pg.display.get_window_size()) // 100)
        pg.draw.rect(self.surface, settings["TE"]["menucolor"], pg.rect.Rect(self.buttonslist[0].xy, [self.buttonslist[0].rect.w, len(self.buttonslist[:-1]) * self.buttonslist[0].rect.h + 1]))
        for button in self.buttonslist[:-1]:
            button.blit(sum(pg.display.get_window_size()) // 120)
        super().blit()
        cir = [self.buttonslist[self.toolindex].rect.x + 3, self.buttonslist[self.toolindex].rect.y + self.buttonslist[self.toolindex].rect.h / 2]
        pg.draw.circle(self.surface, cursor, cir, self.buttonslist[self.toolindex].rect.h / 2)
        if self.field.rect.collidepoint(pg.mouse.get_pos()) and self.tileimage is not None:
            # cords = [math.floor(pg.mouse.get_pos()[0] / self.size) * self.size, math.floor(pg.mouse.get_pos()[1] / self.size) * self.size]
            # self.surface.blit(self.tools, pos, [curtool, graphics["tilesize"]])

            pos = [math.floor((pg.mouse.get_pos()[0] - self.field.rect.x) / self.size),
                   math.floor((pg.mouse.get_pos()[1] - self.field.rect.y) / self.size)]
            pos2 = [pos[0] * self.size + self.field.rect.x, pos[1] * self.size + self.field.rect.y]
            posoffset = [pos[0] - self.xoffset, pos[1] - self.yoffset]

            cposx = pos2[0] - (self.tileimage["size"][0] // 3) * self.size
            cposy = pos2[1] - (self.tileimage["size"][1] // 3) * self.size

            cposxo = posoffset[0] - (self.tileimage["size"][0] // 3)
            cposyo = posoffset[1] - (self.tileimage["size"][1] // 3)

            if posoffset != self.mpos:
                self.cols = self.test_cols(cposxo, cposyo)
                self.mpos = posoffset
                self.labels[1].set_text(f"X: {posoffset[0]}, Y: {posoffset[1]}, Z: {self.layer + 1}")
                if self.canplace(posoffset[0], posoffset[1], cposxo, cposyo):
                    self.labels[0].set_text(
                        "Tile: " + str(self.data["TE"]["tlMatrix"][posoffset[0]][posoffset[1]][self.layer]))
            bord = 3
            if self.cols and not self.tool:
                pg.draw.rect(self.surface, canplace, [[cposx - bord, cposy - bord],
                                                      [self.tileimage["image"].get_width() + bord * 2,
                                                       self.tileimage["image"].get_height() + bord * 2]], bord)
            else:
                pg.draw.rect(self.surface, cannotplace, [[cposx - bord, cposy - bord],
                                                         [self.tileimage["image"].get_width() + bord * 2,
                                                          self.tileimage["image"].get_height() + bord * 2]], bord)
            if not self.tool:
                self.surface.blit(self.tileimage["image"], [cposx, cposy])
                self.printcols(cposxo, cposyo)
            bp = pg.mouse.get_pressed(3)

            if bp[0] == 1 and mousp and (mousp2 and mousp1):
                mousp = False
            elif bp[0] == 1 and not mousp and (mousp2 and mousp1):
                if (0 <= posoffset[0] < len(self.data["GE"])) and (0 <= posoffset[1] < len(self.data["GE"][0])):
                    pass
                if not self.tool:
                    if self.cols:
                        self.place(cposxo, cposyo)
                        self.fieldadd.blit(self.tileimage["image"],
                                           [cposxo * self.size, cposyo * self.size])
                else:
                    self.destroy(posoffset[0], posoffset[1])
                    pg.draw.rect(self.fieldadd, red, [posoffset[0] * self.size, posoffset[1] * self.size, self.size, self.size])
            elif bp[0] == 0 and not mousp and (mousp2 and mousp1):
                self.fieldadd.fill(white)
                mousp = True
                self.rfa()

            self.movemiddle(bp, pos)

            if bp[2] == 1 and mousp2 and (mousp and mousp1):
                mousp2 = False
                self.rectdata = [posoffset, [0, 0], pos2]
            elif bp[2] == 1 and not mousp2 and (mousp and mousp1):
                self.rectdata[1] = [posoffset[0] - self.rectdata[0][0], posoffset[1] - self.rectdata[0][1]]
                # rect = [[(self.rectdata[0][0] + self.xoffset) * self.size + self.field.rect.x, (self.rectdata[0][1] + self.yoffset) * self.size + self.field.rect.y], [(self.rectdata[1][0] + self.xoffset) * self.size, (self.rectdata[1][1] + self.yoffset) * self.size]]
                rect = [self.rectdata[2], [pos2[0] - self.rectdata[2][0], pos2[1] - self.rectdata[2][1]]]
                pg.draw.rect(self.surface, select, rect, 5)
                ##pg.draw.polygon(self.surface, red, [pos2, [pos2[0], self.rectdata[1][1]], self.rectdata[1], [self.rectdata[1][0], pos2[1]]], 5)
            elif bp[2] == 0 and not mousp2 and (mousp and mousp1):
                # self.rectdata = [self.rectdata[0], posoffset]
                for x in range(self.rectdata[1][0]):
                    for y in range(self.rectdata[1][1]):
                        if not self.tool:
                            self.place(x + self.rectdata[0][0], y + self.rectdata[0][1])
                        else:
                            self.destroy(x + self.rectdata[0][0], y + self.rectdata[0][1])
                self.rfa()
                mousp2 = True

    def rebuttons(self):
        self.buttonslist = []
        btn2 = None
        for count, item in enumerate(self.items[list(self.items.keys())[self.currentcategory]]):
            # rect = pg.rect.Rect([0, count * settings[self.menu]["itemsize"], self.field2.field.get_width(), settings[self.menu]["itemsize"]])
            # rect = pg.rect.Rect(0, 0, 100, 10)
            cat = pg.rect.Rect([settings[self.menu]["buttons"][settings[self.menu]["itemsposindex"]][1][0], 6, 22, 4])
            btn2 = widgets.button(self.surface, cat, settings["global"]["color"], item["category"])

            rect = pg.rect.Rect([settings[self.menu]["buttons"][settings[self.menu]["itemsposindex"]][1][0], count * settings[self.menu]["itemsize"] + settings[self.menu]["buttons"][settings[self.menu]["itemsposindex"]][1][1] + settings[self.menu]["buttons"][settings[self.menu]["itemsposindex"]][1][3] + 4, 22, settings[self.menu]["itemsize"]])
            if item["category"] == "material":
                btn = widgets.button(self.surface, rect, item["color"], item["name"], onpress=self.getmaterial)
            else:
                tooltip = "Size: " + str(item["size"])
                btn = widgets.button(self.surface, rect, item["color"], item["name"], onpress=self.getblock, tooltip=tooltip)
            self.buttonslist.append(btn)
            count += 1
        if btn2 is not None:
            self.buttonslist.append(btn2)
        self.resize()

    def resize(self):
        super().resize()
        if hasattr(self, "field"):
            self.field.resize()
            for i in self.buttonslist:
                i.resize()
            self.renderfield()

    def renderfield(self):
        self.fieldadd = pg.transform.scale(self.fieldadd,
                                           [len(self.data["GE"]) * self.size, len(self.data["GE"][0]) * self.size])
        self.fieldadd.fill(white)
        super().renderfield()
        if self.tileimage is not None:
            self.tileimage["image"] = pg.transform.scale(self.tileimage2["image"], [self.size * self.tileimage2["size"][0],
                                                                                self.size * self.tileimage2["size"][1]])
            self.tileimage["image"].set_colorkey(None)

    def lt(self):
        if self.currentcategory - 1 < 0:
            self.currentcategory = len(self.items) - 1
        else:
            self.currentcategory = self.currentcategory - 1
        self.set(list(self.items)[self.currentcategory], self.items[list(self.items)[self.currentcategory]][0]["name"])
        self.rebuttons()

    def rt(self):
        self.currentcategory = (self.currentcategory + 1) % len(self.items)
        self.set(list(self.items)[self.currentcategory], self.items[list(self.items)[self.currentcategory]][0]["name"])
        self.rebuttons()

    def dt(self):
        for i in self.items[self.tileimage["category"]]:
            if i["cat"][1] == self.tileimage["cat"][1] + 1:
                self.set(i["category"], i["name"])
                return
        self.set(self.tileimage["category"], self.items[self.tileimage["category"]][0]["name"])

    def ut(self):
        for i in self.items[self.tileimage["category"]]:
            if i["cat"][1] == self.tileimage["cat"][1] - 1:
                self.set(i["category"], i["name"])
                return
        self.set(self.tileimage["category"], self.items[self.tileimage["category"]][-1]["name"])

    def getblock(self, text):
        cat = self.buttonslist[-1].text
        self.set(cat, text)

    def getmaterial(self, text):
        cat = self.buttonslist[-1].text
        self.set(cat, text)

    def set(self, cat, name):
        self.tool = 0
        for num, i in enumerate(self.items[cat]):
            if i["name"] == name:
                self.toolindex = num
                self.tileimage2 = i
                self.tileimage2["image"].set_alpha(100)
                self.tileimage = self.tileimage2.copy()

                self.tileimage["image"] = pg.transform.scale(self.tileimage2["image"],
                                                             [self.size * self.tileimage2["size"][0],
                                                              self.size * self.tileimage2["size"][1]])
                self.tileimage["image"].set_colorkey(None)
                return

    def test_cols(self, x, y):
        w, h = self.tileimage["size"]
        sp = self.tileimage["cols"][0]
        sp2 = self.tileimage["cols"][1]
        if x + w > len(self.data["GE"]) or y + h > len(self.data["GE"][0]) or x < 0 or y < 0:
            return False
        if self.tileimage["category"] == "material":
            return self.data["GE"][x][y][self.layer][0] not in [0] and self.data["TE"]["tlMatrix"][x][y][self.layer][
                "tp"] == "default"
        for x2 in range(w):
            for y2 in range(h):
                csp = sp[x2 * h + y2]
                if csp != -1:
                    if self.data["GE"][x + x2][y + y2][self.layer][0] != csp or \
                            self.data["TE"]["tlMatrix"][x + x2][y + y2][self.layer]["tp"] != "default":
                        return False
                if sp2 != 0:
                    if self.layer + 1 <= 2:
                        csp2 = sp2[x2 * h + y2]
                        if csp2 != -1:
                            if self.data["GE"][x + x2][y + y2][self.layer + 1][0] != csp2 or \
                                    self.data["TE"]["tlMatrix"][x + x2][y + y2][self.layer + 1]["tp"] != "default":
                                return False

        return True
        # self.data["TE"]

    def printcols(self, x, y):
        def printtile(sft, color):
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

        w, h = self.tileimage["size"]
        sp = self.tileimage["cols"][0]
        sp2 = self.tileimage["cols"][1]
        shift = self.size // 10
        if x + w > len(self.data["GE"]) or y + h > len(self.data["GE"][0]):
            return
        for x2 in range(w):
            for y2 in range(h):
                csp = sp[x2 * h + y2]
                printtile(0, layer1)
                if sp2 != 0:
                    csp = sp2[x2 * h + y2]
                    printtile(shift, layer2)

    def place(self, x, y):
        px = x + (self.tileimage["size"][0] // 3)
        py = y + (self.tileimage["size"][1] // 3)
        w, h = self.tileimage["size"]
        sp = self.tileimage["cols"][0]
        sp2 = self.tileimage["cols"][1]
        if not self.test_cols(x, y):
            return
        for x2 in range(w):
            for y2 in range(h):
                csp = sp[x2 * h + y2]
                xpos = x + x2
                ypos = y + y2
                if self.tileimage["category"] == "material":
                    self.data["TE"]["tlMatrix"][xpos][ypos][self.layer] = {"tp": "material",
                                                                           "data": self.tileimage["name"]}
                elif x + x2 == px and y + y2 == py:
                    p = makearr(self.tileimage["cat"], "point")
                    self.data["TE"]["tlMatrix"][xpos][ypos][self.layer] = {"tp": "tileHead",
                                                                           "data": [p, self.tileimage["name"]]}
                elif csp != -1:
                    p = makearr([px + 1, py + 1], "point")
                    self.data["TE"]["tlMatrix"][xpos][ypos][self.layer] = {"tp": "tileBody",
                                                                           "data": [p, self.layer + 1]}
                if sp2 != 0:
                    csp = sp2[x2 * h + y2]
                    if self.layer + 1 <= 2 and csp != -1:
                        p = makearr([px + 1, py + 1], "point")
                        self.data["TE"]["tlMatrix"][xpos][ypos][self.layer + 1] = {"tp": "tileBody",
                                                                                   "data": [p, self.layer + 1]}
        self.mpos = 1

    def destroy(self, x, y):
        destroy(self.data["TE"], x, y, self.items, self.layer)

    def canplace(self, x, y, x2, y2):
        return canplaceit(self.data["TE"], x, y, x2, y2)

    def sad(self):
        if self.tileimage["category"] == "material":
            self.data["TE"]["defaultMaterial"] = self.tileimage["name"]
        self.labels[2].set_text("Default material: " + self.data["TE"]["defaultMaterial"])

    def cleartool(self):
        self.tool = True

    def changetools(self):
        self.tool = not self.tool

    def copytile(self):
        pos = [math.floor((pg.mouse.get_pos()[0] - self.field.rect.x) / self.size),
               math.floor((pg.mouse.get_pos()[1] - self.field.rect.y) / self.size)]
        posoffset = [pos[0] - self.xoffset, pos[1] - self.yoffset]
        if not 0 < posoffset[0] < len(self.data["GE"]) or not 0 < posoffset[1] < len(self.data["GE"][0]):
            return
        tile = self.data["TE"]["tlMatrix"][posoffset[0]][posoffset[1]][self.layer]
        cat = "material"
        name = "Standard"

        match tile["tp"]:
            case "default":
                return
            case "material":
                name = tile["data"]
            case "tileBody":
                pos = toarr(tile["data"][0], "point")
                pos[0] -= 1
                pos[1] -= 1
                tile = self.data["TE"]["tlMatrix"][pos[0]][pos[1]][tile["data"][1] - 1]

        if tile["tp"] == "tileHead":
            i = 0
            for catname, items in self.items.items():
                for item in items:
                    if item["name"] == tile["data"][1]:
                        cat = catname
                        name = tile["data"][1]
                        self.currentcategory = i
                        self.rebuttons()
                        self.set(cat, name)
                        return
                i += 1

        self.currentcategory = len(self.items) - 1
        self.rebuttons()
        self.set(cat, name)
