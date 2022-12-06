import json
import pygame as pg
import os
import sys

name = r"\\files\\"

# determine if application is a script file or frozen exe
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(__file__)

path = application_path + name
path2graphics = application_path + r"\\drizzle\\Data\\Graphics\\"
path2cast = application_path + r"\\drizzle\\Data\\Cast\\"
path2renderedlevels = application_path + r"\\drizzle\\Data\\Levels\\"
path2props = application_path + r"\\drizzle\\Data\\Props\\"

pg.font.init()

settings = json.load(open(path + "settings.json", "r"))
graphics = json.load(open(path + "graphics.json", "r"))
hotkeys = json.load(open(path + "hotkeys.json", "r"))
e = json.load(open(path + "effects.json", "r"))


tooltiles = pg.image.load(path + graphics["tooltiles"])
toolmenu = pg.image.load(path + graphics["toolmenu"])

mat = pg.image.load(path + graphics["materials"])

ofstop = 11
ofsleft = 11

image1size = 20
spritesize = 16
image2sprite = spritesize / image1size
sprite2image = image1size / spritesize

camw = 70
camh = 40

wladd = 5.7
bignum = 9999999


fonts: dict[pg.font.Font, ...] = {}


def fs(sz):
    if sz in fonts.keys():
        return fonts[sz]
    else:
        fonts[sz] = pg.font.Font(path + "\\" + settings["global"]["font"], sz)
        return fonts[sz]


def solveeffects(effects):
    ef = []
    for cat in effects["effects"]:
        efcat = {"nm": cat["nm"], "efs": []}
        for effect in cat["efs"]:
            d = {**effects["defaultproperties"], **effect}
            if "options" not in d:
                d["options"] = []
            for i in effects["defaultparams"]:
                d["options"].append(i)
            efcat["efs"].append(d)
        ef.append(efcat)
    # print(ef)
    return ef


def map(x, in_min, in_max, out_min, out_max):
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


effects = solveeffects(e)
