from menuclass import *


class GE(MenuWithField):
    def __init__(self, surface: pg.surface.Surface, renderer):
        self.state = 0
        self.mx = 0

        self.selectedtool = ""
        self.lastselectedtool = ""

        self.tools = toolmenu
        self.tooltiles = tooltiles
        self.toolrender = self.tooltiles

        self.tools.set_alpha(150)
        self.placetile = 0

        self.mirrorp = False
        self.mirrorpos = [0, 0]

        self.replaceair = True
        self.fillshape = "pencil"  # pencil, brush, fill
        self.fillshape2 = "rect"  # rect, rect-hollow, circle, circle-hollow, line

        super().__init__(surface, "GE", renderer)
        self.emptyarea()
        self.air()
        self.rs()
        self.replacestate()
        self.blit()
        self.resize()

    def resize(self):
        super().resize()
        if hasattr(self, "field"):
            self.rs()

    def rotate(self):
        if self.mx != 0:
            self.state = (self.state + 1) % self.mx
        else:
            self.state = 0

    def mleft(self):
        if self.mirrorpos[1] == 0:
            self.mirrorpos[0] -= 1
        else:
            self.mirrorpos[1] = 0
            self.mirrorpos[0] = len(self.data["GE"]) // 2

    def mright(self):
        if self.mirrorpos[1] == 0:
            self.mirrorpos[0] += 1
        else:
            self.mirrorpos[1] = 0
            self.mirrorpos[0] = len(self.data["GE"]) // 2

    def mup(self):
        if self.mirrorpos[1] == 1:
            self.mirrorpos[0] -= 1
        else:
            self.mirrorpos[1] = 1
            self.mirrorpos[0] = len(self.data["GE"][0]) // 2

    def mdown(self):
        if self.mirrorpos[1] == 1:
            self.mirrorpos[0] += 1
        else:
            self.mirrorpos[1] = 1
            self.mirrorpos[0] = len(self.data["GE"][0]) // 2

    def rs(self):
        self.toolrender = pg.transform.scale(self.tooltiles,
                                             [self.tooltiles.get_width() / graphics["tilesize"][0] * image1size,
                                              self.tooltiles.get_height() / graphics["tilesize"][1] * image1size])

    def renderfield(self):
        super().renderfield()
        self.fieldadd = pg.transform.scale(self.fieldadd,
                                           [len(self.data["GE"]) * self.size, len(self.data["GE"][0]) * self.size])
        self.fieldadd.fill(white)
        # renderfield(self.fieldmap, self.size, self.layer, self.data["GE"])

    def blit(self):
        cellsize2 = [self.size, self.size]
        super().blit()
        mpos = pg.Vector2(pg.mouse.get_pos())
        if self.selectedtool != self.lastselectedtool:
            self.lastselectedtool = self.selectedtool
            self.recaption()
        if self.onfield:
            curtool = [graphics["tools"][self.selectedtool][0] * graphics["tilesize"][0],
                       graphics["tools"][self.selectedtool][1] * graphics["tilesize"][1]]
            self.surface.blit(self.tools, mpos, [curtool, graphics["tilesize"]])

            # cords = [math.floor(pg.mouse.get_pos()[0] / self.size) * self.size, math.floor(pg.mouse.get_pos()[1] / self.size) * self.size]
            # self.surface.blit(self.tools, pos, [curtool, graphics["tilesize"]])
            pos = self.pos
            pos2 = self.pos2
            pg.draw.rect(self.surface, cursor, [pos2, [self.size, self.size]], 1)
            posoffset = self.posoffset

            toolsized = pg.transform.scale(self.toolrender,
                                           pg.Vector2(self.toolrender.get_size()) / image1size * self.size)

            self.labels[1].set_text(f"X: {posoffset.x}, Y: {posoffset.y}, Z: {self.layer + 1}")
            if self.selectedtool in self.settings["codes"].keys():
                if type(self.placetile) == int:
                    if self.settings["codes"][self.selectedtool] == 1:
                        curtool = [graphics["tileplaceicon"][str(self.placetile + self.state)][0] * self.size,
                                   graphics["tileplaceicon"][str(self.placetile + self.state)][1] * self.size]
                    else:
                        curtool = [graphics["tileplaceicon"][str(self.placetile - self.state)][0] * self.size,
                                   graphics["tileplaceicon"][str(self.placetile - self.state)][1] * self.size]
                    # print([abs(self.field.rect.x - pos2[0]), abs(self.field.rect.y - pos2[1])])
                    self.surface.blit(toolsized, pos2, [curtool, cellsize2])
            rect = [self.xoffset * self.size, self.yoffset * self.size, len(self.data["GE"]) * self.size,
                    len(self.data["GE"][0]) * self.size]
            pg.draw.rect(self.field.field, border, rect, self.size // image1size + 1)
            if (0 <= posoffset.x < len(self.data["GE"])) and (0 <= posoffset.y < len(self.data["GE"][0])):
                tilename = settings["GE"]["names"][
                    str(self.data["GE"][int(posoffset.x)][int(posoffset.y)][self.layer][0])]
                self.labels[0].set_text(
                    f"Tile: {tilename} {self.data['GE'][int(posoffset.x)][int(posoffset.y)][self.layer]}")

            bp = pg.mouse.get_pressed(3)

            if bp[0] == 1 and self.mousp and (self.mousp2 and self.mousp1):
                if self.selectedtool == "MV":
                    self.rectdata[0] = pos
                    self.rectdata[1] = self.offset
                    self.field.field.fill(self.field.color)
                else:
                    self.emptyarea()
                self.mousp = False
            elif bp[0] == 1 and not self.mousp and (self.mousp2 and self.mousp1):
                if self.selectedtool == "MV":
                    self.offset = self.rectdata[1] - (self.rectdata[0] - pos)
                elif self.selectedtool == "CT":
                    pass
                elif (0 <= posoffset.x < len(self.data["GE"])) and (0 <= posoffset.y < len(self.data["GE"][0])) and self.area[int(posoffset.x)][int(posoffset.y)] == 1:
                    self.place(posoffset, False)
                    if type(self.placetile) == int:
                        if self.settings["codes"][self.selectedtool] == 1:
                            curtool = [
                                graphics["tileplaceicon"][str(self.placetile + self.state)][0] * self.size,
                                graphics["tileplaceicon"][str(self.placetile + self.state)][1] * self.size]
                        else:
                            curtool = [
                                graphics["tileplaceicon"][str(self.placetile + self.state)][0] * self.size,
                                graphics["tileplaceicon"][str(self.placetile + self.state)][1] * self.size]
                        rect = [posoffset[0] * self.size, posoffset[1] * self.size]
                        self.fieldadd.blit(toolsized, rect, [curtool, cellsize2])
                        if self.mirrorp:
                            px = int(posoffset.x)
                            py = int(posoffset.y)
                            if self.mirrorpos[1] == 0:
                                px = self.mirrorpos[0] * 2 + (-px - 1)
                            else:
                                py = self.mirrorpos[0] * 2 + (-py - 1)
                            self.area[px][py] = 0
                            px *= self.size
                            py *= self.size
                            self.fieldadd.blit(self.toolrender, [px, py], [curtool, cellsize2])
            elif bp[0] == 0 and not self.mousp and (self.mousp2 and self.mousp1):
                self.fieldadd.fill(white)
                self.mousp = True
                paths = []
                count = 0
                for xindex, xpos in enumerate(self.area):
                    for yindex, ypos in enumerate(xpos):
                        if ypos == 0:
                            paths.append(["GE", xindex, yindex, self.layer])
                            count += 1
                if len(paths) > 0:
                    if count < 20: # if we changed more than 20 pixels, changing history save method
                        self.updatehistory(paths)
                    else:
                        self.detecthistory(["GE"])
                self.render_geo_area()
                self.rfa()

            self.movemiddle(bp)

            if bp[2] == 1 and self.mousp2 and (self.mousp and self.mousp1):
                self.mousp2 = False
                self.rectdata = [posoffset, pg.Vector2(0, 0), pos2]
                self.emptyarea()
            elif bp[2] == 1 and not self.mousp2 and (self.mousp and self.mousp1):
                self.rectdata[1] = posoffset - self.rectdata[0]
                # print(self.rectdata[2], pos2 - self.rectdata[2])
                rect = self.vec2rect(self.rectdata[2], pos2)
                tx = f"{abs(int(rect.w / self.size))}, {abs(int(rect.h / self.size))}"
                widgets.fastmts(self.surface, tx, *mpos, white)
                if self.fillshape2 in ["rect", "rect-hollow"] or self.selectedtool == "CP" or self.selectedtool == "CT":
                    pg.draw.rect(self.surface, select, rect, 5)
                elif self.fillshape2 in ["circle", "circle-hollow"]:
                    pg.draw.ellipse(self.surface, select, rect, 5)
                elif self.fillshape2 == "line":
                    pg.draw.line(self.surface, select, self.rectdata[2], pos2, 5)
            elif bp[2] == 0 and not self.mousp2 and (self.mousp and self.mousp1):
                if self.selectedtool == "CP" or self.selectedtool == "CT":
                    rect = self.vec2rect(self.rectdata[0], posoffset)
                    data1 = self.data["GE"][rect.x:rect.x + rect.w]
                    data1 = [i[rect.y:rect.y + rect.h] for i in data1]
                    data1 = [[y[self.layer] for y in x] for x in data1]
                    pyperclip.copy(str(data1))
                    print("Copied!")
                elif self.fillshape2 in ["circle", "circle-hollow"]:
                    rect = self.vec2rect(self.rectdata[0], posoffset)
                    rect2ellipse(rect, self.fillshape2 == "circle-hollow", self.place)
                    self.detecthistory(["GE"])
                    self.render_geo_area()
                    self.rfa()
                elif self.fillshape2 == "line":
                    self.linepoints(self.rectdata[0], posoffset)
                    self.detecthistory(["GE"])
                    self.render_geo_area()
                    self.rfa()
                elif self.fillshape2 in ["rect", "rect-hollow"]:
                    rect = self.vec2rect(self.rectdata[0], posoffset)
                    for x in range(int(rect.w)):
                        for y in range(int(rect.h)):
                            vec = pg.Vector2(x, y)
                            if self.fillshape2 == "rect" or (vec.x == 0 or vec.y == 0 or vec.x == int(rect.w)-1 or vec.y == int(rect.h)-1):
                                self.place(vec + rect.topleft, False)
                    self.detecthistory(["GE"])
                    self.render_geo_area()
                    self.rfa()
                if self.selectedtool == "CT":
                    rect = self.vec2rect(self.rectdata[0], posoffset)
                    for x in range(int(rect.w)):
                        for y in range(int(rect.h)):
                            vec = pg.Vector2(x, y)
                            self.place(vec + rect.topleft, False)
                    self.detecthistory(["GE"])
                    self.renderer.geo_render_area(self.area, self.layer)
                    self.rfa()
                self.mousp2 = True

            # aaah math
            if self.mirrorp:
                px = pos.x
                py = pos.y
                if self.mirrorpos[1] == 0:
                    px = pos.x - self.xoffset * 2
                    px = self.mirrorpos[0] * 2 + (-px - 1)
                else:
                    py = pos.y - self.yoffset * 2
                    py = self.mirrorpos[0] * 2 + (-py - 1)
                px = px * self.size + self.field.rect.x
                py = py * self.size + self.field.rect.y
                pg.draw.rect(self.surface, cursor2, [px, py, self.size, self.size], 1)
        if self.mirrorp:

            px = (self.mirrorpos[0] + self.xoffset) * self.size + self.field.rect.x
            py = (self.mirrorpos[0] + self.yoffset) * self.size + self.field.rect.y
            if self.mirrorpos[1] == 0:
                pg.draw.rect(self.surface, mirror, [px, self.field.rect.y, 3, self.field.field.get_height()])
            else:
                pg.draw.rect(self.surface, mirror, [self.field.rect.x, py, self.field.field.get_width(), 3])
        if pg.key.get_pressed()[pg.K_LCTRL]:
            try:
                geodata = eval(pyperclip.paste())
                if type(geodata) != list:
                    return
                pos = self.field.rect.topleft + (self.pos * self.size if self.onfield else pg.Vector2(0, 0))
                rect = pg.Rect([pos, pg.Vector2(len(geodata), len(geodata[0])) * self.size])

                pg.draw.rect(self.surface, select, rect, 5)
            except:
                pass

    def linepoints(self, pointa: pg.Vector2, pointb: pg.Vector2):
        plotLine(pointa, pointb, self.place)

    def replacestate(self):
        self.replaceair = not self.replaceair
        self.labels[2].set_text(self.labels[2].originaltext + str(self.replaceair))

    def pastegeo(self):
        try:
            self.emptyarea()
            geodata = eval(pyperclip.paste())
            if type(geodata) != list:
                return
            for xi, x in enumerate(geodata):
                for yi, y in enumerate(x):
                    pa = pg.Vector2(0, 0)
                    if self.field.rect.collidepoint(pg.mouse.get_pos()):
                        pa = self.pos
                    xpos = -self.xoffset + xi + int(pa.x)
                    ypos = -self.yoffset + yi + int(pa.y)
                    if (self.replaceair and y[0] == 0) or not self.canplaceit(xpos, ypos, xpos, ypos):
                        continue
                    self.data["GE"][xpos][ypos][self.layer] = y
                    self.area[xpos][ypos] = 0
            self.detecthistory(["GE"])
            self.renderer.geo_render_area(self.area, self.layer)
            self.rfa()
        except:
            print("Error pasting data!")

    def s0(self):
        self.state = 0

    def inverse(self):
        self.selectedtool = "IN"
        self.placetile = 0.2
        self.mx = 0

    def walls(self):
        self.selectedtool = "WL"
        self.placetile = 1
        self.mx = 0

    def air(self):
        self.selectedtool = "AR"
        self.placetile = 0
        self.mx = 0

    def slope(self):
        self.selectedtool = "SL"
        self.placetile = 2
        self.mx = 4

    def floor(self):
        self.selectedtool = "FL"
        self.placetile = 6
        self.mx = 0

    def rock(self):
        self.selectedtool = "RK"
        self.placetile = -9
        self.mx = 0

    def spear(self):
        self.selectedtool = "SP"
        self.placetile = -10
        self.mx = 0

    def move(self):
        self.selectedtool = "MV"
        self.placetile = 0.1
        self.mx = 0

    def crack(self):
        self.selectedtool = "CR"
        self.placetile = -11
        self.mx = 0

    def beam(self):
        self.selectedtool = "BM"
        self.placetile = -1
        self.mx = 2

    def glass(self):
        self.selectedtool = "GL"
        self.placetile = 9
        self.mx = 0

    def shortcutentrance(self):
        self.selectedtool = "SE"
        self.placetile = 0.4
        self.mx = 0

    def shortcut(self):
        self.selectedtool = "SC"
        self.placetile = -5
        self.mx = 0

    def dragonden(self):
        self.selectedtool = "D"
        self.placetile = -7
        self.mx = 0

    def entrance(self):
        self.selectedtool = "E"
        self.placetile = -6
        self.mx = 0

    def mirror(self):
        self.mirrorp = not self.mirrorp
        self.mirrorpos = [len(self.data["GE"]) // 2, 0]

    def clearall(self):
        self.selectedtool = "CA"
        self.placetile = 0.3

    def flychains(self):
        self.selectedtool = "FC"
        self.placetile = -12
        self.mx = 0

    def flyhive(self):
        self.selectedtool = "HV"
        self.placetile = -3
        self.mx = 0

    def scavengerhole(self):
        self.selectedtool = "SH"
        self.placetile = -21
        self.mx = 0

    def garbagewormden(self):
        self.selectedtool = "GWD"
        self.placetile = -13
        self.mx = 0

    def whack_a_mole_hole(self):
        self.selectedtool = "WMH"
        self.placetile = -19
        self.mx = 0

    def waterfall(self):
        self.selectedtool = "W"
        self.placetile = -18
        self.mx = 0

    def wormgrass(self):
        self.selectedtool = "WG"
        self.placetile = -20
        self.mx = 0

    def clearlayer(self):
        self.selectedtool = "CL"
        self.placetile = 0.5
        self.mx = 0

    def clearblock(self):
        self.selectedtool = "CB"
        self.placetile = 0.6
        self.mx = 0

    def copylayer(self):
        self.selectedtool = "CP"
        self.placetile = 0.1
        self.mx = 0

    def cutlayer(self):
        self.selectedtool = "CT"
        self.placetile = 0.5
        self.mx = 0

    def place(self, pos, render=True):
        x = int(pos.x)
        y = int(pos.y)
        self.mirrorplace(pos, render)
        if x >= len(self.data["GE"]) or y >= len(self.data["GE"][0]) or x < 0 or y < 0:
            return
        self.area[x][y] = 0
        if self.placetile != 0.1:  # dont place
            if self.placetile == 0.2:  # inverse
                if self.data["GE"][x][y][self.layer][0] == 0:
                    self.data["GE"][x][y][self.layer][0] = 1
                else:
                    self.data["GE"][x][y][self.layer][0] = self.reverseslope(self.data["GE"][x][y][self.layer][0])
            elif self.placetile == 0.3:  # clear all
                self.data["GE"][x][y] = [[0, []], [0, []], [0, []]]
            elif self.placetile == 0.4:  # shortcut entrance
                self.data["GE"][x][y][self.layer][0] = 7
                if 4 not in self.data["GE"][x][y][self.layer][1]:
                    self.data["GE"][x][y][self.layer][1].append(4)
            elif self.placetile == 0.5:  # clear layer
                self.data["GE"][x][y][self.layer] = [0, []]
            elif self.placetile == 0.6:  # clear upper
                self.data["GE"][x][y][self.layer][1] = []
            elif self.selectedtool in self.settings["codes"].keys():  # else
                if self.settings["codes"][self.selectedtool] == 1:
                    self.data["GE"][x][y][self.layer][0] = self.placetile + self.state
                if self.settings["codes"][self.selectedtool] == 0:
                    if (abs(int(self.placetile))) + self.state not in self.data["GE"][x][y][self.layer][1]:
                        self.data["GE"][x][y][self.layer][1].append((abs(int(self.placetile))) + self.state)
            else:
                self.data["GE"][x][y][self.layer][0] = self.placetile
        if render:
            self.renderer.geo_render_area(self.area, self.layer)
            self.rfa()

    def mirrorplace(self, pos, render=False):
        if not self.mirrorp:
            return
        x = int(pos.x)
        y = int(pos.y)
        if self.mirrorpos[1] == 0:
            x = self.mirrorpos[0] * 2 + (-x - 1)
        else:
            y = self.mirrorpos[0] * 2 + (-y - 1)
        if x >= len(self.data["GE"]) or y >= len(self.data["GE"][0]) or x < 0 or y < 0:
            return
        self.area[x][y] = 0
        if self.placetile != 0.1:
            if self.placetile == 0.2:
                if self.data["GE"][x][y][self.layer][0] == 0:
                    self.data["GE"][x][y][self.layer][0] = 1
                else:
                    self.data["GE"][x][y][self.layer][0] = self.reverseslope(self.data["GE"][x][y][self.layer][0])
            elif self.placetile == 0.3:
                self.data["GE"][x][y] = [[0, []], [0, []], [0, []]]
            elif self.placetile == 0.4:
                self.data["GE"][x][y][self.layer][0] = 7
                if 4 not in self.data["GE"][x][y][self.layer][1]:
                    self.data["GE"][x][y][self.layer][1].append(4)
            elif self.placetile == 0.5:
                self.data["GE"][x][y][self.layer] = [0, []]
            elif self.placetile == 0.6:
                self.data["GE"][x][y][self.layer][1] = []
            elif self.selectedtool in self.settings["codes"].keys():
                if self.settings["codes"][self.selectedtool] == 1:
                    self.data["GE"][x][y][self.layer][0] = self.reverseslope(self.placetile + self.state)
                if self.settings["codes"][self.selectedtool] == 0:
                    if (abs(int(self.placetile))) + self.state not in self.data["GE"][x][y][self.layer][1]:
                        self.data["GE"][x][y][self.layer][1].append((abs(int(self.placetile))) + self.state)
            else:
                self.data["GE"][x][y][self.layer][0] = self.reverseslope(self.placetile)
        if render:
            self.renderer.geo_render_area(self.area, self.layer)
            self.rfa()

    def reverseslope(self, slope):
        if slope in [2, 3, 4, 5]:
            if self.selectedtool == "SL":
                if self.mirrorp:
                    if self.mirrorpos[1] == 0:
                        return [3, 2, 5, 4][slope - 2]
                    else:
                        return [4, 5, 2, 3][slope - 2]
            elif self.selectedtool == "IN":
                return [5, 4, 3, 2][slope - 2]
        if self.selectedtool == "IN":
            return 0
        return slope

    def tool_rect(self):
        self.fillshape2 = "rect"
        self.recaption()

    def tool_rect_hollow(self):
        self.fillshape2 = "rect-hollow"
        self.recaption()

    def tool_circle(self):
        self.fillshape2 = "circle"
        self.recaption()

    def tool_circle_hollow(self):
        self.fillshape2 = "circle-hollow"
        self.recaption()

    def tool_line(self):
        self.fillshape2 = "line"
        self.recaption()

    def tool_pencil(self):
        self.fillshape = "pencil"
        self.recaption()

    def tool_brush(self):
        self.fillshape = "brush"
        self.recaption()

    def tool_fill(self):
        self.fillshape = "fill"
        self.recaption()

    @property
    def custom_info(self):
        try:
            return f"{super().custom_info} | Placing: {self.selectedtool} | LMB tool: {self.fillshape}, RMB tool: {self.fillshape2}"
        except TypeError:
            return super().custom_info
