from files import *
import cv2
import numpy as np
from path_dict import PathDict
from pathlib import Path
from lingotojson import *
import pygame as pg

col8 = [
    [-1, -1], [0, -1], [1, -1],
    [-1, 0],           [1, 0],
    [-1, 1],  [0, 1],  [1, 1]
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

    def set_surface(self, size):
        self.surf_geo = pg.Surface(size)
        self.surf_tiles = pg.Surface(size)
        self.surf_props = pg.Surface(size)

    def tiles_full_render(self, layer):
        self.surf_tiles.fill(pg.Color(0, 0, 0, 0))
        area = [[0 for _ in range(len(self.data["GE"][0]))] for _ in range(len(self.data["GE"]))]
        self.tiles_render_area(area, layer)

    def tiles_render_area(self, area, layer):
        for xp, x in enumerate(area):
            for yp, y in enumerate(x):
                if y == 1:
                    continue
                self.render_tile_pixel(xp, yp, layer)

    def render_tile_pixel(self, xp, yp, layer):
        material = pg.transform.scale(mat, [mat.get_width() / 16 * image1size, mat.get_height() / 16 * image1size])
        images = {}
        tiledata = self.data["TE"]["tlMatrix"]

        cell = tiledata[xp][yp][layer]
        posx = xp * image1size
        posy = yp * image1size

        datcell = cell["tp"]
        datdata = cell["data"]

        if datcell == "default":
            # pg.draw.rect(field.field, red, [posx, posy, size, size], 3)
            pass
        elif datcell == "material":
            if self.data["GE"][xp][yp][layer][0] != 0:
                area = pg.rect.Rect([graphics["matposes"].index(datdata) * image1size, 0, image1size, image1size])
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
            self.surf_tiles.fill(pg.Color(0, 0, 0, 0), siz)
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