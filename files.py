import ujson as json
import webbrowser
from path_dict import PathDict
import pygame as pg
import os
import sys
import math
import time
from tkinter import filedialog
import jsonc  # it's so fucking dumb that i use 3 json libraries in this project why
from pathlib import Path

# determine if application is a script file or frozen exe
if getattr(sys, 'frozen', False):
    application_path = Path(os.path.dirname(sys.executable))
else:
    application_path = Path(os.path.dirname(__file__))

islinux = os.name == "posix"


def resolvepath(input_path):  # Thanks to someone... someone nice
    # returning function back for compatibility
    if not islinux:
        return str(input_path)
    path = input_path.replace("\\", "/")
    if os.path.isdir(path):
        return path
    directory, filename = os.path.split(path)
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower() == filename.lower():
                return os.path.join(root, file)
    return None


allleters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,- =+_*()[]{}#@"

path = application_path / "files"
path2favs = path / "favourites"
path2tutorial = path / "tutorial"
path2ui = path / "ui"
path2graphics = application_path / "drizzle" / "Data" / "Graphics"
path2cast = application_path / "drizzle" / "Data" / "Cast"
path2renderedlevels = application_path / "drizzle" / "Data" / "Levels"
path2props = application_path / "drizzle" / "Data" / "Props"
path2levels = application_path / "LevelEditorProjects"
path2hotkeys = path  /"hotkeys"

path2effectPreviews = path / "effectPreviews"
path2materialPreviews = path / "materialPreviews"
path2patterns = path / "patternScripts"
path2gifs = path / "gifs"

pg.font.init()

globalsettings : dict = jsonc.load(open(path / "settings.json", "r"))
settings: dict = jsonc.load(open(path2ui / globalsettings["uifile"], "r"))
hotkeys: dict = jsonc.load(open(path2hotkeys / globalsettings["hotkeyfile"], "r"))
e = jsonc.load(open(path / "effects.json", "r"))


def loadimage(filepath):
    if filepath != path / globalsettings["godimage"] and globalsettings["godmode"]:
        global god
        return god
    if not os.path.exists(filepath):
        newpath = resolvepath(filepath)
        if newpath is not None:
            return pg.image.load(newpath)
        raise FileNotFoundError(f"Image by path {os.path.relpath(path.absolute(), application_path.absolute())} does not exist", path)
    return pg.image.load(filepath)


god = loadimage(path / globalsettings["godimage"])
if god is None:
    raise Exception("how dare you")
godres = pg.Surface([0, 0])

tooltiles = loadimage(path / globalsettings["tooltiles"])
toolmenu = loadimage(path / globalsettings["toolmenu"])

load_error_count = 0

tag = "2.6.8"

ofstop = 15
ofsleft = 15

propsize = 20
image1size = globalsettings["rendertilesize"]
spritesize = 16
image2sprite = spritesize / image1size
sprite2image = image1size / spritesize

camw = 70  # camera width in blocks
camh = 40  # camera height in blocks

wladd = 5.7  # addition to water level
bignum = 9999999  # just a big number

inputpromtname = "RWE+ input"
debugmode = globalsettings["debugmode"]
timeformat = globalsettings["time_format"]

fonts: dict[[pg.font.Font, int], ...] = {}


def filetime(filepath) -> str:
    return time.strftime(timeformat, time.gmtime(os.path.getmtime(filepath)))


def smallestchange(args: list[list]) -> list:
    args2 = [i[0] for i in args]
    if len(args2) <= 0:
        return []
    currentMin = args2[0]
    for indx, i in enumerate(currentMin):
        currentName = i
        for item in args:
            if item[0][0] in [".index", ".pop", ".append", ".insert"]:
                return []
            if item[0] == currentMin:
                continue
            if item[0][indx] != currentName:
                for sorteditem in args:
                    sorteditem[0] = sorteditem[0][indx:]
                return currentMin[:indx]
    return []


def rotatepoint(point, angle):
    px, py = point
    angle = math.radians(angle)
    qx = math.cos(angle) * px - math.sin(angle) * py
    qy = math.sin(angle) * px + math.cos(angle) * py
    return pg.Vector2([qx, qy])


class RWELevel:
    def __init__(self, data=None):
        if data is None:
            self.data = PathDict({})
        else:
            self.data = PathDict(data)

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        self.data[key] = value

    def GE_data(self, x, y, layer):
        return self.data["GE"][int(x)][int(y)][layer]

    def TE_data(self, x, y, layer):
        return self.data["TE"]["tlMatrix"][int(x)][int(y)][layer]


def fs(sz) -> list[pg.font.Font, int]:
    if sz in fonts.keys():
        return fonts[sz]
    else:
        f = pg.font.Font(path / settings["global"]["font"], sz)
        fonts[sz] = [f, f.size(allleters)[1]]
        return fonts[sz]


def plotLineLow(pointa: pg.Vector2, pointb: pg.Vector2, callback):
    if pointa.x > pointb.x:
        pointa, pointb = pointb, pointa
    dx = pointb.x - pointa.x
    dy = pointb.y - pointa.y
    yi = 1
    if dy < 0:
        yi = -1
        dy = -dy
    D = (2 * dy) - dx
    y = pointa.y

    for x in range(int(pointa.x), int(pointb.x)):
        callback(pg.Vector2(x, y), False)
        if D > 0:
            y = y + yi
            D = D + (2 * (dy - dx))
        else:
            D = D + 2 * dy


def plotLineHigh(pointa: pg.Vector2, pointb: pg.Vector2, callback):
    if pointa.y > pointb.y:
        pointa, pointb = pointb, pointa
    dx = pointb.x - pointa.x
    dy = pointb.y - pointa.y
    xi = 1
    if dx < 0:
        xi = -1
        dx = -dx
    D = (2 * dx) - dy
    x = pointa.x

    for y in range(int(pointa.y), int(pointb.y)):
        callback(pg.Vector2(x, y), False)
        if D > 0:
            x = x + xi
            D = D + (2 * (dx - dy))
        else:
            D = D + 2 * dx


def plotLine(pointa, pointb, callback):
    if abs(pointb.y - pointa.y) < abs(pointb.x - pointa.x):
        plotLineLow(pointa, pointb, callback)
    else:
        plotLineHigh(pointa, pointb, callback)


def rect2ellipse(rect: pg.Rect, hollow, callback):
    width = rect.width // 2
    height = rect.height // 2
    origin = rect.center
    hh = height * height
    ww = width * width
    hhww = hh * ww
    x0 = width
    dx = 0
    for x in range(-width, width + 1):
        if x == -width or x == width or not hollow:
            callback(pg.Vector2(origin[0] + x, origin[1]), False)
    for y in range(1, height + 1):
        x1 = x0 - (dx - 1)
        while x1 > 0:
            if x1*x1*hh + y*y*ww <= hhww:
                break
            x1 -= 1
        dx = x0 - x1
        x0 = x1
        for x in range(-x0, x0 + 1):
            if x == -x0 or x == x0 or not hollow:
                callback(pg.Vector2(origin[0] + x, origin[1] - y), False)
                callback(pg.Vector2(origin[0] + x, origin[1] + y), False)

    if not hollow:
        return

    y0 = height
    dy = 0
    for y in range(-height, height + 1):
        if y == -height or y == height or not hollow:
            callback(pg.Vector2(origin[0], origin[1] + y), False)
    for x in range(1, width + 1):
        y1 = y0 - (dy - 1)
        while y1 > 0:
            if y1*y1*ww + x*x*hh <= hhww:
                break
            y1 -= 1
        dy = y0 - y1
        y0 = y1
        for y in range(-y0, y0 + 1):
            if y == -y0 or y == y0 or not hollow:
                callback(pg.Vector2(origin[0] - x, origin[1] + y), False)
                callback(pg.Vector2(origin[0] + x, origin[1] + y), False)


def map2(x, in_min, in_max, out_min, out_max):
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def deepcopy(data):
    if type(data) is RWELevel:
        return RWELevel(json.loads(json.dumps(data.data.data)))
    return json.loads(json.dumps(data))

def report():
    webbrowser.open("https://github.com/timofey260/RWE-Plus/issues/new/choose")


def github():
    webbrowser.open("https://github.com/timofey260/RWE-Plus")


def tutorial():
    webbrowser.open(globalsettings["tutorial_link"])


def log_to_load_log(message, error=False, nl=True):
    global load_error_count
    with open(application_path / "loadLog.txt", "a") as load_log:
        load_log.write(f"{'[ERROR]: ' if error else ''}{message}")
        if nl:
            load_log.write("\n")
    print(message)
    if error:
        load_error_count += 1


def errorcount_get():
    return load_error_count
