# class default():
import copy
import math
import widgets
import pygame as pg
import json
from files import *

prefix = "RWE+: "

red = [255, 0, 0]
darkred = [100, 0, 0]
blue = [50, 0, 255]
green = [0, 255, 0]
black = [0, 0, 0]
white = [255, 255, 255]

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
        for i in settings[self.menu]["unlock_keys"]:
            self.uc.append(getattr(pg, i))
    def init(self):
        self.message = ""
        pg.display.set_caption(prefix + self.menu)
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


def renderfield(field: widgets.window, size: int, mainlayer, offset, data):
    global tooltiles
    field.field.fill(field.color)
    renderedimage = pg.transform.scale(tooltiles, [
        (tooltiles.get_width() / graphics["tilesize"][0]) * size,
        (tooltiles.get_height() / graphics["tilesize"][1]) * size])
    cellsize2 = [size, size]
    for i in range(0, 3):
        renderedimage.set_alpha(50)
        if i == mainlayer:
            renderedimage.set_alpha(255)
        xp = 0
        for x in data:
            yp = 0
            if (xp + offset[0]) * size > field.field.get_width():
                break
            for y in x:
                if (yp + offset[1]) * size > field.field.get_height():
                    break
                cell = y[i][0]
                if cell == 7 and 4 not in y[i][1]:
                    data[xp][yp][i][0] = 0
                    cell = data[xp][yp][i][0]
                curtool = [graphics["shows"][str(cell)][0] * size,
                           graphics["shows"][str(cell)][1] * size]
                field.field.blit(renderedimage,
                                 [(xp + offset[0]) * size, (yp + offset[1]) * size],
                                 [curtool, cellsize2])
                for adds in y[i][1]:
                    if 4 in y[i][1] and data[xp][yp][i][0] != 7:
                        data[xp][yp][i][1].remove(4)
                    curtool = [graphics["shows2"][str(adds)][0] * size,
                               graphics["shows2"][str(adds)][1] * size]
                    field.field.blit(renderedimage,
                                     [(xp + offset[0]) * size, (yp + offset[1]) * size],
                                     [curtool, cellsize2])
                yp += 1
            xp += 1


def renderfield2(field: widgets.window, size: int, mainlayer, offset, json, items: dict):
    global mat
    material = pg.transform.scale(mat, [mat.get_width() / 16 * size, mat.get_height() / 16 * size])
    images = {}
    xp = 0
    data = json["TE"]["tlMatrix"]
    for x in data:
        yp = 0
        if (xp + offset[0]) * size > field.field.get_width():
            break
        for y in x:
            if (yp + offset[1]) * size > field.field.get_height():
                break
            cell = y[mainlayer]
            posx = (xp + offset[0]) * size
            posy = (yp + offset[1]) * size

            datcell = cell["tp"]
            datdata = cell["data"]

            if datcell == "default":
                #pg.draw.rect(field.field, red, [posx, posy, size, size], 3)
                pass
            elif datcell == "material":
                if json["GE"][xp][yp][mainlayer][0] != 0:
                    area = pg.rect.Rect([graphics["matposes"].index(datdata) * size, 0, size, size])
                    field.field.blit(material, [posx, posy], area)
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
                pg.draw.rect(field.field, it["color"], siz, 0)
                field.field.blit(it["image"], [cposx, cposy])
            elif datcell == "tileBody":
                pass
            yp += 1
        xp += 1