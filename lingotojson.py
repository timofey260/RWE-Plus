import copy
import json
import re
from files import *


def tojson(string: str):
    t = string.replace("[#", "{#").replace("point(", "\"point(").replace("rect(", "\"rect(").replace("color(",
                                                                                                     "\"color(").replace(
        ")", ")\"").replace("void", "\"void\"")
    m = list(t)
    count = 0
    for i in m:
        if i == "{":
            localcount = 0
            v = count
            while v < len(m):
                if m[v] == "[" or m[v] == "{":
                    localcount += 1
                elif m[v] == "]" or m[v] == "}":
                    localcount -= 1
                    if localcount == 0:
                        m[v] = "}"
                        break
                v += 1
        count += 1
    t = "".join(m)
    t = t.replace("#", "\"").replace(":", "\":").replace("1\":st", "1':st").replace("2\":nd", "2':nd").replace("3\":rd", "3':rd")
    # print(t)
    if t != "":
        a = json.loads(t)
    else:
        a = {}
    return a


def turntoproject(string: str):
    proj = {}
    lines = string.split("\n")
    proj["GE"] = eval(lines[0])  # geometry
    proj["TE"] = tojson(lines[1])  # tile editor and his settings
    proj["FE"] = tojson(lines[2])  # effect editor params
    proj["LE"] = tojson(lines[3])  # light editor and presets
    proj["EX"] = tojson(lines[4])  # map settings
    proj["EX2"] = tojson(lines[5])  # light and level settings
    proj["CM"] = tojson(lines[6])  # camera settigs
    proj["WL"] = tojson(lines[7])  # water level
    proj["PR"] = tojson(lines[8])  # props and settingsw
    return proj


def tolingo(string: dict):
    s = json.dumps(string)
    t = s.replace("\"point(", "point(").replace("\"rect(", "rect(").replace("\"color(", "color(").replace(")\"",
                                                                                                          ")").replace(
        "{", "[").replace("}", "]").replace("'", "")
    t = re.sub(r"\"([a-zA-Z]+[0-9]*)\":", r"#\1:", t)
    #print(t)
    return t


def toarr(col: str, mark):
    s = col.replace(mark + "(", "")
    s = s.replace(",", " ")
    s = s.replace(")", "")
    a = [float(i) if int(float(i)) != float(i) else int(i) for i in s.split()]
    return a

def makearr(col: list, mark):
    return f"{mark}({col[0]}, {col[1]})"


def inittolist(file: str):
    s = open(file, "r").readlines()
    a = {}
    a2 = []
    cat = ''
    colr = pg.Color(0, 0, 0)
    counter = 0
    counter2 = 2
    for i in s:
        i = i.replace("\n", "")
        if len(i) > 1:
            if i[0] == "-":
                counter2 += 1
                a[cat] = a2
                a2 = []
                js = tojson(i[1:])
                cat = js[0]
                colr = pg.Color(toarr(js[1], "color"))
                counter = 0
            else:

                js = tojson(i)
                img = pg.image.load(path2graphics + js["nm"] + ".png")
                sz = toarr(js["sz"], "point")
                try:
                    ln = len(js["repeatL"])
                except KeyError:
                    ln = 1
                    # sz:point(x,y) + ( #bfTiles * 2 )) * 20
                try:
                    tp = js["tp"]
                except KeyError:
                    tp = ""
                if tp == "box":  # math
                    ln = 4
                    size = (ln * sz[1] + (js["bfTiles"] * 2)) * 20
                    rect = pg.rect.Rect([0, size, sz[0] * 16, sz[1] * 16])
                elif ((ln * sz[1] + (js["bfTiles"] * 2 * ln)) * 20 + 1) > img.get_height():
                    rect = pg.rect.Rect([0, img.get_height() - sz[1] * 16, sz[0] * 16, sz[1] * 16])
                else:
                    size = (sz[1] + (js["bfTiles"] * 2)) * ln * 20 + 1
                    rect = pg.rect.Rect([0, size, sz[0] * 16, sz[1] * 16])

                try:
                    img = img.subsurface(rect)
                except ValueError:
                    try:
                        rect = pg.rect.Rect([0, img.get_height() - sz[1] * 16, sz[0] * 16, sz[1] * 16])
                        img = img.subsurface(rect)
                    except ValueError:
                        rect = pg.rect.Rect([0, 0, 1, 1])
                        img = img.subsurface(rect)
                # srf = img.copy()
                # srf.fill(colr)
                # img.set_colorkey(pg.Color(0, 0, 0))
                # srf.blit(img, [0, 0])
                # img.fill(colr)

                # arr = pg.pixelarray.PixelArray(img)
                # arr.replace(pg.Color(0, 0, 0), pg.color.Color(colr))
                # img = arr.make_surface()
                # print(colr, img.get_at([0, 0]))

                img.set_colorkey(pg.color.Color(255, 255, 255))

                a2.append({"name": js["nm"], "image": img, "size": sz, "category": cat, "color": colr, "cols": [js["specs"], js["specs2"]], "cat": [counter2, counter + 1]})
                counter += 1
    del a[""]
    a["material"] = []
    counter = 1
    for i in graphics["matposes"]:
        col = settings["global"]["color2"]
        rect = pg.rect.Rect(graphics["matposes"].index(i) * 16, 0, 16, 16)
        img = mat.subsurface(rect)
        a["material"].append({"name": i, "image": img, "size": [1, 1], "category": "material", "color": col, "cols": [[-1], 0], "cat": [1, counter]})
        counter += 1
    return a


def turntolingo(string: dict, file):
    with file as fl:
        fl.write(str(string["GE"]) + "\n")
        fl.write(tolingo(string["TE"]) + "\n")
        fl.write(tolingo(string["FE"]) + "\n")
        fl.write(tolingo(string["LE"]) + "\n")
        fl.write(tolingo(string["EX"]) + "\n")
        fl.write(tolingo(string["EX2"]) + "\n")
        fl.write(tolingo(string["CM"]) + "\n")
        fl.write(tolingo(string["WL"]) + "\n")
        fl.write(tolingo(string["PR"]) + "\n")

