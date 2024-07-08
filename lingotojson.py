import copy
import json.decoder
import os
import random
import re
import subprocess
import multiprocessing
import json as jsonenc
import sys

from files import *
import math

notfound = loadimage(path / "notfound.png")
notfound.set_colorkey(pg.Color(255, 255, 255))
notfoundtile = {
    "name": "unloaded tile",
    "tp": "notfound",
    "repeatL": [1],
    "bfTiles": 0,
    "image": notfound,
    "size": [2, 2],
    "category": "material",
    "color": pg.Color(255, 255, 255),
    "cols": [[-1], 0],
    "cat": [1, 1],
    "tags": [""]
}
defaultlevel = open(path / "default.txt", "r").readlines()


def tojson(string: str, replacement: str = None):
    try:
        closebracketscount = string.count("]")
        openbracketscount = string.count("[")
        t = string
        if closebracketscount > openbracketscount:
            t = t[:-1]
        t = t.replace("#Data:", "#data:") \
            .replace("#Options:", "#options:") \
            .replace("[#", "{#") \
            .replace("point(", "\"point(") \
            .replace("rect(", "\"rect(") \
            .replace("color(", "\"color(") \
            .replace("color (", "\"color(") \
            .replace(")\"", ")") \
            .replace(")", ")\"") \
            .replace("void", "0")
        count = 0
        m = list(t)
        brcount = 0
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
            if i in ["{", "["]:
                brcount += 1
            elif i in ["}", "]"]:
                brcount -= 1
                if brcount == 0:
                    m = m[:count+1]
                    break
        t = "".join(m)
        t = t.replace("#", "\"").replace(":", "\":").replace("1\":st", "1':st").replace("2\":nd", "2':nd").replace("3\":rd", "3':rd")
        # print(t)
        if t.replace(" ", "") != "":
            if replacement is not None:
                return {**tojson(replacement), **json.loads(t)}
            return json.loads(t)
        else:
            if replacement is not None:
                return tojson(replacement)
            return {}
    except:
        print("fixing, just wait")
        if replacement is None:
            raise
        return tojson(replacement)


def turntoproject(string: str) -> RWELevel:
    proj = RWELevel()
    lines = string.split("\n")
    print("Loading level...")
    proj["GE"] = json.loads(lines[0])  # geometry
    proj["TE"] = tojson(lines[1])  # tile editor and his settings
    proj["FE"] = tojson(lines[2])  # effect editor params
    proj["LE"] = tojson(lines[3], defaultlevel[3])  # light editor and presets
    proj["EX"] = tojson(lines[4], defaultlevel[4])  # map settings
    proj["EX2"] = tojson(lines[5], defaultlevel[5])  # light and level settings
    proj["CM"] = tojson(lines[6], defaultlevel[6])  # camera settings
    proj["WL"] = tojson(lines[7], defaultlevel[7])  # water level
    proj["PR"] = tojson(lines[8], defaultlevel[8])  # props and settings why the hell i typed both settings wrong???
    return proj


def tolingo(string: dict):
    s = jsonenc.dumps(string)
    # print(s)
    t = s.replace("\"point(", "point(").replace("\"rect(", "rect(").replace("\"color(", "color(") \
        .replace(")\"", ")").replace("{", "[").replace("}", "]").replace("'", "")
    t = re.sub(r"\"([a-zA-Z]+[0-9]*)\":", r"#\1:", t)
    # print(t)
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


class ItemData():
    def __init__(self):
        self.data = []

    def __getitem__(self, item):
        if type(item) is str:
            return self.searchitem(item)
        elif type(item) is int:
            return self.data[item]
        elif type(item) is tuple:
            return self.searchitem(item[1], item[0])
        return None

    def searchitem(self, name, category=None):
        if category is None:
            for catnum, cat in enumerate(self.data):
                for itemnum, items in enumerate(cat["items"]):
                    if items["nm"] == name:
                        return items
        else:
            for itemnum, items in enumerate(self.data[self.categories.index(category)]["items"]):
                if items["nm"] == name:
                    return items
        return None

    def getnameindex(self, cat, name):
        for i, v in enumerate(self.data[cat]["items"]):
            if v["nm"] == name:
                return i
        return None


    @property
    def categories(self):
        return [i["name"] for i in self.data]

    @property
    def colors(self):
        return [i["color"] for i in self.data]

    def append(self, category_data):
        self.data.append(category_data)

    def addcat(self, name, color):
        self.data.append({"name": name, "color": color, "items": []})

    def remove(self, category_data):
        self.data.remove(category_data)

    def insert(self, index, category_data):
        self.data.insert(index, category_data)

    def pop(self, index):
        self.data.pop(index)

    def __str__(self):
        return str(self.data)

    def __len__(self):
        return len(self.data)

    def isempty(self):
        return len(self.data) == 0


def init_solve(files: list[str,]):
    output = ItemData()
    for file in files:
        s = open(file, "r").readlines()
        category_data = {}
        item_counter = 0
        findcategory = True  # if true, all non-category lines will be ignored until a category line is found
        for ln, i in enumerate(s):
            i = i.strip()
            if len(i) > 1:
                if i[0] == "-":
                    try:
                        if category_data:
                            output.append(category_data)
                        js = tojson(i[1:])
                        category_data = {"name": js[0], "color": pg.Color(toarr(js[1], "color")), "items": []}
                        item_counter = 0
                        findcategory = False
                    except json.JSONDecodeError:
                        log_to_load_log(
                            f"Failed to convert init CATEGORY line \"{i}\" (line number: {ln}) in file \"{os.path.relpath(file, application_path)}\"! Skipping line and all subsequent tiles!",
                            True)
                        findcategory = True
                        continue
                elif not findcategory:
                    try:
                        js = tojson(i)
                        item = {}
                        for p, val in js.items():
                            item[p] = val
                        category_data["items"].append(item)
                        item_counter += 1
                    except json.JSONDecodeError:
                        log_to_load_log(
                        f"Failed to convert init ITEM line \"{i}\" (line number: {ln}) in file \"{os.path.relpath(file, application_path)}\"! Skipping line!",
                        True)
                        continue
        output.append(category_data)
        # output.remove([])
    return output


def inittolist(window: pg.Surface):
    def printmessage(message):
        surf = f.render(message, True, pg.color.THECOLORS["white"], None)
        pg.draw.rect(window, pg.color.THECOLORS["black"], [0, 0, window.get_width(), surf.get_height()])
        window.blit(surf, [0, 0])
        pg.display.update()
    inv = settings["TE"]["LEtiles"]
    tilefiles = [path2graphics / i for i in globalsettings["tileinits"]]
    solved = init_solve(tilefiles)
    solved_copy = copy.deepcopy(solved)
    f = pg.font.Font(path / settings["global"]["font"], 20)
    for catnum, catitem in enumerate(solved.data):
        cat = catitem["name"]

        items = catitem["items"]
        colr = catitem["color"]
        solved_copy[catnum]["items"] = []
        for indx, item in enumerate(items):
            printmessage(f"Loading tile {item['nm']}...")
            try:
                img = loadimage(f"{path2graphics / item['nm']}.png")
            except FileNotFoundError:
                continue
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
                size = (ln * sz[1] + (item.get("bfTiles", 0) * 2)) * image1size
                rect = pg.rect.Rect([0, size, sz[0] * spritesize, sz[1] * spritesize])
            elif ((ln * sz[1] + (item.get("bfTiles", 0) * 2 * ln)) * image1size + 1) > img.get_height():
                rect = pg.rect.Rect([0, img.get_height() - sz[1] * spritesize, sz[0] * spritesize, sz[1] * spritesize])
            else:
                size = (sz[1] + (item.get("bfTiles", 0) * 2)) * ln * image1size
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
                "nm": item["nm"],
                "tp": item.get("tp"),
                "repeatL": item["repeatL"] if item.get("repeatL") is not None else [1],
                "description": "Size" + str(sz),
                "bfTiles": item.get("bfTiles", 0),
                "image": img,
                "size": sz,
                "category": cat,
                "color": colr,
                "cols": [item.get("specs", [1]), item.get("specs2", 0)],
                "cat": [catnum + 1, indx + 1],
                "tags": item["tags"],
                "printcols": True
            }
            solved_copy[catnum]["items"].append(newitem)
    matcat = "materials 0"
    matcatcount = 0
    solved_copy.insert(matcatcount, {"name": matcat, "color": pg.Color(0, 0, 0), "items": []})
    for k, v in globalsettings["matposes"].items():
        col = pg.Color(v)
        img = pg.Surface([image1size, image1size], pg.SRCALPHA)
        img.fill(pg.Color(0, 0, 0, 0))
        ms = globalsettings["matsize"]
        pg.draw.rect(img, v, pg.Rect(ms[0], ms[0], ms[1], ms[1]))
        try:
            preview = loadimage(path2materialPreviews / (k + ".png"))
        except FileNotFoundError:
            preview = pg.Surface([image1size, image1size])
            preview.set_alpha(0)
        preview.set_colorkey(pg.Color(255, 255, 255))
        printmessage(f"Loading material {k}")
        solved_copy[matcatcount]["items"].append(
            {
                "nm": k,
                "tp": None,
                "repeatL": [1],
                "description": "Material",
                "bfTiles": 0,
                "image": img,
                "size": [1, 1],
                "category": matcat,
                "color": col,
                "cols": [[-1], 0],
                "cat": [matcatcount + 1, len(solved_copy[matcatcount]["items"]) + 1],
                "tags": ["material"],
                "preview": preview
            })
        if len(solved_copy[matcatcount]["items"]) > 30:
            matcatcount += 1
            matcat = f"materials {matcatcount}"
            solved_copy.insert(matcatcount, {"name": matcat, "color": pg.Color(0, 0, 0), "items": []})
    printmessage("All tiles loaded!")
    return solved_copy


def renderlevel(data):
    fl = os.path.splitext(data["path"])[0] + ".txt"
    file = open(fl, "w")
    turntolingo(data, file)
    #print(f"\"{application_path}/drizzle/Drizzle.ConsoleApp{'' if islinux else '.exe'}")
    # subprocess.Popen([f"{application_path}/drizzle/Drizzle.ConsoleApp{'' if islinux else '.exe'}", "render", fl], shell=True)
    p = multiprocessing.Process(target=renderlevelProccess, args=(f"{application_path}/drizzle/Drizzle.ConsoleApp{'' if islinux else '.exe'} render \"{fl}\"", ))
    pickedgif = random.choice(list(globalsettings["rendergifimages"].keys()))
    theimage = loadimage(path2gifs / pickedgif)
    fontr: pg.font.Font = fs(30)[0]
    text = fontr.render(settings["global"].get("renderingscugtext", "wendewing level :3 Esc to cancel"), True, pg.Color(255, 255, 255), None)
    frame = 0
    size = globalsettings["rendergifimages"][pickedgif]
    pg.display.get_surface().fill([0, 0, 0])
    clock = pg.time.Clock()
    p.start()
    if globalsettings["removerendergifs"]:
        return
    while p.is_alive():
        for e in pg.event.get():
            if e.type == pg.QUIT or (e.type == pg.KEYDOWN and (e.key in (pg.K_ESCAPE, pg.K_RETURN, pg.K_TAB))):
                print("rendering canceled")
                p.terminate()
                # p.kill()
                return

        # pg.draw.rect(pg.display.get_surface(), [0, 0, 0], [0, 0, 200, 200])
        # 164 x 127
        rightimage = theimage.subsurface([(size[0] * frame) % theimage.get_width(), 0, size[0], size[1]])
        rect = rightimage.get_rect()
        pg.draw.rect(pg.display.get_surface(), pg.Color(0, 0, 0), [pg.display.get_window_size()[0] / 2 - rect.centerx,
                                                        pg.display.get_window_size()[1] / 2 - rect.centery,
                                                                   rightimage.get_width(),
                                                                   rightimage.get_height()])
        pg.display.get_surface().blit(rightimage, [pg.display.get_window_size()[0] / 2 - rect.centerx,
                                                        pg.display.get_window_size()[1] / 2 - rect.centery])
        pg.display.get_surface().blit(text, [0, 0])
        pg.display.flip()
        pg.display.update()
        clock.tick(30)
        frame += 1


def renderlevelProccess(data):
    os.system(data)
    # os.system(f"{application_path}/drizzle/Drizzle.ConsoleApp{'' if islinux else '.exe'} render {fl}")
    if not islinux:
        os.system("start " + str(resolvepath(path2renderedlevels)))


def getcolors():
    solved = open(application_path / "drizzle" / "Data" / "Props" / "propColors.txt", 'r').readlines()
    cols = []
    for line in solved:
        if line[0] != '[':
            continue
        l = tojson(line)
        l[1] = toarr(l[1], "color")
        cols.append(l)
    return cols


def addprop(item: dict, img: pg.Surface):
    img.set_colorkey(pg.color.Color(255, 255, 255))

    images = []
    if item.get("vars") is not None:
        item["vars"] = max(item["vars"], 1)

    ws, hs = img.get_size()
    if item.get("pxlSize") is not None:
        w, h = toarr(item["pxlSize"], "point")
    else:
        w, h = ws, hs
        if item.get("vars") is not None:
            w = round(ws / item["vars"])
        if item.get("repeatL") is not None:
            repeatl = item.get("repeatL")
            h = math.floor((hs / len(repeatl)))
            if item.get("sz") is not None:
                sz = toarr(item["sz"], "point")
                w = min(sz[0] * propsize, ws)
                h = sz[1] * propsize

            cons = 0.4
            wh = pg.Color("#ffffff")
            gr = pg.Color("#dddddd")
            bl = pg.Color("#000000")

            vars = item.get("vars", 1)

            for varindx in range(vars):
                curcol = gr

                for iindex, _ in enumerate(repeatl):
                    # print(img, item["nm"], varindx * w, h * (len(repeatl) - 1), w, h)
                    curcol = curcol.lerp(bl, cons)
                    rect = pg.Rect(varindx * w, (len(repeatl) - 1 - iindex) * h, w, h + 1)
                    rect = rect.clip(pg.Rect(0, 0, ws, hs))
                    try:
                        ss = img.subsurface(rect).copy()
                    except ValueError:
                        continue

                    if item["colorTreatment"] == "bevel":
                        pxl = pg.PixelArray(ss)
                        pxl.replace(bl, curcol)
                        ss = pxl.make_surface()
                    ss.set_colorkey(wh)
                    img.blit(ss, [0, h * (len(repeatl) - 1)])

    if item.get("vars") is not None:
        for iindex in range(item["vars"]):
            images.append(img.subsurface(iindex * w, 0, w, h))
    else:
        images.append(img.subsurface(0, hs - h if item.get("colorTreatment", "") == "bevel" else 0, w, h))
    return images


def getprops(tiles: dict, window: pg.Surface):
    # turning tiles to props and then add them to all other props
    def printmessage(message):
        surf = f.render(message, True, pg.color.THECOLORS["white"], None)
        pg.draw.rect(window, pg.color.THECOLORS["black"], [0, 0, window.get_width(), surf.get_height()])
        window.blit(surf, [0, 0])
        pg.display.update()
    propfiles = [path2props / i for i in globalsettings["propinits"]]
    propfiles.append(path / "additionprops.txt")
    solved = init_solve(propfiles)
    solved_copy = copy.deepcopy(solved)
    f = pg.font.Font(path / settings["global"]["font"], 20)
    for catnum, catitem in enumerate(solved.data):
        items = catitem["items"]
        colr = catitem["color"]
        solved_copy[catnum]["items"] = []
        for indx, item in enumerate(items):
            printmessage(f"Loading prop {item['nm']}...")
            try:
                img = loadimage(path2props / f"{item['nm']}.png")
                images = addprop(item, img)
                newitem = solved[catnum]["items"][indx]
                newitem["images"] = images
                newitem["color"] = list(colr)
                newitem["category"] = solved[catnum]["name"]
                newitem["description"] = "Prop"
                newitem["cat"] = [catnum + 1, indx + 1]
                solved_copy[catnum]["items"].append(newitem)
            except FileNotFoundError:
                log_to_load_log(f"Failed to load prop image {item['nm']}, skip", True)
                continue
            except ValueError:
                log_to_load_log(f"Failed to load prop {item['nm']}, skip", True)
                continue
    # solved_copy["material"] = []
    # for cat in tiles:
    #     pass
    printmessage("Loading tiles as props")
    count = 0
    count2 = 0
    title = ""
    itemlist = []
    for catnum, catdata in enumerate(tiles):
        cat = catdata["name"]
        items = catdata["items"]
        if not items:
            print(cat, items)
            continue

        if "material" in items[0]["tags"]:
            continue
        for indx, tile in enumerate(items):
            if count <= 0:
                count = settings["PE"]["elements_as_tiles_count"]
                if title != "":
                    solved_copy.append({"name": title, "color": pg.Color(0, 0, 0), "items": itemlist})
                    itemlist = []
                count2 += 1
                title = f"tiles as prop {count2}"
            if tile["tp"] == "voxelStruct" and "notProp" not in tile["tags"]:
                # returnimage = pg.Surface(pg.Vector2(tile["image"].get_width(), tile["image"].get_height()) + pg.Vector2(spritesize, spritesize) * tile["bfTiles"] * 2)
                # returnimage.fill(pg.Color(255, 255, 255))
                # returnimage.blit(tile["image"], pg.Vector2(spritesize, spritesize) * tile["bfTiles"])
                # returnimage.set_colorkey(pg.Color(255, 255, 255))
                size = (pg.Vector2(tile["size"]) + pg.Vector2(tile["bfTiles"], tile["bfTiles"]) * 2) * propsize
                returnimage = pg.Surface(size)
                returnimage.fill(pg.Color(255, 255, 255))
                try:
                    img = loadimage(path2graphics / (tile["nm"] + ".png"))
                except:
                    img = pg.transform.scale(notfound, size)
                    returnimage.blit(pg.transform.scale(notfound, size), [0, 0])
                    print(f"{tile['nm']} is not Loaded properly")
                img.set_colorkey(pg.Color(255, 255, 255))
                truewidth = size.x
                if truewidth > img.get_width():
                    truewidth = img.get_width()
                for layer in range(len(tile["repeatL"]) - 1, -1, -1):
                    rect = pg.Rect(0, layer * size.y + 1, truewidth, size.y)
                    try:
                        returnimage.blit(img.subsurface(rect), [0, 0])
                    except ValueError:
                        if layer < 3:
                            errorimg = pg.transform.scale(notfound, size)
                            errorimg.set_colorkey(pg.Color(255, 255, 255))
                            returnimage.blit(errorimg, [0, 0])
                returnimage = pg.transform.scale(returnimage, pg.Vector2(returnimage.get_size()) / propsize * spritesize)
                returnimage.set_colorkey(pg.Color(255, 255, 255))
                printmessage(f"Loading tile as prop {tile['nm']}...")
                itemlist.append({
                    "nm": tile["nm"],
                    "tp": "standard",
                    "description": "Tile as prop",
                    "images": [returnimage],
                    "colorTreatment": "standard",
                    "color": settings["PE"]["elements_as_tiles_color"],
                    "sz": list(pg.Vector2(tile["size"]) + pg.Vector2(tile["bfTiles"] * 2, tile["bfTiles"] * 2)),
                    "depth": 10 + int(tile["cols"][1] != []),
                    "repeatL": tile["repeatL"],
                    "tags": ["tile"],
                    "layerExceptions": [],
                    "notes": ["Tile as prop"],
                    "category": title,
                    "cat": [catnum + 1, indx + 1]
                })
                count -= 1
    solved_copy.append({"name": title, "color": pg.Color(0, 0, 0), "items": itemlist})
    printmessage("All props loaded!")
    return solved_copy


def solveeffects(effects):
    ef = ItemData()
    for cat in effects["effects"]:
        efcat = {"name": cat["nm"], "color": cat["color"], "items": []}
        for effect in cat["efs"]:
            d = {**effects["defaultproperties"], **effect}
            if "options" not in d:
                d["options"] = []
            if "preview" in d:
                d["preview"] = loadimage(path2effectPreviews / f"{d['preview']}.png")
            for i in effects["defaultparams"]:
                d["options"].append(i)
            for indx, option in enumerate(d["options"]):
                if option[0].lower() == "layers": # idk why, but it is what it is
                    l = d["options"].pop(indx)
                    d["options"].insert(1, l)
                    break
            d["color"] = cat["color"]
            d["description"] = effect.get("description", "no description found") + "\n"
            d["description"] += "\n".join(str(i) for i in d["options"])
            d["category"] = efcat["name"]
            efcat["items"].append(d)
        ef.append(efcat)
    return ef


def turntolingo(string: RWELevel|dict, file):
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

