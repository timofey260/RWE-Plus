from files import *
import cv2
import numpy as np
from path_dict import PathDict
from pathlib import Path
from lingotojson import *
import pygame as pg

colors = settings["global"]["colors"]  # NOQA

color = pg.Color(settings["global"]["color"])
color2 = pg.Color(settings["global"]["color2"])

dc = pg.Color(0, 0, 0, 0)

cursor = dc
cursor2 = dc
mirror = dc
bftiles = dc
border = dc
canplace = dc
cannotplace = dc
select = dc
layer1 = dc
layer2 = dc
mixcol_empty = dc
mixcol_fill = dc

camera_border = dc
camera_held = dc
camera_notheld = dc

slidebar = dc
rope = dc

grid = dc

for key, value in colors.items():
    exec(f"{key} = pg.Color({value})")

red = pg.Color([255, 0, 0])
darkred = pg.Color([100, 0, 0])
blue = pg.Color([50, 0, 255])
green = pg.Color([0, 255, 0])
black = pg.Color([0, 0, 0])
white = pg.Color([255, 255, 255])
gray = pg.Color([110, 110, 110])
darkgray = pg.Color([80, 80, 80])
purple = pg.Color([255, 0, 255])
alpha = dc

col8 = [
    [-1, -1], [0, -1], [1, -1],
    [-1, 0], [1, 0],
    [-1, 1], [0, 1], [1, 1]
]

col4 = [[0, -1], [-1, 0], [1, 0], [0, 1]]

notfound = pg.image.load(path + "notfound.png")
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

color = pg.Color(settings["global"]["color"])
color2 = pg.Color(settings["global"]["color2"])

renderedimage = pg.transform.scale(tooltiles, [
            (tooltiles.get_width() / graphics["tilesize"][0]) * image1size,
            (tooltiles.get_height() / graphics["tilesize"][1]) * image1size])

material = pg.transform.scale(mat, [mat.get_width() / 16 * image1size, mat.get_height() / 16 * image1size])


def quadsize(quad):
    mostleft = bignum
    mostright = 0
    mosttop = bignum
    mostbottom = 0
    for q in quad:
        x, y = q
        if x < mostleft:
            mostleft = x
        if x > mostright:
            mostright = x

        if y < mosttop:
            mosttop = y
        if y > mostbottom:
            mostbottom = y
    ww = round(mostright - mostleft)
    wh = round(mostbottom - mosttop)
    return ww, wh, [mostleft, mosttop, mostright, mostbottom]


def quadtransform(quads, image: pg.Surface):
    ww, wh, mosts = quadsize(quads)

    colkey = image.get_colorkey()
    view = pg.surfarray.array3d(image)
    view = view.transpose([1, 0, 2])

    img = cv2.cvtColor(view, cv2.COLOR_RGB2RGBA) # NOQA
    ws, hs = img.shape[1::-1]
    pts1 = np.float32([[0, 0], [ws, 0],
                       [ws, hs], [0, hs]])
    q2 = []
    for q in quads:
        q2.append([q[0] - mosts[0], q[1] - mosts[1]])

    pts2 = np.float32(q2)
    persp = cv2.getPerspectiveTransform(pts1, pts2) # NOQA
    result = cv2.warpPerspective(img, persp, (ww, wh)) # NOQA

    img = pg.image.frombuffer(result.tostring(), result.shape[1::-1], "RGBA")
    img.set_colorkey(colkey)

    return [img, mosts[0], mosts[1], ww, wh]


class Renderer:
    def __init__(self, data, tiles, props, propcolors):
        self.tiles = tiles
        self.props = props
        self.propcolors = propcolors
        self.data = data

        size = [len(data["GE"]) * image1size, len(data["GE"][0]) * image1size]
        self.surf_geo = pg.Surface(size)
        self.surf_tiles = pg.Surface(size)
        self.surf_tiles = self.surf_tiles.convert_alpha()
        self.surf_props = pg.Surface(size)
        self.surf_props = self.surf_props.convert_alpha()
        self.surf_effect = pg.Surface(size)
        self.surf_effect.set_alpha(190)

    def set_surface(self, size):
        self.surf_geo = pg.Surface(size)
        self.surf_tiles = pg.Surface(size)
        self.surf_tiles = self.surf_tiles.convert_alpha()
        self.surf_props = pg.Surface(size)
        self.surf_props = self.surf_props.convert_alpha()
        self.surf_effect = pg.Surface(size)
        self.surf_effect.set_alpha(190)

    def tiles_full_render(self, layer):
        self.surf_tiles.fill(dc)
        area = [[0 for _ in range(len(self.data["GE"][0]))] for _ in range(len(self.data["GE"]))]
        self.tiles_render_area(area, layer)

    def tiles_render_area(self, area, layer):
        for xp, x in enumerate(area):
            for yp, y in enumerate(x):
                if y == 1:
                    continue
                self.render_tile_pixel(xp, yp, layer)

    def render_tile_pixel(self, xp, yp, layer):
        images = {}
        tiledata = self.data["TE"]["tlMatrix"]

        cell = tiledata[xp][yp][layer]
        posx = xp * image1size
        posy = yp * image1size

        datcell = cell["tp"]
        datdata = cell["data"]

        if datcell == "default":
            self.surf_tiles.fill(pg.Color(0, 0, 0, 0), [posx, posy, image1size, image1size])
            # pg.draw.rect(field.field, red, [posx, posy, size, size], 3)
            pass
        elif datcell == "material":
            if self.data["GE"][xp][yp][layer][0] != 0:
                area = pg.rect.Rect([graphics["matposes"].index(datdata) * image1size, 0, image1size, image1size])
                self.surf_tiles.fill(pg.Color(0, 0, 0, 0), [posx, posy, image1size, image1size])
                self.surf_tiles.blit(material, [posx, posy], area)
        elif datcell == "tileHead":
            it = None
            if datdata[1] in images.keys(): # if image stored in hash, returning it, else adding to hash
                it = images[datdata[1]]
            else:
                for i in self.tiles.keys():
                    for i2 in self.tiles[i]:
                        if i2["name"] == datdata[1]:
                            img = i2.copy()
                            img["image"] = pg.transform.scale(img["image"], [img["image"].get_width() / 16 * image1size,
                                                                             img["image"].get_height() / 16 * image1size])
                            images[datdata[1]] = img
                            it = img
                            break
                    if it is not None:
                        break
            if it is None:
                it = notfoundtile
            cposx = posx - int((it["size"][0] * .5) + .5) * image1size + image1size
            cposy = posy - int((it["size"][1] * .5) + .5) * image1size + image1size
            siz = pg.rect.Rect([cposx, cposy, it["size"][0] * image1size, it["size"][1] * image1size])
            if not settings["TE"]["LEtiles"]:
                pg.draw.rect(self.surf_tiles, it["color"], siz, 0)
            #for xpos in range(0, it["size"][0]):
            #    for ypos in range(0, it["size"][1]):
            #        #if it["cols"][0][xpos * it["size"][1] + ypos] == -1:
            #        self.surf_tiles.fill(dc, [(cposx + xpos) * image1size, (cposy + ypos) * image1size, image1size, image1size])
            # self.surf_tiles.fill(dc, siz)
            self.surf_tiles.blit(it["image"], [cposx, cposy])
        elif datcell == "tileBody":
            pass
        # self.surf_tiles.fill(pg.Color(0, 0, 0, 0), [posx, posy, image1size, image1size])

    def geo_full_render(self, layer):
        self.surf_geo.fill(color2)
        area = [[0 for _ in range(len(self.data["GE"][0]))] for _ in range(len(self.data["GE"]))]
        self.geo_render_area(area, layer)

    def geo_render_area(self, area, layer):
        for xp, x in enumerate(area):
            for yp, y in enumerate(x):
                if y == 1:
                    continue
                for i in col8:
                    try:
                        if area[xp + i[0]][yp + i[1]] == 0:
                            continue
                        self.surf_geo.blit(self.render_geo_pixel(xp + i[0], yp + i[1], layer), [(xp + i[0]) * image1size, (yp + i[1]) * image1size])
                    except IndexError:
                        continue
                self.surf_geo.blit(self.render_geo_pixel(xp, yp, layer), [xp * image1size, yp * image1size])

    def render_all(self, layer):
        self.geo_full_render(layer)
        self.tiles_full_render(layer)
        self.props_full_render()
        if len(self.data["FE"]["effects"]):
            self.rendermatrix(self.data["FE"]["effects"][0]["mtrx"])

    def render_geo_pixel(self, xp, yp, layer):
        def incorner(x, y):
            try:
                return self.data["GE"][x][y][i][1]
            except IndexError:
                return []
        def incornerblock(x, y):
            try:
                return self.data["GE"][x][y][i][0]
            except IndexError:
                return 0
        cellsize2 = [image1size, image1size]
        pixel = pg.Surface(cellsize2)
        pixel.fill(color2)
        for i in range(2, -1, -1):
            renderedimage.set_alpha(settings["global"]["secondarylayeralpha"])
            if i == layer:
                renderedimage.set_alpha(settings["global"]["primarylayeralpha"])
            self.data["GE"][xp][yp][i][1] = list(set(self.data["GE"][xp][yp][i][1]))
            cell = self.data["GE"][xp][yp][i][0]
            over: list = self.data["GE"][xp][yp][i][1]
            if cell == 7 and 4 not in over:
                self.data["GE"][xp][yp][i][0] = 0
                cell = self.data["GE"][xp][yp][i][0]
            curtool = [graphics["shows"][str(cell)][0] * image1size,
                       graphics["shows"][str(cell)][1] * image1size]
            pixel.blit(renderedimage, [0, 0], [curtool, cellsize2])
            if 4 in over and self.data["GE"][xp][yp][i][0] != 7:
                self.data["GE"][xp][yp][i][1].remove(4)
            if 11 in over and over.index(11) != 0:
                over.remove(11)
                over.insert(0, 11)
            for addsindx, adds in enumerate(over):
                curtool = [graphics["shows2"][str(adds)][0] * image1size,
                           graphics["shows2"][str(adds)][1] * image1size]
                bufftiles = self.data["EX2"]["extraTiles"]
                bufftiles = pg.Rect(bufftiles[0], bufftiles[1],
                                    len(self.data["GE"]) - bufftiles[0] - bufftiles[2],
                                    len(self.data["GE"][0]) - bufftiles[1] - bufftiles[3])
                if bufftiles.collidepoint(xp, yp):
                    if adds == 11:  # cracked terrain search
                        inputs = 0
                        pos = -1
                        for tile in col4:
                            curhover = incorner(xp + tile[0], yp + tile[1])
                            if 11 in curhover:
                                inputs += 1
                                if inputs == 1:
                                    match tile:
                                        case [0, 1]:  # N
                                            pos = graphics["crackv"]
                                        case [0, -1]:  # S
                                            pos = graphics["crackv"]
                                        case [-1, 0]:  # E
                                            pos = graphics["crackh"]
                                        case [1, 0]:  # W
                                            pos = graphics["crackh"]
                                elif inputs > 1:
                                    pos = -1
                        if inputs == 2:
                            pos = -1
                            if 11 in incorner(xp + 1, yp) and 11 in incorner(xp - 1, yp):
                                pos = graphics["crackh"]
                            elif 11 in incorner(xp, yp + 1) and 11 in incorner(xp, yp - 1):
                                pos = graphics["crackv"]
                        if pos != -1:
                            curtool = [pos[0] * image1size, pos[1] * image1size]
                    if adds == 4:  # shortcut entrance validation
                        # checklist
                        foundair = False
                        foundwire = False
                        tilecounter = 0
                        pathcount = 0
                        pos = -1
                        for tile in col8:
                            curtile = incornerblock(xp + tile[0], yp + tile[1])
                            curhover = incorner(xp + tile[0], yp + tile[1])
                            if curtile == 1:
                                tilecounter += 1
                            if curtile in [0, 6] and tile in col4:  # if we found air in 4 places near
                                foundair = True
                                if 5 in incorner(xp - tile[0], yp - tile[1]):  # if opposite of air is wire
                                    foundwire = True
                                    match tile:
                                        case [0, 1]:  # N
                                            pos = graphics["shortcutentrancetexture"]["N"]
                                        case [0, -1]:  # S
                                            pos = graphics["shortcutentrancetexture"]["S"]
                                        case [-1, 0]:  # E
                                            pos = graphics["shortcutentrancetexture"]["E"]
                                        case [1, 0]:  # W
                                            pos = graphics["shortcutentrancetexture"]["W"]
                                else:
                                    break
                            if 5 in curhover and tile in col4:  # if wire in 4 places near
                                pathcount += 1
                                if pathcount > 1:
                                    break
                        else:  # if no breaks
                            if tilecounter == 7 and foundwire and foundair and pos != -1:  # if we found the right one
                                curtool = [pos[0] * image1size, pos[1] * image1size]
                pixel.blit(renderedimage, [0, 0], [curtool, cellsize2])
        return pixel

    def findprop(self, name, cat=None):
        if cat is not None:
            for itemi, item in enumerate(self.props[cat]):
                if item["nm"] == name:
                    return item, [list(self.props.keys()).index(cat), itemi]
        for cati, cats in self.props.items():
            for itemi, item in enumerate(cats):
                if item["nm"] == name:
                    return item, [list(self.props.keys()).index(cati), itemi]
        item = {
            "nm": "notfound",
            "tp": "standard",
            "colorTreatment": "bevel",
            "bevel": 3,
            "sz": "point(2, 2)",
            "repeatL": [1],
            "tags": ["randomRotat"],
            "layerExceptions": [],
            "color": white,
            "images": [notfound],
            "notes": []
        }
        return item, [0, 0]

    def props_full_render(self):
        self.surf_props.fill(dc)
        for indx, prop in enumerate(self.data["PR"]["props"]):
            var = 0
            if prop[4]["settings"].get("variation") is not None:
                var = prop[4]["settings"]["variation"] - 1
            found, _ = self.findprop(prop[1])
            if found is None:
                print(f"Prop {prop[1]} not Found! image not loaded")
            image = found["images"][var] # .save(path2hash + str(id(self.data["PR"]["props"][indx][1])) + ".png")
            qd = prop[3]
            quads = []
            for q in qd:
                quads.append(toarr(q, "point"))

            # surf = pg.image.fromstring(string, [ws, hs], "RGBA")
            surf, mostleft, mosttop, ww, wh = quadtransform(quads, image)
            surf = pg.transform.scale(surf, [ww * sprite2image, wh * sprite2image])
            surf.set_colorkey(white)
            surf.set_alpha(190)
            self.surf_props.blit(surf, [mostleft / spritesize * image1size, mosttop / spritesize * image1size])
            if prop[4].get("points") is not None:
                propcolor = toarr(self.findprop(prop[1])[0]["previewColor"], "color")  # wires
                for point in prop[4]["points"]:
                    px, py = toarr(point, "point")
                    pg.draw.circle(self.surf_props, propcolor, [px, py], 5)

    def rendermatrix(self, matrix, mix=mixcol_empty):
        for xp, x in enumerate(matrix):
            for yp, cell in enumerate(x):
                #surf = pg.surface.Surface([size, size])
                col = mix.lerp(mixcol_fill, cell / 100)
                #surf.set_alpha(col.a)
                #surf.fill(col)
                #self.surf_effect.blit(surf, [xp * size, yp * size])
                self.surf_effect.fill(col, [xp * image1size, yp * image1size, image1size, image1size])
                # pg.draw.rect(f, col, [xp * size, yp * size, size, size], 0)