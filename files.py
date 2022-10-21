import json
import pygame as pg

import os
import sys

name = "\\files\\"

# determine if application is a script file or frozen exe
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)

path = application_path + name
path2graphics = application_path + "\\drizzle\\Data\\Graphics\\"
path2cast = application_path + "\\drizzle\\Data\\Cast\\"
path2renderedlevels = application_path + "\\drizzle\\Data\\Levels\\"

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

camw = 70
camh = 40


def fs(sz):
    return pg.font.Font(path + "\\" + settings["global"]["font"], sz)


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
    print(ef)
    return ef


effects = solveeffects(e)
