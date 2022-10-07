import pygame as pg
import copy
import json
import os
from files import settings, fs, path

pg.font.init()


bol = True
mul = settings["global"]["colormul"]
black = [0, 0, 0]
white = [255, 255, 255]


def mts(window, text: str = "", x: int = 0, y: int = 0, col=None, fontsize=settings["global"]["fontsize"],
        centered: bool = False):
    if col is None:
        col = [0, 0, 0]
    fontr = fs(fontsize)
    screen_text = fontr.render(text, True, col, None)
    if centered:
        window.blit(screen_text, [x - screen_text.get_width() / 2, y - screen_text.get_height() / 2])
    else:
        if x + screen_text.get_width() > window.get_width():
            window.blit(screen_text, [x - screen_text.get_width(), y])
        else:
            window.blit(screen_text, [x, y])


class button:
    def __init__(self, surface: pg.surface.Surface, rect: pg.rect.Rect, col, text: str, icon=None, onpress=None,
                 onrelease=None, tooltip: str = ""):
        self.surface = surface
        self.rect = copy.deepcopy(rect)
        self.lastrect = copy.deepcopy(rect)
        self.col = pg.Color(col)
        self.text = text
        self.originstext = text
        self.icon = None
        self.loadicon = icon
        if icon is not None:
            cut = [icon[1][0] * settings["global"]["size"], icon[1][1] * settings["global"]["size"],
                   settings["global"]["size"], settings["global"]["size"]]
            image = pg.image.load(path + icon[0]).subsurface(cut)
            wh = image.get_height() / settings["global"]["size"] * (rect.height / 100 * surface.get_height())
            size = [wh, wh]
            image = pg.transform.scale(image, size)
            self.icon = image
        self.onpress = onpress
        self.onrelease = onrelease
        self.tooltip = tooltip
        self.bol = True

    def blit(self, fontsize=30):
        global bol
        cp = False
        col = self.col
        if self.onmouseover():
            cp = True
            if pg.mouse.get_pressed(3)[0] == 1 and bol:
                self.bol = False
                bol = False
                if self.onpress is not None:
                    self.onpress()
            elif pg.mouse.get_pressed(3)[0] == 0 and not bol:
                self.bol = True
                bol = True
                if self.onrelease is not None:
                    self.onrelease()

            col = [abs(self.col.r - mul), abs(self.col.g - mul), abs(self.col.b - mul)]
        pg.draw.rect(self.surface, col, self.rect, 0, 10)
        if self.icon is None:
            mts(self.surface, self.text, self.rect.center[0], self.rect.center[1], black, centered=True, fontsize=fontsize)
        else:
            self.icon.set_alpha(255)
            if cp:
                self.icon.set_alpha(50)
            px = self.rect.w / 2 - self.icon.get_width() / 2
            py = self.rect.h / 2 - self.icon.get_height() / 2
            pos = [px + self.rect.x, py + self.rect.y]
            self.surface.blit(self.icon, pos)
        if cp:
            mts(self.surface, self.tooltip, pg.mouse.get_pos()[0], pg.mouse.get_pos()[1] - 20, white, centered=False)

    def resize(self):
        x = self.lastrect.x / 100 * self.surface.get_width()
        y = self.lastrect.y / 100 * self.surface.get_height()
        w = self.lastrect.w / 100 * self.surface.get_width()
        h = self.lastrect.h / 100 * self.surface.get_height()
        self.rect.update(x, y, w, h)

        if self.icon is not None:
            cut = [self.loadicon[1][0] * settings["global"]["size"], self.loadicon[1][1] * settings["global"]["size"],
                   settings["global"]["size"], settings["global"]["size"]]
            image = pg.image.load(path + self.loadicon[0]).subsurface(cut)
            wh = image.get_height() / settings["global"]["size"] * self.rect.height
            size = [wh, wh]
            image = pg.transform.scale(image, size)
            self.icon = image

    def onmouseover(self):
        return self.rect.collidepoint(pg.mouse.get_pos())


class window:
    def __init__(self, surface: pg.surface.Surface, data):
        self.surface = surface
        self.rect = copy.deepcopy(pg.rect.Rect(data["rect"]))
        self.rect2 = copy.deepcopy(pg.rect.Rect(data["rect"]))
        self.field = pg.surface.Surface(
            [self.rect.width / 100 * surface.get_width(), self.rect.height / 100 * surface.get_height()])
        self.color = data["color"]
        self.border = data["border"]

    def blit(self, draw=True):
        if draw:
            pg.draw.rect(self.surface, self.color, self.rect)
            pg.draw.rect(self.surface, self.border, self.rect, 6)
        self.surface.blit(self.field, self.rect.topleft)

    def resize(self):
        self.field = pg.surface.Surface(
            [self.rect2.width / 100 * self.surface.get_width(), self.rect2.height / 100 * self.surface.get_height()])
        self.rect = pg.rect.Rect([
            self.rect2.x / 100 * self.surface.get_width(),
            self.rect2.y / 100 * self.surface.get_height(),
            self.rect2.width / 100 * self.surface.get_width(),
            self.rect2.height / 100 * self.surface.get_height()])

    def copy(self):
        wcopy = window(self.surface, {"rect": [0, 0, 1, 1], "color": [0, 0, 0], "border": [0, 0, 0]})
        wcopy.rect = self.rect.copy()
        wcopy.rect2 = self.rect2.copy()
        wcopy.field = self.field.copy()
        self.color = self.color.copy()
        self.border = self.border.copy()
        return wcopy


class lable:
    def __init__(self, surface: pg.surface.Surface, text, pos, color, fontsize=15):
        self.surface = surface
        self.text = text
        self.originaltext = text
        self.pos = copy.deepcopy(pos)
        self.posp = copy.deepcopy(pos)
        self.color = color
        self.fontsize = fontsize

    def blit(self):
        mts(self.surface, self.text, self.pos[0], self.pos[1], self.color, self.fontsize)

    def resize(self):
        self.pos[0] = self.posp[0] / 100 * self.surface.get_width()
        self.pos[1] = self.posp[1] / 100 * self.surface.get_height()

    def set_text(self, text):
        self.text = text
