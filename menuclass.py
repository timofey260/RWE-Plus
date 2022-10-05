# class default():
import copy
import math
import widgets
import pygame as pg
import json
from tkinter.filedialog import askopenfilename, asksaveasfilename
from lingotojson import *
from files import *

colors = settings["global"]["colors"]

color = pg.Color(settings["global"]["color"])
color2 = pg.Color(settings["global"]["color2"])

cursor = pg.Color(colors["cursor"])
cursor2 = pg.Color(colors["cursor2"])
mirror = pg.Color(colors["mirror"])
bftiles = pg.Color(colors["bftiles"])
border = pg.Color(colors["border"])
select = pg.Color(colors["select"])

layer1 = pg.Color(colors["layer1"])
layer2 = pg.Color(colors["layer2"])

canplace = pg.Color(colors["canplace"])
cannotplace = pg.Color(colors["cannotplace"])

red = pg.Color([255, 0, 0])
darkred = pg.Color([100, 0, 0])
blue = pg.Color([50, 0, 255])
green = pg.Color([0, 255, 0])
black = pg.Color([0, 0, 0])
white = pg.Color([255, 255, 255])

mousp = True
mousp2 = True
mousp1 = True

class menu():
    def __init__(self, surface: pg.surface.Surface, data):
        self.surface = surface
        self.menu = ""
        self.data = data
        self.rectdata = [[0, 0], [0, 0], [0, 0]]
        self.uc = []
        self.init()

    def unlock_keys(self):
        self.uc = []
        for i in hotkeys[self.menu]["unlock_keys"]:
            self.uc.append(getattr(pg, i))

    def init(self):
        self.message = ""
        pg.display.set_caption(f"RWE+: {self.menu} - {self.data['path']}")
        self.buttons = []
        for i in settings[self.menu]["buttons"]:
            if len(i) == 6:
                self.buttons.append(
                    widgets.button(self.surface, pg.rect.Rect(i[1]), i[2], i[0], onpress=getattr(self, i[3]),
                                   onrelease=getattr(self, i[4]), tooltip=i[5]))
            elif len(i) == 7:
                self.buttons.append(
                    widgets.button(self.surface, pg.rect.Rect(i[1]), i[2], i[0], onpress=getattr(self, i[3]),
                                   onrelease=getattr(self, i[4]), tooltip=i[5], icon=i[6]))
        self.labels = []
        for i in settings[self.menu]["labels"]:
            if len(i) == 3:
                self.labels.append(widgets.lable(self.surface, i[0], i[1], i[2]))
            elif len(i) == 4:
                self.labels.append(widgets.lable(self.surface, i[0], i[1], i[2], i[3]))
        self.unlock_keys()
        self.resize()

    def blit(self):
        for i in self.labels:
            i.blit()
        for i in self.buttons:
            i.blit()

    def non(self):
        pass

    def resize(self):
        for i in self.buttons:
            i.resize()
        for i in self.labels:
            i.resize()

    def sendsignal(self, message):
        self.message = message

    def reload(self):
        global settings
        settings = json.load(open(path + "settings.json", "r"))
        self.init()

    def send(self, message):
        pass

    def movemiddle(self, bp, pos):
        global mousp1, mousp2, mousp3
        if bp[1] == 1 and mousp1 and (mousp2 and mousp):
            self.rectdata[0] = pos
            self.rectdata[1] = [self.xoffset, self.yoffset]
            mousp1 = False
        elif bp[1] == 1 and not mousp1 and (mousp2 and mousp):
            self.xoffset = self.rectdata[1][0] - (self.rectdata[0][0] - pos[0])
            self.yoffset = self.rectdata[1][1] - (self.rectdata[0][1] - pos[1])
        elif bp[1] == 0 and not mousp1 and (mousp2 and mousp):
            self.field.field.fill(self.field.color)
            mousp1 = True
            self.renderfield()

    def drawborder(self):
        rect = [self.xoffset * self.size, self.yoffset * self.size, len(self.data["GE"]) * self.size,
                len(self.data["GE"][0]) * self.size]
        pg.draw.rect(self.field.field, border, rect, 5)
        fig = [(self.btiles[0] + self.xoffset) * self.size, (self.btiles[1] + self.yoffset) * self.size,
               (len(self.data["GE"]) - self.btiles[2] - self.btiles[0]) * self.size,
               (len(self.data["GE"][0]) - self.btiles[3] - self.btiles[1]) * self.size]
        rect = pg.rect.Rect(fig)
        pg.draw.rect(self.field.field, bftiles, rect, 5)
        self.field.blit()

    def drawmap(self):
        self.field.field.fill(self.field.color)
        self.field.field.blit(self.fieldmap, [self.xoffset * self.size, self.yoffset * self.size])
        self.field.field.blit(self.fieldadd, [self.xoffset * self.size, self.yoffset * self.size])
        self.drawborder()


def renderfield(field: widgets.window | pg.surface.Surface, size: int, mainlayer, data):
    global tooltiles
    f = field
    f.fill(color2)
    renderedimage = pg.transform.scale(tooltiles, [
        (tooltiles.get_width() / graphics["tilesize"][0]) * size,
        (tooltiles.get_height() / graphics["tilesize"][1]) * size])
    cellsize2 = [size, size]
    for i in range(0, 3):
        renderedimage.set_alpha(50)
        if i == mainlayer:
            renderedimage.set_alpha(255)
        for xp, x in enumerate(data):
            for yp, y in enumerate(x):
                cell = y[i][0]
                if cell == 7 and 4 not in y[i][1]:
                    data[xp][yp][i][0] = 0
                    cell = data[xp][yp][i][0]
                curtool = [graphics["shows"][str(cell)][0] * size,
                           graphics["shows"][str(cell)][1] * size]
                f.blit(renderedimage, [xp * size, yp * size], [curtool, cellsize2])
                for adds in y[i][1]:
                    if 4 in y[i][1] and data[xp][yp][i][0] != 7:
                        data[xp][yp][i][1].remove(4)
                    curtool = [graphics["shows2"][str(adds)][0] * size,
                               graphics["shows2"][str(adds)][1] * size]
                    f.blit(renderedimage, [xp * size, yp * size], [curtool, cellsize2])


def renderfield2(field: widgets.window | pg.surface.Surface, size: int, mainlayer, json, items: dict):
    global mat
    material = pg.transform.scale(mat, [mat.get_width() / 16 * size, mat.get_height() / 16 * size])
    images = {}
    data = json["TE"]["tlMatrix"]
    f = field
    for xp, x in enumerate(data):
        for yp, y in enumerate(x):
            cell = y[mainlayer]
            posx = xp * size
            posy = yp * size

            datcell = cell["tp"]
            datdata = cell["data"]

            if datcell == "default":
                #pg.draw.rect(field.field, red, [posx, posy, size, size], 3)
                pass
            elif datcell == "material":
                if json["GE"][xp][yp][mainlayer][0] != 0:
                    area = pg.rect.Rect([graphics["matposes"].index(datdata) * size, 0, size, size])
                    f.blit(material, [posx, posy], area)
            elif datcell == "tileHead":
                it = None
                if datdata[1] in images.keys():
                    it = images[datdata[1]]
                else:
                    for i in items.keys():
                        for i2 in items[i]:
                            if i2["name"] == datdata[1]:
                                img = i2.copy()
                                img["image"] = pg.transform.scale(img["image"], [img["image"].get_width() / 16 * size, img["image"].get_height() / 16 * size])
                                images[datdata[1]] = img
                                it = img
                                break
                        if it is not None:
                            break
                cposx = posx - (it["size"][0] // 3) * size
                cposy = posy - (it["size"][1] // 3) * size
                siz = pg.rect.Rect([cposx, cposy, it["size"][0] * size, it["size"][1] * size])
                pg.draw.rect(f, it["color"], siz, 0)
                f.blit(it["image"], [cposx, cposy])
            elif datcell == "tileBody":
                pass

def canplaceit(data, x, y, x2, y2):
    return (0 <= x2 and x < len(data["tlMatrix"])) and (0 <= y2 and y < len(data["tlMatrix"][0]))


def destroy(data, x, y, items, layer):
    def clearitem(mx, my, layer):
        val = data["tlMatrix"][mx][my][layer]
        if val["data"] == 0:
            return
        name = val["data"][1]
        itm = None
        for i in items.keys():
            for i2 in items[i]:
                if i2["name"] == name:
                    itm = i2
                    break
            if itm is not None:
                break
        backx = mx - (itm["size"][0] // 3)
        backy = my - (itm["size"][1] // 3)
        if backx + itm["size"][0] >= len(data["tlMatrix"]) or backy + itm["size"][1] >= len(data["tlMatrix"][0]):
            return
        # startcell = self.data["TE"]["tlMatrix"][backx][backy][layer]
        sp = itm["cols"][0]
        sp2 = itm["cols"][1]
        w, h = itm["size"]
        data["tlMatrix"][mx][my][layer] = {"tp": "default", "data": 0}
        for x2 in range(w):
            for y2 in range(h):
                posx = backx + x2
                posy = backy + y2
                csp = sp[x2 * h + y2]
                if csp != -1:
                    data["tlMatrix"][posx][posy][layer] = {"tp": "default", "data": 0}
                if sp2 != 0:
                    csp = sp2[x2 * h + y2]
                    if csp != -1 and layer + 1 <= 2:
                        data["tlMatrix"][posx][posy][layer + 1] = {"tp": "default", "data": 0}

    if not canplaceit(data, x, y, x, y):
        return
    tile = data["tlMatrix"][x][y][layer]
    if tile["tp"] != "default":
        match tile["tp"]:
            case "tileBody":
                posx, posy = toarr(tile["data"][0], "point")
                clearitem(posx - 1, posy - 1, tile["data"][1] - 1)
            case "tileHead":
                clearitem(x, y, layer)
            case "material":
                data["tlMatrix"][x][y][layer] = {"tp": "default", "data": 0}