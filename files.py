import json
import pygame as pg
import os
import sys
from tkinter.simpledialog import *

# determine if application is a script file or frozen exe
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(__file__)

allleters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,- =+()[]{}#@"

path = application_path + "\\files\\"
path2ui = path + "ui\\"
path2graphics = application_path + r"\\drizzle\\Data\\Graphics\\"
path2cast = application_path + r"\\drizzle\\Data\\Cast\\"
path2renderedlevels = application_path + "\\drizzle\\Data\\Levels\\"
path2props = application_path + r"\\drizzle\\Data\\Props\\"

pg.font.init()

graphics = json.load(open(path + "graphics.json", "r"))
settings = json.load(open(path2ui +  graphics["uifile"], "r"))
hotkeys = json.load(open(path + "hotkeys.json", "r"))
e = json.load(open(path + "effects.json", "r"))


tooltiles = pg.image.load(path + graphics["tooltiles"])
toolmenu = pg.image.load(path + graphics["toolmenu"])

mat = pg.image.load(path + graphics["materials"])

ofstop = 15
ofsleft = 15

image1size = 20
spritesize = 16
image2sprite = spritesize / image1size
sprite2image = image1size / spritesize

camw = 70
camh = 40

wladd = 5.7
bignum = 9999999

inputpromtname = "RWE+ input"


fonts: dict[[pg.font.Font, int], ...] = {}


def fs(sz):
    if sz in fonts.keys():
        return fonts[sz]
    else:
        f = pg.font.Font(path + "\\" + settings["global"]["font"], sz)
        fonts[sz] = [f, f.size(allleters)[1]]
        return fonts[sz]


def solveeffects(effects):
    ef = []
    for cat in effects["effects"]:
        efcat = {"nm": cat["nm"], "color": cat["color"], "efs": []}
        for effect in cat["efs"]:
            d = {**effects["defaultproperties"], **effect}
            if "options" not in d:
                d["options"] = []
            for i in effects["defaultparams"]:
                d["options"].append(i)
            for indx, option in enumerate(d["options"]):
                if option[0].lower() == "layers": # idk why, but it is what it is
                    l = d["options"].pop(indx)
                    d["options"].insert(1, l)
                    break
            efcat["efs"].append(d)
        ef.append(efcat)
    # print(ef)
    return ef


def map(x, in_min, in_max, out_min, out_max):
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


effects = solveeffects(e)
