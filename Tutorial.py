from menuclass import *


class TT(MenuWithField):
    def __init__(self, surface: pg.surface.Surface, renderer: Renderer):
        super().__init__(surface, "TT", renderer)
        self.matshow = None
        self.buttonslist = []
        self.step = -1
        self.maxstep = 0
        self.renderer.geo_full_render(self.layer)
        self.size = 13
        self.pastedata = json.load(open(path2tutorial + "text samples.json", "r"))
        self.selectedtool = ""
        self.toolrotation = 0
        self.examplelist = {
            "thingies": [
                {"nm": "Very cool thing", "color": [10, 10, 10]},
                {"nm": "Upper is liar", "color": [50, 50, 50]},
                {"nm": "Upper is liar", "color": [150, 150, 150]}
            ],
            "colors": [
                {"nm": "Ima red", "color": [200, 20, 20]},
                {"nm": "Ima blue", "color": [20, 20, 200]},
                {"nm": "Ima green", "color": [20, 200, 20]}
            ],
            "More colors": [
                {"nm": "pink", "color": [200, 20, 200]},
                {"nm": "yellow", "color": [200, 200, 20]},
                {"nm": "hm", "color": [20, 200, 200]}
            ]
        }
        self.selectedtile = ""
        self.currentcategory = 0
        self.next()
        self.resize()
        self.rfa()
        self.blit()
        self.onstart()

    def onstart(self):
        self.labels[1].visible = False
        self.buttons[2].visible = False
        self.buttons[3].visible = False
        self.buttons[4].visible = False
        self.buttons[6].visible = False
        self.buttons[7].visible = False
        self.buttons[8].visible = False
        self.field.visible = False

    def resize(self):
        super().resize()
        if hasattr(self, "field"):
            self.field.resize()
            for i in self.buttonslist:
                i.resize()
            self.renderfield()

    def blit(self, draw=True):
        mpos = pg.mouse.get_pos()
        con = False
        match self.step:
            case 1:
                con = self.xoffset != 0 or self.yoffset != 0
            case 2:
                con = self.size != 13
            case 3:
                con = self.layer != 0
        if len(self.buttonslist) > 1:
            pg.draw.rect(self.surface, settings["TE"]["menucolor"], pg.rect.Rect(self.buttonslist[0].xy, [self.buttonslist[0].rect.w, len(self.buttonslist[:-1]) * self.buttonslist[0].rect.h + 1]))
            for button in self.buttonslist:
                button.blitshadow()
            for button in self.buttonslist[:-1]:
                button.blit(sum(pg.display.get_window_size()) // 120)
            self.buttonslist[-1].blit(sum(pg.display.get_window_size()) // 100)
        super().blit(draw)
        self.enablenext(con)
        if self.field.rect.collidepoint(mpos) and self.field.visible:
            bp = pg.mouse.get_pressed(3)
            pos = self.pos
            pos2 = self.pos2
            pg.draw.rect(self.surface, cursor, [pos2, [self.size, self.size]], 1)
            posoffset = self.posoffset
            if bp[0] == 1 and self.mousp and (self.mousp2 and self.mousp1):
                self.mousp = False
                self.emptyarea()
            elif bp[0] == 1 and not self.mousp and (self.mousp2 and self.mousp1) and self.step > 5:
                placeblock = 1
                if self.selectedtool == "AR":
                    placeblock = 0
                elif self.selectedtool == "SL":
                    placeblock = 2 + self.toolrotation
                if (0 <= posoffset[0] < len(self.data["GE"])) and (0 <= posoffset[1] < len(self.data["GE"][0])):
                    self.area[int(posoffset[0])][int(posoffset[1])] = False
                    self.data["GE"][int(posoffset[0])][int(posoffset[1])][self.layer][0] = placeblock
            elif bp[0] == 0 and not self.mousp and (self.mousp2 and self.mousp1):
                if self.step == 6 or (self.selectedtool == "AR" and self.step == 8) \
                                  or (self.selectedtool == "SL" and self.step == 10):
                    self.enablenext()
                self.mousp = True
                self.render_geo_area()
                self.rfa()

            if bp[2] == 1 and self.mousp2 and (self.mousp and self.mousp1):
                self.mousp2 = False
                self.rectdata = [posoffset, pg.Vector2(0, 0), pos2]
                self.emptyarea()
            elif bp[2] == 1 and not self.mousp2 and (self.mousp and self.mousp1) and self.step > 6:
                self.rectdata[1] = posoffset - self.rectdata[0]
                rect = self.vec2rect(self.rectdata[2], pos2)
                tx = f"{int(rect.w / self.size)}, {int(rect.h / self.size)}"
                widgets.fastmts(self.surface, tx, *mpos, white)
                pg.draw.rect(self.surface, select, rect, 5)
            elif bp[2] == 0 and not self.mousp2 and (self.mousp and self.mousp1):
                if self.step == 7 or (self.selectedtool == "AR" and self.step == 8) \
                                  or (self.selectedtool == "SL" and self.step == 10):
                    self.enablenext()
                rect = self.vec2rect(self.rectdata[0], posoffset)
                placeblock = 1
                if self.selectedtool == "AR":
                    placeblock = 0
                elif self.selectedtool == "SL":
                    placeblock = 2 + self.toolrotation
                for x in range(int(rect.w)):
                    for y in range(int(rect.h)):
                        if (0 <= posoffset[0] < len(self.data["GE"])) and (0 <= posoffset[1] < len(self.data["GE"][0])):
                            self.data["GE"][x + int(rect.x)][y + int(rect.y)][self.layer][0] = placeblock
                            self.area[x + int(rect.x)][y + int(rect.y)] = False
                self.data["GE"] = self.data["GE"]
                self.detecthistory(["GE"])
                self.renderer.geo_render_area(self.area, self.layer)
                self.rfa()
                self.mousp2 = True

            if self.step > 0:
                self.movemiddle(bp)

    def enablenext(self, condition=True):
        if condition:
            self.buttons[0].enabled = True
            self.buttons[0].visible = True

    def next(self):
        self.step += 1
        if self.step >= len(self.settings["textlines"]):
            self.message = "load"
            return
        textline = self.settings["textlines"][self.step]
        firstchar = textline[0]
        self.buttons[0].visible = True
        self.buttons[0].enabled = True
        if firstchar == "?":
            self.labels[0].set_text(textline[1:])
        elif firstchar == "@":
            self.labels[0].set_text(textline[1:])
            self.buttons[0].visible = False
        else:
            self.labels[0].set_text(textline)
            if self.step > self.maxstep:
                self.buttons[0].enabled = False
        if self.maxstep < self.step - 1:
            self.maxstep = self.step
        self.showstep()

    def showstep(self):
        self.clearfield()
        match self.step:
            case 0:
                self.field.visible = False
            case 1:
                self.field.visible = True
                self.pastegeo("MMB - move around")
            case 2:
                self.pastegeo("MMB - move around")
                self.pastegeo("scroll - scale", 1)
            case 3:
                if self.layer != 0:
                    self.layer = 0
                    self.render_geo_full()
                self.pastegeo("MMB - move around")
                self.pastegeo("scroll - scale", 1)
                self.pastegeo("L - change layer", 2)
                self.buttons[2].visible = False
                self.buttons[3].visible = False
                self.buttons[4].visible = False
                self.labels[1].visible = False
            case 4:
                if self.layer != 1:
                    self.layer = 1
                    self.render_geo_full()
            case 5:
                self.buttons[2].visible = True
                self.buttons[3].visible = True
                self.buttons[4].visible = True

                self.buttons[2].enabled = True
                self.buttons[3].enabled = False
                self.buttons[4].enabled = False
                self.labels[1].visible = True
            case 6:
                self.pastegeo("LMB - Place")
            case 7:
                self.pastegeo("LMB - Place")
                self.pastegeo("RMB - fill", 1)
                self.buttons[3].enabled = False
            case 8:
                self.pastegeo("LMB - Place")
                self.pastegeo("RMB - fill", 1)
                self.buttons[3].enabled = True
                self.buttons[4].enabled = False
            case 9:
                self.pastegeo("LMB - Place")
                self.pastegeo("RMB - fill", 1)
                self.pastegeo("SPACE - rotate slopes", 2)
                self.buttons[4].enabled = True
                self.buttons[2].visible = True
                self.buttons[3].visible = True
                self.buttons[4].visible = True
                self.labels[1].visible = True
                self.field.visible = True
            case 12:
                self.field.visible = False
                self.buttons[2].visible = False
                self.buttons[3].visible = False
                self.buttons[4].visible = False
                self.labels[1].visible = False
                self.buttons[6].visible = False
                self.buttons[7].visible = False
                self.buttons[8].visible = False
                self.buttonslist = []
            case 13:
                self.labels[1].visible = True
                self.buttons[6].visible = True
                self.buttons[7].visible = True
                self.buttons[8].visible = True
                self.rebuttons()
            case 18:
                self.labels[1].visible = True
                self.buttons[6].visible = True
                self.buttons[7].visible = True
                self.buttons[8].visible = True
                self.rebuttons()
            case 19:
                self.buttonslist = []
                self.labels[1].visible = False
                self.buttons[6].visible = False
                self.buttons[7].visible = False
                self.buttons[8].visible = False

    def clearfield(self):
        clearblock = 1 if self.layer == 0 else 0
        for x in range(self.btiles[0], len(self.data["GE"]) - self.btiles[2]):
            for y in range(self.btiles[1], len(self.data["GE"][0]) - self.btiles[3]):
                self.data["GE"][x][y][self.layer][0] = clearblock
        self.render_geo_full()
        self.rfa()

    def skip(self):
        self.enablenext()
        self.next()

    def prev(self):
        if self.step - 1 >= 0:
            self.step -= 1
            textline = self.settings["textlines"][self.step]
            firstchar = textline[0]
            self.buttons[0].visible = True
            if firstchar == "?":
                self.labels[0].set_text(textline[1:])
            elif firstchar == "@":
                self.labels[0].set_text(textline[1:])
                self.buttons[0].visible = False
            else:
                self.labels[0].set_text(textline)
            self.buttons[0].enabled = True
            self.showstep()
        else:
            self.message = "load"

    def swichlayers(self):
        if self.step in [3, 11]:
            super().swichlayers()
            self.next()

    def swichlayers_back(self):
        if self.step in []:
            super().swichlayers_back()
            self.next()

    def WL(self):
        if self.step == 5:
            self.enablenext()
        self.selectedtool = "WL"
        self.labels[1].set_text("Selected tool: Wall")

    def AR(self):
        self.selectedtool = "AR"
        self.labels[1].set_text("Selected tool: Air")

    def SL(self):
        self.selectedtool = "SL"
        self.labels[1].set_text("Selected tool: Slope, rotation: 0")
        self.toolrotation = 0

    def rotate(self):
        if self.selectedtool == "SL":
            self.toolrotation = (self.toolrotation + 1) % 4
            self.labels[1].set_text("Selected tool: Slope, rotation: " + str(self.toolrotation))

    def send(self, message):
        if message[0] == "-":
            self.mpos = 1
            if hasattr(self, message[1:]):
                getattr(self, message[1:])()
        match message:
            case "SU":
                if not self.onfield:
                    return
                if self.step > 1:
                    pos = self.pos
                    self.size += 1
                    self.offset -= pos - self.pos
                    self.renderfield()
            case "SD":
                if not self.onfield:
                    return
                if self.step > 1:
                    if self.size - 1 > 0:
                        pos = self.pos
                        self.size -= 1
                        self.offset -= pos - self.pos
                        self.renderfield()
            case "left":
                self.offset.x += 1
            case "right":
                self.offset.x -= 1
            case "up":
                self.offset.y += 1
            case "down":
                self.offset.y -= 1

    def rebuttons(self):
        self.buttonslist = []
        self.matshow = False
        btn2 = None
        itemcat = list(self.examplelist)[self.currentcategory]
        for count, item in enumerate(self.examplelist[itemcat]):
            cat = pg.rect.Rect(self.settings["catpos"])
            btn2 = widgets.button(self.surface, cat, settings["global"]["color"], itemcat, onpress=self.changematshow,
                                  tooltip=self.returnkeytext("Select category(<[-changematshow]>)"))
            rect = pg.rect.Rect(self.settings["itempos"])
            rect = rect.move(0, rect.h * count)
            btn = widgets.button(self.surface, rect, item["color"], item["nm"], onpress=self.settile)
            self.buttonslist.append(btn)
        if btn2 is not None:
            self.buttonslist.append(btn2)
        self.toolindex = 0
        self.resize()

    def changematshow(self):
        if self.matshow:
            self.currentcategory = self.toolindex
            cat = list(self.examplelist.keys())[self.currentcategory]
            self.settile(self.examplelist[cat][0]["nm"])
            self.rebuttons()
        else:
            self.cats()

    def cats(self):
        self.buttonslist = []
        self.matshow = True
        btn2 = None
        if self.step == 15:
            self.next()
        for count, item in enumerate(self.examplelist.keys()):
            cat = pg.rect.Rect(self.settings["catpos"])
            btn2 = widgets.button(self.surface, cat, settings["global"]["color"], "Categories", onpress=self.changematshow)
            rect = pg.rect.Rect(self.settings["itempos"])
            rect = rect.move(0, rect.h * count)
            col = self.examplelist[item][0]["color"]
            if col is None:
                col = gray
            if count == self.currentcategory:
                col = darkgray
            btn = widgets.button(self.surface, rect, col, item, onpress=self.selectcat)
            self.buttonslist.append(btn)
        if btn2 is not None:
            self.buttonslist.append(btn2)
        self.resize()

    def selectcat(self, name):
        self.currentcategory = list(self.examplelist.keys()).index(name)
        self.enablenext(self.step == 16)
        self.rebuttons()

    def settile(self, name):
        self.selectedtile = name
        self.labels[1].set_text(self.selectedtile + " selected")
        self.enablenext(self.step == 13)

    def findtile(self):
        nd = {}
        for cat, item in self.examplelist.items():
            for i in item:
                nd[i["nm"]] = cat
        name = self.find(nd, self.settings["findmenu_text"])
        if name is None:
            return
        cat = self.findcat(name)
        if self.step == 17:
            self.next()
        self.selectcat(cat)
        self.settile(name)

    def findcat(self, itemname):
        for name, listdata in self.examplelist.items():
            for bl in listdata:
                if bl["nm"] == itemname:
                    return name
        return None

    def rt(self):
        self.currentcategory = (self.currentcategory + 1) % len(self.examplelist.keys())
        self.enablenext(self.step == 14)
        self.rebuttons()

    def lt(self):
        self.currentcategory -= 1
        if self.currentcategory < 0:
            self.currentcategory = len(self.examplelist.keys()) - 1
        self.enablenext(self.step == 14)
        self.rebuttons()

    def pastegeo(self, data, line=0):
        self.emptyarea()
        for xi, x in enumerate(copy.deepcopy(self.pastedata[data])):
            for yi, y in enumerate(x):
                xpos = self.btiles[0] + xi + 1
                ypos = self.btiles[1] + yi + 1
                ypos += line * 6
                self.data["GE"][xpos][ypos][self.layer] = y
                self.area[xpos][ypos] = False
        self.detecthistory(["GE"])
        self.render_geo_area()
        self.rfa()