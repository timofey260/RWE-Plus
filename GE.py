from menuclass import *

class GE(menu_with_field):
    def __init__(self, surface: pg.surface.Surface, data, items, props, propcolors):
        self.menu = "GE"
        self.mapdata = data["GE"]
        self.state = 0
        self.mx = 0

        self.selectedtool = ""
        self.tools = toolmenu
        self.tooltiles = tooltiles
        self.toolrender = self.tooltiles

        self.tools.set_alpha(150)
        self.placetile = 0
        self.area = [[1 for _ in range(len(self.mapdata[0]))] for _ in range(len(self.mapdata))]

        self.mirrorp = False
        self.mirrorpos = [0, 0]

        self.replaceair = False

        super().__init__(surface, data, "GE", items, props, propcolors)
        self.air()
        self.init()
        self.rs()
        self.rfa()

    def resize(self):
        super().resize()
        if hasattr(self, "field"):
            self.rs()

    def send(self, message):
        if message[0] == "-":
            getattr(self, message[1:])()
        match message:
            case "left":
                self.xoffset += 1
            case "right":
                self.xoffset -= 1
            case "up":
                self.yoffset += 1
            case "down":
                self.yoffset -= 1
            case "SU":
                self.size += 1
                self.rs()
                self.renderfield()
            case "SD":
                if self.size - 1 != 0:
                    self.size -= 1
                self.rs()
                self.renderfield()
            case "rotate":
                if self.mx != 0:
                    self.state = (self.state + 1) % self.mx
                else:
                    self.state = 0
            case "mleft":
                if self.mirrorpos[1] == 0:
                    self.mirrorpos[0] -= 1
                else:
                    self.mirrorpos[1] = 0
                    self.mirrorpos[0] = len(self.mapdata) // 2
            case "mright":
                if self.mirrorpos[1] == 0:
                    self.mirrorpos[0] += 1
                else:
                    self.mirrorpos[1] = 0
                    self.mirrorpos[0] = len(self.mapdata) // 2
            case "mup":
                if self.mirrorpos[1] == 1:
                    self.mirrorpos[0] -= 1
                else:
                    self.mirrorpos[1] = 1
                    self.mirrorpos[0] = len(self.mapdata[0]) // 2
            case "mdown":
                if self.mirrorpos[1] == 1:
                    self.mirrorpos[0] += 1
                else:
                    self.mirrorpos[1] = 1
                    self.mirrorpos[0] = len(self.mapdata[0]) // 2

    def rs(self):
        self.toolrender = pg.transform.scale(self.tooltiles,
                                             [self.tooltiles.get_width() / graphics["tilesize"][0] * self.size,
                                              self.tooltiles.get_height() / graphics["tilesize"][1] * self.size])

    def renderfield(self):
        super().renderfield()
        self.fieldadd = pg.transform.scale(self.fieldadd,
                                           [len(self.data["GE"]) * self.size, len(self.data["GE"][0]) * self.size])
        self.fieldadd.fill(white)
        # renderfield(self.fieldmap, self.size, self.layer, self.mapdata)

    def blit(self):
        cellsize2 = [self.size, self.size]
        super().blit()
        mpos = pg.mouse.get_pos()
        if self.field.rect.collidepoint(mpos):
            curtool = [graphics["tools"][self.selectedtool][0] * graphics["tilesize"][0],
                       graphics["tools"][self.selectedtool][1] * graphics["tilesize"][1]]
            self.surface.blit(self.tools, mpos, [curtool, graphics["tilesize"]])

            # cords = [math.floor(pg.mouse.get_pos()[0] / self.size) * self.size, math.floor(pg.mouse.get_pos()[1] / self.size) * self.size]
            # self.surface.blit(self.tools, pos, [curtool, graphics["tilesize"]])
            pos = [math.floor((mpos[0] - self.field.rect.x) / self.size),
                   math.floor((mpos[1] - self.field.rect.y) / self.size)]
            pos2 = [pos[0] * self.size + self.field.rect.x, pos[1] * self.size + self.field.rect.y]
            pg.draw.rect(self.surface, cursor, [pos2, [self.size, self.size]], 1)
            posoffset = [pos[0] - self.xoffset, pos[1] - self.yoffset]

            self.labels[1].set_text(f"X: {posoffset[0]}, Y: {posoffset[1]}, Z: {self.layer + 1}")
            if self.selectedtool in self.settings["codes"].keys():
                if type(self.placetile) == int:
                    if self.settings["codes"][self.selectedtool] == 1:
                        curtool = [graphics["tileplaceicon"][str(self.placetile + self.state)][0] * self.size,
                                   graphics["tileplaceicon"][str(self.placetile + self.state)][1] * self.size]
                    else:
                        curtool = [graphics["tileplaceicon"][str(self.placetile - self.state)][0] * self.size,
                                   graphics["tileplaceicon"][str(self.placetile - self.state)][1] * self.size]
                    # print([abs(self.field.rect.x - pos2[0]), abs(self.field.rect.y - pos2[1])])
                    self.surface.blit(self.toolrender, pos2, [curtool, cellsize2])
            rect = [self.xoffset * self.size, self.yoffset * self.size, len(self.mapdata) * self.size,
                    len(self.mapdata[0]) * self.size]
            pg.draw.rect(self.field.field, border, rect, 5)
            if (0 <= posoffset[0] < len(self.mapdata)) and (0 <= posoffset[1] < len(self.mapdata[0])):
                tilename = settings["GE"]["names"][str(self.mapdata[posoffset[0]][posoffset[1]][self.layer][0])]
                self.labels[0].set_text(f"Tile: {tilename} {self.mapdata[posoffset[0]][posoffset[1]][self.layer]}")

            bp = pg.mouse.get_pressed(3)

            if bp[0] == 1 and self.mousp and (self.mousp2 and self.mousp1):
                if self.selectedtool == "MV":
                    self.rectdata[0] = pos
                    self.rectdata[1] = [self.xoffset, self.yoffset]
                    self.field.field.fill(self.field.color)
                else:
                    self.area = [[1 for _ in range(len(self.mapdata[0]))] for _ in range(len(self.mapdata))]
                self.mousp = False
            elif bp[0] == 1 and not self.mousp and (self.mousp2 and self.mousp1):
                if self.selectedtool == "MV":
                    self.xoffset = self.rectdata[1][0] - (self.rectdata[0][0] - pos[0])
                    self.yoffset = self.rectdata[1][1] - (self.rectdata[0][1] - pos[1])
                elif (0 <= posoffset[0] < len(self.mapdata)) and (0 <= posoffset[1] < len(self.mapdata[0])) and self.area[posoffset[0]][posoffset[1]] == 1:
                    self.place(posoffset[0], posoffset[1], False)
                    self.area[posoffset[0]][posoffset[1]] = 0
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
                        self.fieldadd.blit(self.toolrender, rect, [curtool, cellsize2])
                        if self.mirrorp:
                            px = posoffset[0]
                            py = posoffset[1]
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
                self.rfa()

            self.movemiddle(bp, pos)

            if bp[2] == 1 and self.mousp2 and (self.mousp and self.mousp1):
                self.mousp2 = False
                self.rectdata = [posoffset, [0, 0], pos2]
            elif bp[2] == 1 and not self.mousp2 and (self.mousp and self.mousp1):
                self.rectdata[1] = [posoffset[0] - self.rectdata[0][0], posoffset[1] - self.rectdata[0][1]]
                rect = pg.Rect([self.rectdata[2], [pos2[0] - self.rectdata[2][0], pos2[1] - self.rectdata[2][1]]])
                tx = f"{int(rect.w / image1size)}, {int(rect.h / image1size)}"
                widgets.fastmts(self.surface, tx, *mpos, white)
                pg.draw.rect(self.surface, select, rect, 5)
            elif bp[2] == 0 and not self.mousp2 and (self.mousp and self.mousp1):
                if self.selectedtool == "CP":
                    data1 = self.mapdata[self.rectdata[0][0]:posoffset[0]]
                    data1 = [i[self.rectdata[0][1]:posoffset[1]] for i in data1]
                    data1 = [[y[self.layer] for y in x] for x in data1]
                    pyperclip.copy(str(data1))
                    print("Copied!")
                else:
                    for x in range(self.rectdata[1][0]):
                        for y in range(self.rectdata[1][1]):
                            self.place(x + self.rectdata[0][0], y + self.rectdata[0][1], False)
                    self.detecthistory(["GE"])
                    self.rfa()
                self.mousp2 = True

            # aaah math
            if self.mirrorp:
                px = pos[0]
                py = pos[1]
                if self.mirrorpos[1] == 0:
                    px = pos[0] - self.xoffset * 2
                    px = self.mirrorpos[0] * 2 + (-px - 1)
                else:
                    py = pos[1] - self.yoffset * 2
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


    def pastegeo(self):
        try:
            geodata = eval(pyperclip.paste())
            if type(geodata) != list:
                return
            for xi, x in enumerate(geodata):
                for yi, y in enumerate(x):
                    if self.replaceair and y[0] == 0:
                        continue
                    self.data["GE"][-self.xoffset + xi][-self.yoffset + yi][self.layer] = y
            self.rfa()
        except SyntaxError:
            pass

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
        self.mirrorpos = [len(self.mapdata) // 2, 0]

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

    def place(self, x, y, render=True):
        self.mirrorplace(x, y, render)
        if x >= len(self.mapdata) or y >= len(self.mapdata[0]) or x < 0 or y < 0:
            return
        if self.placetile != 0.1:  # dont place
            if self.placetile == 0.2:  # inverse
                if self.mapdata[x][y][self.layer][0] == 0:
                    self.mapdata[x][y][self.layer][0] = 1
                else:
                    self.mapdata[x][y][self.layer][0] = self.reverseslope(self.mapdata[x][y][self.layer][0])
            elif self.placetile == 0.3:  # clear all
                self.mapdata[x][y] = [[0, []], [0, []], [0, []]]
            elif self.placetile == 0.4:  # shortcut entrance
                self.mapdata[x][y][self.layer][0] = 7
                if 4 not in self.mapdata[x][y][self.layer][1]:
                    self.mapdata[x][y][self.layer][1].append(4)
            elif self.placetile == 0.5:  # clear layer
                self.mapdata[x][y][self.layer] = [0, []]
            elif self.placetile == 0.6:  # clear upper
                self.mapdata[x][y][self.layer][1] = []
            elif self.selectedtool in self.settings["codes"].keys():  # else
                if self.settings["codes"][self.selectedtool] == 1:
                    self.mapdata[x][y][self.layer][0] = self.placetile + self.state
                if self.settings["codes"][self.selectedtool] == 0:
                    if (abs(int(self.placetile))) + self.state not in self.mapdata[x][y][self.layer][1]:
                        self.mapdata[x][y][self.layer][1].append((abs(int(self.placetile))) + self.state)
            else:
                self.mapdata[x][y][self.layer][0] = self.placetile
        if render:
            self.rfa()

    def mirrorplace(self, xm, ym, render=False):
        if not self.mirrorp:
            return
        x = xm
        y = ym
        if self.mirrorpos[1] == 0:
            x = self.mirrorpos[0] * 2 + (-xm - 1)
        else:
            y = self.mirrorpos[0] * 2 + (-ym - 1)
        if x >= len(self.mapdata) or y >= len(self.mapdata[0]) or x < 0 or y < 0:
            return
        if self.placetile != 0.1:
            if self.placetile == 0.2:
                if self.mapdata[x][y][self.layer][0] == 0:
                    self.mapdata[x][y][self.layer][0] = 1
                else:
                    self.mapdata[x][y][self.layer][0] = self.reverseslope(self.mapdata[x][y][self.layer][0])
            elif self.placetile == 0.3:
                self.mapdata[x][y] = [[0, []], [0, []], [0, []]]
            elif self.placetile == 0.4:
                self.mapdata[x][y][self.layer][0] = 7
                if 4 not in self.mapdata[x][y][self.layer][1]:
                    self.mapdata[x][y][self.layer][1].append(4)
            elif self.placetile == 0.5:
                self.mapdata[x][y][self.layer] = [0, []]
            elif self.placetile == 0.6:
                self.mapdata[x][y][self.layer][1] = []
            elif self.selectedtool in self.settings["codes"].keys():
                if self.settings["codes"][self.selectedtool] == 1:
                    self.mapdata[x][y][self.layer][0] = self.reverseslope(self.placetile + self.state)
                if self.settings["codes"][self.selectedtool] == 0:
                    if (abs(int(self.placetile))) + self.state not in self.mapdata[x][y][self.layer][1]:
                        self.mapdata[x][y][self.layer][1].append((abs(int(self.placetile))) + self.state)
            else:
                self.mapdata[x][y][self.layer][0] = self.reverseslope(self.placetile)
        if render:
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
