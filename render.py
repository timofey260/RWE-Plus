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
mosttextcolor = dc

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
yellow = pg.Color([255, 255, 0])
alpha = dc

col8 = [
    [-1, -1], [0, -1], [1, -1],
    [-1, 0], [1, 0],
    [-1, 1], [0, 1], [1, 1]
]

col4 = [[0, -1], [-1, 0], [1, 0], [0, 1]]

renderedimage = pg.transform.scale(tooltiles, [
    (tooltiles.get_width() / globalsettings["tilesize"][0]) * image1size,
    (tooltiles.get_height() / globalsettings["tilesize"][1]) * image1size])

colorint = 170
renderedimage2 = renderedimage.copy()
renderedimage2.fill(pg.Color(100, colorint, 100), special_flags=pg.BLEND_MAX)
renderedimage3 = renderedimage.copy()
renderedimage3.fill(pg.Color(colorint, 100, 100), special_flags=pg.BLEND_MAX)

renderedimagecolored = [renderedimage, renderedimage2, renderedimage3]


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
    """
    FAILURE AFTER FAILURE AFTER FAILURE
    AFTER FAILURE AFTER FAILURE AFTER
    FAILURE AFTER FAILURE AFTER FAILURE
    AFTER FAILURE AFTER FAILURE

    THE RESULTS REFUSE TO ALTER

    AGAIN AND AGAIN AND AGAIN AND AGAIN AND
    AGAIN AND AGAIN AND AGAIN AND AGAIN AND
    AGAIN AND AGAIN AND AGAIN AND AGAIN AND
    AGAIN AND AGAIN AND AGAIN AND AGAIN

    MY FAITH BEGINS TO FALTER
    """
    def __init__(self, process, render=True):
        self.tiles: ItemData = process.manager.tiles
        self.props: ItemData = process.manager.props
        self.propcolors = process.manager.propcolors
        self.data: RWELevel = process.file
        self.effect_index = 0

        self.lastlayer = 0
        self.offset = pg.Vector2(0, 0)
        self.size = image1size

        self.geolayers = [True, True, True]
        self.tilelayers = [True, True, True]
        self.proplayer = False # thanks to elsafogen
        self.ropepropvis = False
        self.coloredgeo = False
        if render:
            size = [self.levelwidth * image1size, self.levelheight * image1size]
            # self.f = pg.Surface(size)
            self.surfs_geo = [
                pg.Surface(size),
                pg.Surface(size),
                pg.Surface(size)
            ]
            self.surfs_tile = [
                pg.Surface(size, pg.SRCALPHA),
                pg.Surface(size, pg.SRCALPHA),
                pg.Surface(size, pg.SRCALPHA)
            ]
            self.surf_props = pg.Surface(size, pg.SRCALPHA)
            self.surf_effect = pg.Surface(size)
            self.surf_effect.set_alpha(190)

    @property
    def surf_geo(self):
        return self.surfs_geo[self.lastlayer]

    @property
    def surf_tiles(self):
        return self.surfs_tile[self.lastlayer]

    def returntiles(self, layer):
        if self.coloredgeo:
            # renderedimagecolored[layer].set_alpha(200)
            return renderedimagecolored[layer]
        else:
            return renderedimage

    def set_surface(self, size=None):
        if size is None:  # auto
            size = [self.levelwidth * image1size, self.levelheight * image1size]
        self.surfs_geo = [
            pg.Surface(size),
            pg.Surface(size),
            pg.Surface(size)
        ]
        self.surfs_tile = [
            pg.Surface(size, pg.SRCALPHA),
            pg.Surface(size, pg.SRCALPHA),
            pg.Surface(size, pg.SRCALPHA)
        ]
        self.surf_props = pg.Surface(size, pg.SRCALPHA)
        self.surf_effect = pg.Surface(size)
        self.surf_effect.set_alpha(190)

    def tiles_full_render(self, layer):
        for l in range(3):
            self.surfs_tile[l].fill(dc)
        area = [[False for _ in range(self.levelheight)] for _ in range(self.levelwidth)]
        self.tiles_render_area(area, layer)

    def tiles_render_area(self, area, layer):
        self.lastlayer = layer
        for xp, x in enumerate(area):
            for yp, y in enumerate(x):
                if y:
                    continue
                for l in range(3):  # help
                    if self.data["TE"]["tlMatrix"][xp][yp][l]["tp"] == "tileBody":
                        p = toarr(self.data["TE"]["tlMatrix"][xp][yp][l]["data"][0], "point")
                        if p[0] > self.levelwidth or p[1] > self.levelheight:
                            self.data["TE"]["tlMatrix"][xp][yp][l]["data"][0] = makearr([0, 0], "point")
                            continue
                        area[p[0] - 1][p[1] - 1] = False
                    self.surfs_tile[l].fill(pg.Color(0, 0, 0, 0), [xp * image1size, yp * image1size, image1size, image1size])
        for xp, x in enumerate(area):
            for yp, y in enumerate(x):
                if y:
                    continue
                self.render_tile_pixel3(xp, yp)
                # self.render_tile_pixel(xp, yp, layer)

    def render_tile_pixel3(self, xp, yp):
        for l in range(3):
            self.render_tile_pixel(xp, yp, l)

    def render_tile_pixel(self, xp, yp, l):
        tiledata = self.data["TE"]["tlMatrix"]

        def findtileimage(name):
            it = None
            for i in self.tiles:
                for i2 in i["items"]:
                    if i2["nm"] == name:
                        img = i2.copy()
                        img["image"] = pg.transform.scale(img["image"], [img["image"].get_width() / 16 * image1size,
                                                                         img["image"].get_height() / 16 * image1size])
                        it = img
                        break
                if it is not None:
                    break
            if it is None:
                it = notfoundtile
            return it

        for layer in range(2, -1, -1):
            cell = tiledata[xp][yp][layer]
            posx = xp * image1size
            posy = yp * image1size

            datcell = cell["tp"]
            datdata = cell["data"]
            if layer == 1 and self.data["GE"][xp][yp][0][0] != 0 and layer != l:
                continue
            elif layer == 2 and (self.data["GE"][xp][yp][0][0] != 0 or
                                 self.data["GE"][xp][yp][1][0] != 0) and layer != l:
                continue
            if layer < l:
                continue

            if not self.tilelayers[layer]:
                continue
            if datcell == "default":
                # self.surf_tiles.fill(pg.Color(0, 0, 0, 0), [posx, posy, image1size, image1size])
                # pg.draw.rect(field.field, red, [posx, posy, size, size], 3)
                pass
            elif datcell == "material":
                if self.data["GE"][xp][yp][layer][0] != 0:
                    try:
                        it = findtileimage(datdata)
                        #ms = graphics["matsize"]
                        #rect = pg.Rect(ms[0] + posx, ms[0] + posy, ms[1], ms[1])
                        #pg.draw.rect(self.surf_tiles, graphics["matposes"][datdata], rect)
                        if layer != l:
                            it["image"].set_alpha(settings["global"]["tiles_secondarylayeralpha"])
                        else:
                            it["image"].set_alpha(settings["global"]["tiles_primarylayeralpha"])
                        self.surfs_tile[l].blit(it["image"], [posx, posy])
                        it["image"].set_alpha(255)
                    except ValueError:
                        self.surfs_tile[l].blit(notfound, [posx, posy])

            elif datcell == "tileHead":
                it = findtileimage(datdata[1])
                cposx = posx - int((it["size"][0] * .5) + .5) * image1size + image1size
                cposy = posy - int((it["size"][1] * .5) + .5) * image1size + image1size
                siz = pg.rect.Rect([cposx, cposy, it["size"][0] * image1size, it["size"][1] * image1size])
                if not settings["TE"]["LEtiles"]:
                    pg.draw.rect(self.surfs_tile[l], it["color"], siz, 0)
                if layer != l:
                    it["image"].set_alpha(settings["global"]["tiles_secondarylayeralpha"])
                else:
                    it["image"].set_alpha(settings["global"]["tiles_primarylayeralpha"])
                # self.blit_tiles_to_surfs(it["image"], [cposx, cposy])
                self.surfs_tile[l].blit(it["image"], [cposx, cposy])
                it["image"].set_alpha(255)
            elif datcell == "tileBody":
                pass
        # self.surf_tiles.fill(pg.Color(0, 0, 0, 0), [posx, posy, image1size, image1size])

    def geo_full_render(self, layer):
        area = [[False for _ in range(self.levelheight)] for _ in range(self.levelwidth)]
        for i in range(3):
            self.surfs_geo[i].fill(color2)
        self.geo_render_area(area, layer)

    def geo_render_area(self, area, layer):
        for xp, x in enumerate(area):
            for yp, y in enumerate(x):
                if y:
                    continue
                for i in col8:
                    try:
                        if not area[xp + i[0]][yp + i[1]]:
                            continue
                        self.render_geo_pixel3(xp + i[0], yp + i[1])
                        # self.surf_geo.blit(self.render_geo_pixel(xp + i[0], yp + i[1], layer), [(xp + i[0]) * image1size, (yp + i[1]) * image1size])
                    except IndexError:
                        continue
                self.render_geo_pixel3(xp, yp)
                # self.surf_geo.blit(self.render_geo_pixel(xp, yp, layer), [xp * image1size, yp * image1size])

    def render_all(self, layer):
        self.lastlayer = layer
        self.geo_full_render(layer)
        self.tiles_full_render(layer)
        self.props_full_render(layer)
        if len(self.data["FE"]["effects"]):
            self.rendereffect(0)

    def render_geo_pixel3(self, xp, yp):
        for l in range(3):
            self.surfs_geo[l].blit(self.render_geo_pixel(xp, yp, l), [xp * image1size, yp * image1size])

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
            if not self.coloredgeo and not globalsettings["viewportrenderalllayers"] and i < layer:
                continue
            if not self.geolayers[i]:
                continue
            if self.coloredgeo:
                self.returntiles(i).set_alpha(170)
                if i == layer:
                    self.returntiles(i).set_alpha(255)
            else:
                self.returntiles(i).set_alpha(settings["global"]["secondarylayeralpha"])
                if i == layer:
                    self.returntiles(i).set_alpha(settings["global"]["primarylayeralpha"])
                self.data["GE"][xp][yp][i][1] = list(set(self.data["GE"][xp][yp][i][1]))
            cell = self.data["GE"][xp][yp][i][0]
            over: list = self.data["GE"][xp][yp][i][1]
            if cell == 7 and 4 not in over:
                self.data["GE"][xp][yp][i][0] = 0
                cell = self.data["GE"][xp][yp][i][0]
            curtool = [globalsettings["shows"][str(cell)][0] * image1size,
                       globalsettings["shows"][str(cell)][1] * image1size]
            pixel.blit(self.returntiles(i), [0, 0], [curtool, cellsize2])
            if 4 in over and self.data["GE"][xp][yp][i][0] != 7:
                self.data["GE"][xp][yp][i][1].remove(4)
            if 11 in over and over.index(11) != 0:
                over.remove(11)
                over.insert(0, 11)
            if cell in [2, 3, 4, 5]:
                numwall = []
                for tile in col4:
                    t = incornerblock(xp + tile[0], yp + tile[1])
                    numwall.append(t if t == 1 else 0)
                #print(numwall, cell)
                if (numwall == [0, 1, 0, 1] and cell == 2) or \
                    (numwall == [0, 0, 1, 1] and cell == 3) or \
                    (numwall == [1, 1, 0, 0] and cell == 4) or \
                    (numwall == [1, 0, 1, 0] and cell == 5):
                    pass
                else:
                    pg.draw.line(pixel, red, [0, 0], [image1size, image1size], 1)
                    pg.draw.line(pixel, red, [image1size, 0], [0, image1size], 1)
            for addsindx, adds in enumerate(over):
                try:
                    curtool = [globalsettings["shows2"][str(adds)][0] * image1size,
                               globalsettings["shows2"][str(adds)][1] * image1size]
                except KeyError:
                    adds = 0
                    curtool = [globalsettings["shows2"][str(adds)][0] * image1size,
                               globalsettings["shows2"][str(adds)][1] * image1size]
                bufftiles = self.data["EX2"]["extraTiles"]
                bufftiles = pg.Rect(bufftiles[0], bufftiles[1],
                                    self.levelwidth - bufftiles[0] - bufftiles[2],
                                    self.levelheight - bufftiles[1] - bufftiles[3])
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
                                            pos = globalsettings["crackv"]
                                        case [0, -1]:  # S
                                            pos = globalsettings["crackv"]
                                        case [-1, 0]:  # E
                                            pos = globalsettings["crackh"]
                                        case [1, 0]:  # W
                                            pos = globalsettings["crackh"]
                                elif inputs > 1:
                                    pos = -1
                        if inputs == 2:
                            pos = -1
                            if 11 in incorner(xp + 1, yp) and 11 in incorner(xp - 1, yp):
                                pos = globalsettings["crackh"]
                            elif 11 in incorner(xp, yp + 1) and 11 in incorner(xp, yp - 1):
                                pos = globalsettings["crackv"]
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
                                if any(item in [5, 6, 7, 19, 21] for item in incorner(xp - tile[0], yp - tile[1])):  # if opposite of air is wire
                                    foundwire = True
                                    match tile:
                                        case [0, 1]:  # N
                                            pos = globalsettings["shortcutentrancetexture"]["N"]
                                        case [0, -1]:  # S
                                            pos = globalsettings["shortcutentrancetexture"]["S"]
                                        case [-1, 0]:  # E
                                            pos = globalsettings["shortcutentrancetexture"]["E"]
                                        case [1, 0]:  # W
                                            pos = globalsettings["shortcutentrancetexture"]["W"]
                                else:
                                    break
                            if 5 in curhover and tile in col4:  # if wire in 4 places near
                                pathcount += 1
                                if pathcount > 1:
                                    break
                        else:  # if no breaks
                            if tilecounter == 7 and foundwire and foundair and pos != -1:  # if we found the right one
                                curtool = [pos[0] * image1size, pos[1] * image1size]
                pixel.blit(self.returntiles(i), [0, 0], [curtool, cellsize2])
        return pixel

    def findprop(self, name, cat=None):
        if cat is not None:
            found = self.props[cat, name]
            if found is not None:
                return found, [found["cat"][0] - 1, found["cat"][1] - 1]
        found = self.props[name]
        if found is not None:
            return found, [found["cat"][0] - 1, found["cat"][1] - 1]
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
            "notes": [],
            "previewColor": "color(255, 255, 255)"
        }
        return item, [0, 0]

    def props_full_render(self, layer):
        self.lastlayer = layer
        self.surf_props.fill(dc)
        for indx, prop in enumerate(self.data["PR"]["props"]):
            if self.proplayer and not (layer * 10 <= -prop[0] <= layer * 10 + 10):
                continue
            var = 0
            if prop[4]["settings"].get("variation") is not None:
                var = prop[4]["settings"]["variation"] - 1
            found, _ = self.findprop(prop[1])
            if found is None:
                print(f"Prop {prop[1]} not Found! image not loaded")
            try:
                image = found["images"][var] # .save(path2hash + str(id(self.data["PR"]["props"][indx][1])) + ".png")
            except IndexError:
                image = found["images"][0]
                if prop[4]["settings"].get("variation") is not None:
                    self.data["PR"]["props"][indx][4]["settings"]["variation"] = 1
            qd = prop[3]
            quads = []
            for q in qd:
                quads.append(toarr(q, "point"))

            # surf = pg.image.fromstring(string, [ws, hs], "RGBA")
            if not self.ropepropvis or prop[4].get("points") is None:
                surf, mostleft, mosttop, ww, wh = quadtransform(quads, image)
                surf = pg.transform.scale(surf, [ww * sprite2image, wh * sprite2image])
                surf.set_colorkey(white)
                alph = map2(abs(layer - -prop[0] / 10), 3, 0, 40, 190)
                surf.set_alpha(alph)
                self.surf_props.blit(surf, [mostleft * sprite2image, mosttop * sprite2image])
            if prop[4].get("points") is not None:
                propcolor = toarr(self.findprop(prop[1])[0]["previewColor"], "color")  # wires
                lastpos = None
                for point in prop[4]["points"]:
                    px, py = toarr(point, "point")
                    px = px / propsize * image1size
                    py = py / propsize * image1size
                    pg.draw.circle(self.surf_props, propcolor, [px, py], image1size / 3)
                    if lastpos is not None:
                        pg.draw.line(self.surf_props, white, [px, py], lastpos)
                    lastpos = [px, py]

    def rerendereffect(self):
        self.rendereffect(self.effect_index)

    def rendereffect(self, indx, mix=mixcol_empty):
        self.effect_index = indx
        for xp, x in enumerate(self.data["FE"]["effects"][indx]["mtrx"]):
            for yp, cell in enumerate(x):
                #surf = pg.surface.Surface([size, size])
                col = mix.lerp(mixcol_fill, cell / 100)
                #surf.set_alpha(col.a)
                #surf.fill(col)
                #self.surf_effect.blit(surf, [xp * size, yp * size])
                self.surf_effect.fill(col, [xp * image1size, yp * image1size, image1size, image1size])
                # pg.draw.rect(f, col, [xp * size, yp * size, size, size], 0)

    @property
    def hiddenlayer(self):
        return self.geolayers[self.lastlayer]

    @property
    def levelwidth(self):
        return len(self.data["GE"])

    @property
    def levelheight(self):
        return len(self.data["GE"][0])