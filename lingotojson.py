import copy
import json
import re
from files import *
import math


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
    print("Loading level...")
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
    t = s.replace("\"point(", "point(").replace("\"rect(", "rect(").replace("\"color(", "color(")\
        .replace(")\"", ")").replace("{", "[").replace("}", "]").replace("'", "")
    t = re.sub(r"\"([a-zA-Z]+[0-9]*)\":", r"#\1:", t)
    #print(t)
    return t


def toarr(col: str, mark):
    s = col.replace(mark + "(", "")
    s = s.replace(",", " ")
    s = s.replace(")", "")
    a = []
    for i in s.split():
        n = float(i)
        if float(i) == int(float(i)):
            n = int(float(i))
        a.append(n)
    return a


def makearr(col: list | pg.Vector2, mark):
    return f"{mark}({col[0]}, {col[1]})"


def init_solve(file: str):
    s = open(file, "r").readlines()
    a = {}
    a2 = []
    cat = ''
    counter = 0
    counter2 = 2
    for i in s:
        i = i.replace("\n", "")
        if len(i) > 1:
            if i[0] == "-":
                counter2 += 1
                a[cat] = a2
                js = tojson(i[1:])
                a2 = [js]
                cat = js[0]
                counter = 0
            else:
                js = tojson(i)
                item = {}
                for p, val in js.items():
                    item[p] = val
                a2.append(item)
                counter += 1
    a[cat] = a2
    return a


def inittolist():
    inv = settings["TE"]["LEtiles"]
    solved = init_solve(path2graphics + "init.txt")
    del solved['']
    solved_copy = solved.copy()
    for catnum, catitem in enumerate(solved.items()):
        cat, items = catitem
        colr = pg.Color(toarr(items[0][1], "color"))
        solved_copy[cat] = []
        for indx, item in enumerate(items[1:]):

            img = pg.image.load(path2graphics + item["nm"] + ".png")
            sz = toarr(item["sz"], "point")
            try:
                ln = len(item["repeatL"])
            except KeyError:
                ln = 1
                # sz:point(x,y) + ( #bfTiles * 2 )) * 20
            try:
                tp = item["tp"]
            except KeyError:
                tp = ""
            if tp == "box":  # math
                ln = 4
                size = (ln * sz[1] + (item["bfTiles"] * 2)) * image1size
                rect = pg.rect.Rect([0, size, sz[0] * spritesize, sz[1] * spritesize])
            elif ((ln * sz[1] + (item["bfTiles"] * 2 * ln)) * image1size + 1) > img.get_height():
                rect = pg.rect.Rect([0, img.get_height() - sz[1] * spritesize, sz[0] * spritesize, sz[1] * spritesize])
            else:
                size = (sz[1] + (item["bfTiles"] * 2)) * ln * image1size
                rect = pg.rect.Rect([0, size + 1, sz[0] * spritesize, sz[1] * spritesize])

            try:
                img = img.subsurface(rect)
            except ValueError:
                try:
                    rect = pg.rect.Rect([0, img.get_height() - sz[1] * spritesize, sz[0] * spritesize, sz[1] * spritesize])
                    img = img.subsurface(rect)
                except ValueError:
                    rect = pg.rect.Rect([0, 0, 1, 1])
                    img = img.subsurface(rect)
            # srf = img.copy()
            # srf.fill(colr)
            # img.set_colorkey(pg.Color(0, 0, 0))
            # srf.blit(img, [0, 0])
            # img.fill(colr)
            if not inv:
                img.set_colorkey(pg.color.Color(255, 255, 255))
            if inv:
                s = pg.Surface(img.get_size())
                s.blit(img, [0, 0])
                arr = pg.pixelarray.PixelArray(s.copy())
                arr.replace(pg.Color(0, 0, 0), colr)
                img = arr.make_surface()
                img.set_colorkey(pg.Color(255, 255, 255))

            newitem = {
                "name": item["nm"],
                "tp": item.get("tp"),
                "repeatL": item["repeatL"] if item.get("repeatL") is not None else [1],
                "bfTiles": item["bfTiles"],
                "image": img,
                "size": sz,
                "category": cat,
                "color": colr,
                "cols": [item["specs"], item["specs2"]],
                "cat": [catnum + 1, indx + 1],
                "tags": item["tags"]
            }
            solved_copy[cat].append(newitem)
    solved_copy["material"] = []
    counter = 1
    for i in graphics["matposes"]:
        col = settings["global"]["color2"]
        rect = pg.rect.Rect(graphics["matposes"].index(i) * 16, 0, 16, 16)
        img = mat.subsurface(rect)
        solved_copy["material"].append(
            {
                "name": i,
                "tp": None,
                "repeatL": [1],
                "bfTiles": 0,
                "image": img,
                "size": [1, 1],
                "category": "material",
                "color": col,
                "cols": [[-1], 0],
                "cat": [1, counter],
                "tags": [""]
            })
        counter += 1
    return solved_copy


def renderlevel(data):
    fl = os.path.splitext(data["path"])[0] + ".txt"
    file = open(fl, "w")
    turntolingo(data, file)
    os.system(f"{application_path}\\drizzle\\Drizzle.ConsoleApp.exe render {fl}")
    print(path2renderedlevels)
    os.system("explorer " + path2renderedlevels)


def getcolors():
    solved = open(application_path + '/drizzle/Data/Props/propColors.txt', 'r').readlines()
    cols = []
    for line in solved:
        if line[0] != '[':
            continue
        l = tojson(line)
        l[1] = toarr(l[1], "color")
        cols.append(l)
    return cols


def getprops(tiles: dict):
    # turning tiles to props and then add them to all other props
    solved = {**init_solve(path2props + "init.txt"), **init_solve(path + "additionprops.txt")}
    del solved['']
    solved_copy = solved.copy()
    for catnum, catitem in enumerate(solved.items()):
        cat, items = catitem
        colr = pg.Color(toarr(items[0][1], "color"))
        solved_copy[cat] = []
        for indx, item in enumerate(items[1:]):

            img = pg.image.load(path2props + item["nm"] + ".png")
            img.set_colorkey(pg.color.Color(255, 255, 255))

            images = []

            ws, hs = img.get_size()
            if item.get("pxlSize") is not None:
                w, h = toarr(item["pxlSize"], "point")
            else:
                w, h = ws, hs
                if item.get("vars") is not None:
                    w = round(ws / item["vars"])
                if item.get("repeatL") is not None:
                    h = math.floor((hs / len(item["repeatL"])))
                    if item.get("sz") is not None and len(item["repeatL"]) < 2:
                        sz = toarr(item["sz"], "point")
                        w = sz[0] * image1size
                        h = sz[1] * image1size

                    cons = 0.4
                    wh = pg.Color("#ffffff")
                    gr = pg.Color("#dddddd")
                    bl = pg.Color("#000000")

                    vars = 1
                    if item.get("vars") is not None:
                        vars = item["vars"]

                    for varindx in range(vars):
                        curcol = gr

                        for iindex, _ in enumerate(item["repeatL"]):
                            # print(img, item["nm"], varindx * w, hs - h, w, h)
                            curcol = curcol.lerp(bl, cons)
                            ss = img.subsurface(varindx * w, (len(item["repeatL"]) - 1 - iindex) * h, w, h).copy()
                            pxl = pg.PixelArray(ss)
                            pxl.replace(bl, curcol)
                            ss = pxl.make_surface()
                            ss.set_colorkey(wh)
                            img.blit(ss, [0, hs - h])

            if item.get("vars") is not None:
                for iindex in range(item["vars"]):
                    images.append(img.subsurface(iindex * w, 0, w, h))
            else:
                images.append(img.subsurface(0, hs - h, w, h))

            newitem = solved[cat][indx + 1]
            newitem["images"] = images
            newitem["color"] = list(colr)
            solved_copy[cat].append(newitem)
    # solved_copy["material"] = []
    # for cat in tiles:
    #     pass
    count = 0
    count2 = 0
    title = ""
    itemlist = []
    for cat, items in tiles.items():
        if cat == "material":
            continue
        for indx, tile in enumerate(items[1:]):
            if count <= 0:
                count = settings["PE"]["elements_as_tiles_count"]
                if title != "":
                    solved_copy[title] = itemlist
                    itemlist = []
                count2 += 1
                title = f"tiles as prop {count2}"
            if tile["tp"] == "voxelStruct" and "notProp" not in tile["tags"]:
                returnimage = pg.Surface(pg.Vector2(tile["image"].get_width(), tile["image"].get_height()) + pg.Vector2(spritesize, spritesize) * tile["bfTiles"] * 2)
                returnimage.fill(pg.Color(255, 255, 255))
                returnimage.blit(tile["image"], pg.Vector2(spritesize, spritesize) * tile["bfTiles"])
                returnimage.set_colorkey(pg.Color(255, 255, 255))
                itemlist.append({
                    "nm": tile["name"],
                    "tp": "standard",
                    "images": [returnimage],
                    "colorTreatment": "standard",
                    "color": settings["PE"]["elements_as_tiles_color"],
                    "sz": list(pg.Vector2(tile["size"]) + pg.Vector2(tile["bfTiles"] * 2, tile["bfTiles"] * 2)),
                    "depth": 10 + int(tile["cols"][1] != []),
                    "repeatL": tile["repeatL"],
                    "tags": ["tile"],
                    "layerExceptions": [],
                    "notes": ["Tile as prop"]
                })
                count -= 1
    solved_copy[title] = itemlist
    return solved_copy


def turntolingo(string: dict, file):
    with file as fl:
        fl.write(str(string["GE"]) + "\r")
        fl.write(tolingo(string["TE"]) + "\r")
        fl.write(tolingo(string["FE"]) + "\r")
        fl.write(tolingo(string["LE"]) + "\r")
        fl.write(tolingo(string["EX"]) + "\r")
        fl.write(tolingo(string["EX2"]) + "\r")
        fl.write(tolingo(string["CM"]) + "\r")
        fl.write(tolingo(string["WL"]) + "\r")
        fl.write(tolingo(string["PR"]) + "\r")

