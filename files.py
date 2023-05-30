import json
import pygame as pg
import os
import sys

# determine if application is a script file or frozen exe
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(__file__)

islinux = os.name == "posix"


def resolvepath(input_path): # Thanks to someone... someone nice
    if not islinux:
        return input_path
    path = input_path.replace("\\", "/")
    if os.path.isdir(path):
        return path
    directory, filename = os.path.split(path)
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower() == filename.lower():
                return os.path.join(root, file)
    return None


def loadimage(filepath):
    resolved = resolvepath(filepath)
    if filepath is None:
        raise FileNotFoundError(f"Image by path {path} does not exist", path)
    return pg.image.load(resolved)


allleters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,- =+_*()[]{}#@"

path = resolvepath(application_path + "\\files\\")
path2tutorial = resolvepath(path + "tutorial\\")
path2ui = resolvepath(path + "ui\\")
path2graphics = resolvepath(application_path + "\\drizzle\\Data\\Graphics\\")
path2cast = resolvepath(application_path + "\\drizzle\\Data\\Cast\\")
path2renderedlevels = resolvepath(application_path + "\\drizzle\\Data\\Levels\\")
path2props = resolvepath(application_path + "\\drizzle\\Data\\Props\\")
path2levels = resolvepath(application_path + "\\LevelEditorProjects\\")

path2effectPreviews = resolvepath(path + "effectPreviews\\")
path2materialPreviews = resolvepath(path + "materialPreviews\\")

pg.font.init()

graphics = json.load(open(path + "graphics.json", "r"))
settings = json.load(open(path2ui +  graphics["uifile"], "r"))
hotkeys = json.load(open(path + "hotkeys.json", "r"))
e = json.load(open(path + "effects.json", "r"))


tooltiles = loadimage(path + graphics["tooltiles"])
toolmenu = loadimage(path + graphics["toolmenu"])

mat = loadimage(path + graphics["materials"])

tag = "2.2.1"
version = "version: " + tag

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
        f = pg.font.Font(path + "/" + settings["global"]["font"], sz)
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
            if "preview" in d:
                d["preview"] = loadimage(path2effectPreviews + d["preview"] + ".png")
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
