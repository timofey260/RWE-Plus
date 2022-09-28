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

pg.font.init()

settings = json.load(open(path + "settings.json", "r"))
graphics = json.load(open(path + "graphics.json", "r"))
hotkeys = json.load(open(path + "hotkeys.json", "r"))


tooltiles = pg.image.load(path + graphics["tooltiles"])
toolmenu = pg.image.load(path + graphics["toolmenu"])

mat = pg.image.load(path + graphics["materials"])


def fs(sz):
    return pg.font.Font(path + "\\" + "Rodondo.otf", sz)