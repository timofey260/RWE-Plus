import copy

import render
import widgets
from lingotojson import *
from files import *
import cv2
import numpy as np
from path_dict import PathDict
from pathlib import Path
import pyperclip
from render import Renderer

inputfile = ''
filepath = path2levels

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

colors = settings["global"]["colors"] # NOQA

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
    [-1, 0],           [1, 0],
    [-1, 1],  [0, 1],  [1, 1]
]

col4 = [[0, -1], [-1, 0], [1, 0], [0, 1]]

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

def rotatepoint(point, angle):
    px, py = point
    angle = math.radians(angle)
    qx = math.cos(angle) * px - math.sin(angle) * py
    qy = math.sin(angle) * px + math.cos(angle) * py
    return pg.Vector2([qx, qy])


def setasname(name):
    global inputfile
    inputfile = name


class menu:
    def __init__(self, surface: pg.surface.Surface, data, name):
        self.surface = surface
        self.menu = name
        self.data = data
        self.datalast = copy.deepcopy(data)
        self.settings = settings[self.menu]
        self.hotkeys = hotkeys[name]
        self.historybuffer = []
        self.uc = []

        self.mousp = False
        self.mousp1 = True
        self.mousp2 = True

        self.size = image1size
        self.message = ''
        print("Entered " + self.menu)
        widgets.resetpresses()
        widgets.enablebuttons = False
        self.init()

    def unlock_keys(self):
        self.uc = []
        for i in self.hotkeys["unlock_keys"]:
            self.uc.append(getattr(pg, i))

    def watch_keys(self):
        self.message = "%"

    def recaption(self):
        pg.display.set_caption(f"{self.data['path']} | RWE+: {self.menu} | by Timofey")

    def init(self):
        self.recaption()
        self.message = ""
        self.buttons: list[widgets.button, ...] = []
        for i in self.settings["buttons"]:
            try:
                f = getattr(self, i[3])
            except AttributeError:
                f = self.non
            try:
                f2 = getattr(self, i[4])
            except AttributeError:
                f2 = self.non
            if len(i) == 6:
                self.buttons.append(
                    widgets.button(self.surface, pg.rect.Rect(i[1]), i[2], i[0], onpress=f,
                                   onrelease=f2, tooltip=self.returnkeytext(i[5])))
            elif len(i) == 7:
                self.buttons.append(
                    widgets.button(self.surface, pg.rect.Rect(i[1]), i[2], i[0], onpress=f,
                                   onrelease=f2, tooltip=self.returnkeytext(i[5]), icon=i[6]))
        self.labels: list[widgets.lable, ...] = []
        for i in self.settings["labels"]:
            if len(i) == 3:
                self.labels.append(widgets.lable(self.surface, i[0], i[1], i[2]))
            elif len(i) == 4:
                self.labels.append(widgets.lable(self.surface, i[0], i[1], i[2], i[3]))
        self.unlock_keys()
        self.resize()

    def savef(self, saveas=False):
        if self.data["path"] != "" and not saveas:
            open(os.path.splitext(self.data["path"])[0] + ".wep", "w").write(json.dumps(self.data))
            self.data["path"] = os.path.splitext(self.data["path"])[0] + ".wep"
            print(os.path.splitext(self.data["path"])[0] + ".wep")
        else:
            savedest = self.asksaveasfilename()
            if savedest != "":
                open(savedest, "w").write(json.dumps(self.data))
                self.data["level"] = os.path.basename(savedest)
                self.data["path"] = savedest
                self.data["dir"] = os.path.abspath(savedest)
        print("Level saved!")
        self.recaption()

    def addfolder(self, folder):
        global filepath
        filepath += "\\" + folder + "\\"
        self.message = "ab"

    def goback(self):
        global filepath
        p = Path(filepath)
        filepath = str(p.parent.absolute())
        self.message = "ab"

    def asksaveasfilename(self, defaultextension=[".wep"]):
        global inputfile, filepath
        filepath = path2levels
        buttons = []
        slider = 0
        label = widgets.lable(self.surface, "Use scroll to navigate\nEnter to continue\nType to search\nEscape to exit", [50, 0], black, 30)
        label.resize()
        def appendbuttons():
            global filepath
            f = os.listdir(filepath)
            f.reverse()
            buttons.clear()
            buttons.append(widgets.button(self.surface, pg.Rect([0, 20, 50, 5]), color2, "..", onpress=self.goback, tooltip="Go back"))
            count = 1
            for file in f:
                if inputfile.lower() in file.lower():
                    y = 5 * count - slider * 5
                    if os.path.isfile(os.path.join(filepath, file)) and os.path.splitext(file)[1] in defaultextension:
                        if y > 0:
                            buttons.append(widgets.button(self.surface, pg.Rect([0, 20 + y, 50, 5]), color2, file, onpress=setasname, tooltip="File"))
                        count += 1
                    elif os.path.isdir(os.path.join(filepath, file)):
                        if y > 0:
                            buttons.append(widgets.button(self.surface, pg.Rect([0, 20 + y, 50, 5]), color2, file, onpress=self.addfolder, tooltip="Folder"))
                        count += 1
            for button in buttons:
                button.resize()
        inputfile = ''
        r = True
        appendbuttons()
        while r:
            self.surface.fill(color)
            for button in buttons:
                button.blitshadow()
            for button in buttons:
                button.blit()
            for button in buttons:
                button.blittooltip()
            label.blit()
            widgets.fastmts(self.surface, "file name:", 0, 0, fontsize=50)

            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.unicode in allleters:
                        inputfile += event.unicode
                    elif event.key == pg.K_BACKSPACE:
                        inputfile = inputfile[:-1]
                    elif event.key == pg.K_RETURN:
                        r = False
                    elif event.key == pg.K_ESCAPE:
                        return None
                    appendbuttons()
                    slider = 0
                if event.type == pg.QUIT:
                    return None
                if event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 4:
                        slider = max(slider - 1, 0)
                        appendbuttons()
                    elif event.button == 5:
                        slider += 1
                        appendbuttons()
                if event.type == pg.WINDOWRESIZED:
                    self.resize()
                    label.resize()
            if self.message == "ab":
                slider = 0
                self.message = ''
                appendbuttons()
            widgets.fastmts(self.surface, inputfile, 0, 50, fontsize=50)
            pg.display.flip()
            pg.display.update()
        # i = input(q + "(leave blank for cancel): ")
        if inputfile == "":
            return None
        try:
            print(os.path.splitext(inputfile))
            if len(defaultextension) == 1 and os.path.splitext(inputfile)[1] != defaultextension[0]:
                return f"{filepath}{inputfile}{defaultextension[0]}"
            else:
                return f"{filepath}{inputfile}"
        except ValueError:
            print("it's not a string")
            return None

    def askint(self, q):
        self.savef()
        i = ''
        nums = "0123456789-"
        r = True
        while r:
            self.surface.fill(color)
            widgets.fastmts(self.surface, q + "(level was saved):", 0, 0, fontsize=50)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return None
                if event.type == pg.KEYDOWN:
                    if event.unicode in nums:
                        i += event.unicode
                    elif event.key == pg.K_BACKSPACE:
                        i = i[:-1]
                    elif event.key == pg.K_RETURN:
                        r = False
                    elif event.key == pg.K_ESCAPE:
                        return None
            widgets.fastmts(self.surface, i, 0, 50, fontsize=50)
            pg.display.flip()
            pg.display.update()
        # i = input(q + "(leave blank for cancel): ")
        if i == "":
            return None
        try:
            return int(i)
        except ValueError:
            print("it's not a number")
            return None

    def savef_txt(self):
        savedest = self.asksaveasfilename(defaultextension=[".txt"])
        if savedest != "":
            turntolingo(self.data, open(savedest, "w"))

    def blit(self, fontsize=None):
        if settings["global"]["doublerect"]:
            for i in self.buttons:
                i.blitshadow()
        for i in self.labels:
            i.blit()
        for i in self.buttons:
            i.blit(fontsize)
        for i in self.buttons:
            i.blittooltip()
        if not pg.mouse.get_pressed(3)[0] and not widgets.enablebuttons:
            widgets.enablebuttons = True

    def updatehistory(self, paths):
        if self.data != self.datalast:
            h = [[]]
            for historypath in paths:
                ch = PathDict(self.data)[*historypath]
                lastch = PathDict(self.datalast)[*historypath]
                if ch != lastch:
                    h.append([historypath, [ch, lastch]])
            if len(h) > 0:
                self.historybuffer.append(copy.deepcopy(h))
            self.datalast = copy.deepcopy(self.data)

    def detecthistory(self, path, savedata=True):
        if self.data != self.datalast:
            pth = PathDict(self.data)[*path]
            pthlast = PathDict(self.datalast)[*path]
            history = [path]
            for xindx, x in enumerate(pth):
                if x != pthlast[xindx]:
                    history.append([[xindx], [x, pthlast[xindx]]])
            if len(history) > 0:
                self.historybuffer.append(copy.deepcopy(history))
            if savedata:
                self.datalast = copy.deepcopy(self.data)



    def non(self):
        pass

    def resize(self):
        for i in self.buttons:
            i.resize()
        for i in self.labels:
            i.resize()

    def sendsignal(self, message):
        self.message = message

    def reload(self):
        global settings
        settings = json.load(open(path2ui +  graphics["uifile"], "r"))
        self.__init__(self.surface, self.data, self.menu)

    def send(self, message):
        if message[0] == "-":
            self.mpos = 1
            getattr(self, message[1:])()

    def findparampressed(self, paramname: str):
        for key, value in self.hotkeys.items():
            if key == "unlock_keys":
                continue
            if value.lower() == paramname.lower():
                if pg.key.get_pressed()[getattr(pg, key.replace("@", "").replace("+", ""))]:
                    return True
                return False
        # if param not found
        return False

    def findkey(self, paramname, manyparams=False, globalkeys=False):
        p = []
        if not globalkeys:
            for key, value in self.hotkeys.items():
                if key == "unlock_keys":
                    continue
                if value.lower() == paramname.lower():
                    k = key.replace("@", "")
                    if not manyparams:
                        return k
                    p.append(k)
            for key, value in hotkeys["global"].items():
                if value.lower() == paramname.lower():
                    k = key.replace("@", "")
                    if not manyparams:
                        return k
                    p.append(k)
            if not manyparams:
                return None
        else:
            for cat, keyval in hotkeys.items():
                for key, value in keyval.items():
                    if key == "unlock_keys":
                        continue
                    if value.lower() == paramname.lower():
                        k = key.replace("@", "")
                        if not manyparams:
                            return k
                        p.append(k)
        return p

    def returnkeytext(self, text):
        pat = r"(<\[([a-z0-9\-\_\/]+)\]>)"
        found = re.findall(pat, text, flags=re.IGNORECASE)
        if found is None:
            return text
        groups = []
        string = text
        for index, fgroup in enumerate(found):
            groups.append(list(set(self.findkey(fgroup[1], manyparams=True, globalkeys=True))))
            groups[-1].sort()
            for i, key in enumerate(groups[-1]):
                k = key.replace("+", "").replace("@", "")
                if key.find("+") != -1:
                    groups[-1][i] = "ctrl + " + pg.key.name(getattr(pg, k))
                else:
                    groups[-1][i] = pg.key.name(getattr(pg, k))
            rep = str(groups[-1]).replace("[", "").replace("]", "").replace("'", "").replace(" ", "").replace("+", " + ")
            rep = " or ".join(rep.rsplit(",", 1))
            rep = rep.replace(",", ", ")
            string = string.replace(fgroup[0], rep)
        # string = re.sub(pat, rep, text, flags=re.IGNORECASE)
        return string


class MenuWithField(menu):
    def __init__(self, surface: pg.Surface, name, renderer: render.Renderer):
        super(MenuWithField, self).__init__(surface, renderer.data, name)

        self.renderer = renderer
        self.items = renderer.tiles
        self.props = renderer.props
        self.propcolors = renderer.propcolors

        self.menu = name

        self.drawgeo = True
        self.drawcameras = False
        self.drawtiles = False
        self.drawprops = False
        self.draweffects = False
        self.drawgrid = False
        self.selectedeffect = 0

        self.f = pg.Surface([len(self.data["GE"]) * image1size, len(self.data["GE"][0]) * image1size])

        self.field = widgets.window(self.surface, self.settings["d1"])
        self.btiles = renderer.data["EX2"]["extraTiles"]
        self.fieldmap = self.field.field

        self.fieldadd = self.fieldmap
        self.fieldadd.fill(white)
        self.fieldadd.set_colorkey(white)

        self.xoffset = 0
        self.yoffset = 0
        self.size = image1size
        self.rectdata = [[0, 0], [0, 0], [0, 0]]
        self.layer = 0

    def reload(self):
        global settings
        settings = json.load(open(path2ui +  graphics["uifile"], "r"))
        self.__init__(self.surface, self.menu, self.renderer)

    def movemiddle(self, bp, pos):
        if bp[1] == 1 and self.mousp1 and (self.mousp2 and self.mousp):
            self.rectdata[0] = pos.copy()
            self.rectdata[1] = [self.xoffset, self.yoffset]
            self.mousp1 = False
        elif bp[1] == 1 and not self.mousp1 and (self.mousp2 and self.mousp):
            self.xoffset = self.rectdata[1][0] - (self.rectdata[0][0] - pos[0])
            self.yoffset = self.rectdata[1][1] - (self.rectdata[0][1] - pos[1])
        elif bp[1] == 0 and not self.mousp1 and (self.mousp2 and self.mousp):
            self.field.field.fill(self.field.color)
            self.mousp1 = True
            self.renderfield()

    def drawborder(self):
        rect = [self.xoffset * self.size, self.yoffset * self.size, len(self.data["GE"]) * self.size,
                len(self.data["GE"][0]) * self.size]
        pg.draw.rect(self.field.field, border, rect, 5)
        fig = [(self.btiles[0] + self.xoffset) * self.size, (self.btiles[1] + self.yoffset) * self.size,
               (len(self.data["GE"]) - self.btiles[2] - self.btiles[0]) * self.size,
               (len(self.data["GE"][0]) - self.btiles[3] - self.btiles[1]) * self.size]
        rect = pg.rect.Rect(fig)
        pg.draw.rect(self.field.field, bftiles, rect, 5)
        self.field.blit()

    def drawmap(self):
        self.field.field.fill(self.field.color)
        self.field.field.blit(self.fieldmap, [self.xoffset * self.size, self.yoffset * self.size])
        self.field.field.blit(self.fieldadd, [self.xoffset * self.size, self.yoffset * self.size])
        self.drawborder()

    def renderfield(self):
        self.fieldmap = pg.surface.Surface([len(self.data["GE"]) * self.size, len(self.data["GE"][0]) * self.size])
        self.fieldmap.blit(pg.transform.scale(self.f, [self.f.get_width() / image1size * self.size, self.f.get_height() / image1size * self.size]), [0, 0])

    def rfa(self):
        self.f = pg.Surface([len(self.data["GE"]) * image1size, len(self.data["GE"][0]) * image1size])
        if self.drawgeo:
            self.renderer.geo_full_render(self.layer)
            self.f.blit(self.renderer.surf_geo, [0, 0])
        if self.drawtiles:
            self.renderer.tiles_full_render(self.layer)
            self.f.blit(self.renderer.surf_tiles, [0, 0])
        if self.drawprops:
            self.renderprops()
        if self.drawgrid:
            self.rendergrid()
        if self.draweffects != 0 and self.draweffects <= len(self.data['FE']['effects']):
            self.rendermatrix(self.f, image1size, self.data["FE"]["effects"][self.draweffects - 1]["mtrx"])
        self.renderfield()

    def resize(self):
        super().resize()
        if hasattr(self, "field"):
            self.field.resize()
            self.renderfield()

    def blit(self, draw=True):
        if draw:
            self.drawmap()
        if self.drawcameras:
            self.rendercameras()
        if self.draweffects != 0 and self.draweffects <= len(self.data['FE']['effects']):
            widgets.fastmts(self.surface, f"Effect({self.draweffects}): {self.data['FE']['effects'][self.draweffects - 1]['nm']}", *self.field.rect.topleft, white)
        mpos = pg.mouse.get_pos()
        if self.drawgrid and self.field.rect.collidepoint(mpos):
            pos = [math.floor((mpos[0] - self.field.rect.x) / self.size) + 0.5,
                   math.floor((mpos[1] - self.field.rect.y) / self.size) + 0.5]
            pos2 = [pos[0] * self.size + self.field.rect.x, pos[1] * self.size + self.field.rect.y]
            pg.draw.line(self.surface, cursor2, [self.field.rect.left, pos2[1]],
                         [self.field.rect.right, pos2[1]])
            pg.draw.line(self.surface, cursor2, [pos2[0], self.field.rect.top],
                         [pos2[0], self.field.rect.bottom])

        super().blit()

    def swichcameras(self):
        self.drawcameras = not self.drawcameras

    def swichlayers(self):
        self.layer = (self.layer + 1) % 3
        self.mpos = 1
        self.rfa()

    def swichlayers_back(self):
        self.layer -= 1
        if self.layer < 0:
            self.layer = 2
        self.mpos = 1
        self.rfa()

    def send(self, message):
        super().send(message)
        match message:
            case "SU":
                self.size += 1
                self.renderfield()
            case "SD":
                if self.size - 1 != 0:
                    self.size -= 1
                    self.renderfield()
            case "left":
                self.xoffset += 1
            case "right":
                self.xoffset -= 1
            case "up":
                self.yoffset += 1
            case "down":
                self.yoffset -= 1

    def togglegeo(self):
        self.drawgeo = not self.drawgeo
        self.rfa()

    def toggletiles(self):
        self.drawtiles = not self.drawtiles
        self.rfa()

    def toggleeffects(self):
        self.draweffects += 1
        if self.draweffects > len(self.data["FE"]["effects"]):
            self.draweffects = 0
        self.rfa()

    def toggleprops(self):
        self.drawprops = not self.drawprops
        self.rfa()

    def togglegrid(self):
        self.drawgrid = not self.drawgrid
        self.rfa()

    def rendercameras(self):
        if hasattr(self, "closestcameraindex"):
            closest = self.closestcameraindex()
        for indx, cam in enumerate(self.data["CM"]["cameras"]):

            rect = self.getcamerarect(cam)
            rect2 = pg.Rect(rect.x + self.size, rect.y + self.size, rect.w - self.size * 2, rect.h - self.size * 2)
            rect3 = pg.Rect(rect2.x + self.size * 8, rect2.y, rect2.w - self.size * 16, rect2.h)
            # print(camera_border, rect, self.size)
            pg.draw.rect(self.surface, camera_border, rect, max(self.size // 3, 1))
            pg.draw.rect(self.surface, camera_border, rect2, max(self.size // 4, 1))

            pg.draw.rect(self.surface, red, rect3, max(self.size // 3, 1))

            pg.draw.line(self.surface, camera_border, pg.Vector2(rect.center) - pg.Vector2(self.size * 5, 0),
                         pg.Vector2(rect.center) + pg.Vector2(self.size * 5, 0),
                         self.size // 3)

            pg.draw.line(self.surface, camera_border, pg.Vector2(rect.center) - pg.Vector2(0, self.size * 5),
                         pg.Vector2(rect.center) + pg.Vector2(0, self.size * 5),
                         self.size // 3)
            pg.draw.circle(self.surface, camera_border, rect.center, self.size * 3, self.size // 3)

            if "quads" not in self.data["CM"]:
                self.data["CM"]["quads"] = []
                for _ in self.data["CM"]["cameras"]:
                    self.data["CM"]["quads"].append([[0, 0], [0, 0], [0, 0], [0, 0]])
            col = camera_notheld
            if hasattr(self, "held") and hasattr(self, "heldindex"):
                if indx == self.heldindex and self.held:
                    col = camera_held

            quads = self.data["CM"]["quads"][indx]

            newquads = quads.copy()

            for i, q in enumerate(quads):
                n = [0, 0]
                nq = q[0] % 360
                n[0] = math.sin(math.radians(nq)) * q[1] * self.size * 5
                n[1] = -math.cos(math.radians(nq)) * q[1] * self.size * 5
                newquads[i] = n

            tl = pg.Vector2(rect.topleft) + pg.Vector2(newquads[0])
            tr = pg.Vector2(rect.topright) + pg.Vector2(newquads[1])
            br = pg.Vector2(rect.bottomright) + pg.Vector2(newquads[2])
            bl = pg.Vector2(rect.bottomleft) + pg.Vector2(newquads[3])

            if hasattr(self, "held") and indx == closest and not self.held:
                quadindx = self.getquad(closest)

                vec = pg.Vector2([tl, tr, br, bl][quadindx])

                pg.draw.line(self.surface, camera_notheld, rect.center, vec, self.size // 3)

                rects = [rect.topleft, rect.topright, rect.bottomright, rect.bottomleft]
                pg.draw.line(self.surface, camera_held, rects[quadindx], vec, self.size // 3)

                pg.draw.circle(self.surface, camera_held, vec, self.size * 3, self.size // 3)

            pg.draw.polygon(self.surface, col, [tl, bl, br, tr], self.size // 3)


    def rendergeo(self):
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
        global tooltiles
        f: pg.Surface = self.f
        f.fill(color2)
        renderedimage = pg.transform.scale(tooltiles, [
            (tooltiles.get_width() / graphics["tilesize"][0]) * image1size,
            (tooltiles.get_height() / graphics["tilesize"][1]) * image1size])
        cellsize2 = [image1size, image1size]
        for i in range(2, -1, -1):
            renderedimage.set_alpha(settings["global"]["secondarylayeralpha"])
            if i == self.layer:
                renderedimage.set_alpha(settings["global"]["primarylayeralpha"])
            for xp, x in enumerate(self.data["GE"]):
                for yp, y in enumerate(x):
                    self.data["GE"][xp][yp][i][1] = list(set(self.data["GE"][xp][yp][i][1]))
                    cell = y[i][0]
                    over: list = self.data["GE"][xp][yp][i][1]
                    if cell == 7 and 4 not in over:
                        self.data["GE"][xp][yp][i][0] = 0
                        cell = self.data["GE"][xp][yp][i][0]
                    curtool = [graphics["shows"][str(cell)][0] * image1size,
                               graphics["shows"][str(cell)][1] * image1size]
                    f.blit(renderedimage, [xp * image1size, yp * image1size], [curtool, cellsize2])
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
                            if adds == 11: # cracked terrain search
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
                            if adds == 4: # shortcut entrance validation
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
                                    if curtile in [0, 6] and tile in col4: # if we found air in 4 places near
                                        foundair = True
                                        if 5 in incorner(xp - tile[0], yp - tile[1]): # if opposite of air is wire
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
                                    if 5 in curhover and tile in col4: # if wire in 4 places near
                                        pathcount += 1
                                        if pathcount > 1:
                                            break
                                else: # if no breaks
                                    if tilecounter == 7 and foundwire and foundair and pos != -1: # if we found the right one
                                        curtool = [pos[0] * image1size, pos[1] * image1size]
                        f.blit(renderedimage, [xp * image1size, yp * image1size], [curtool, cellsize2])

    def rendertiles(self):
        global mat
        material = pg.transform.scale(mat, [mat.get_width() / 16 * image1size, mat.get_height() / 16 * image1size])
        images = {}
        data = self.data["TE"]["tlMatrix"]
        f: pg.Surface = self.f
        for xp, x in enumerate(data):
            for yp, y in enumerate(x):
                cell = y[self.layer]
                posx = xp * image1size
                posy = yp * image1size

                datcell = cell["tp"]
                datdata = cell["data"]

                if datcell == "default":
                    #pg.draw.rect(field.field, red, [posx, posy, size, size], 3)
                    pass
                elif datcell == "material":
                    if self.data["GE"][xp][yp][self.layer][0] != 0:
                        area = pg.rect.Rect([graphics["matposes"].index(datdata) * image1size, 0, image1size, image1size])
                        f.blit(material, [posx, posy], area)
                elif datcell == "tileHead":
                    it = None
                    if datdata[1] in images.keys():
                        it = images[datdata[1]]
                    else:
                        for i in self.items.keys():
                            for i2 in self.items[i]:
                                if i2["name"] == datdata[1]:
                                    img = i2.copy()
                                    img["image"] = pg.transform.scale(img["image"], [img["image"].get_width() / 16 * image1size, img["image"].get_height() / 16 * image1size])
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
                        pg.draw.rect(f, it["color"], siz, 0)
                    f.blit(it["image"], [cposx, cposy])
                elif datcell == "tileBody":
                    pass

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
    def renderprops(self):
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
            surf.set_alpha(100)
            self.f.blit(surf, [mostleft / spritesize * image1size, mosttop / spritesize * image1size])
            if prop[4].get("points") is not None:
                propcolor = toarr(self.findprop(prop[1])[0]["previewColor"], "color")
                for point in prop[4]["points"]:
                    px, py = toarr(point, "point")
                    pg.draw.circle(self.f, propcolor, [px, py], 5)


    def rendermatrix(self, field, size, matrix, mix=mixcol_empty):
        f = field
        for xp, x in enumerate(matrix):
            for yp, cell in enumerate(x):
                surf = pg.surface.Surface([size, size])
                col = mix.lerp(mixcol_fill, cell / 100)
                surf.set_alpha(col.a)
                surf.fill(col)
                f.blit(surf, [xp * size, yp * size])
                # pg.draw.rect(f, col, [xp * size, yp * size, size, size], 0)

    def saveasf(self):
        self.savef(True)

    def canplaceit(self, x, y, x2, y2):
        return (0 <= x2 and x < len(self.data["GE"])) and (0 <= y2 and y < len(self.data["GE"][0]))


    def destroy(self, x, y):
        def clearitem(mx, my, layer):
            val = self.data["TE"]["tlMatrix"][mx][my][layer]
            if val["data"] == 0:
                return
            name = val["data"][1]
            itm = None
            for i in self.items.keys():
                for i2 in self.items[i]:
                    if i2["name"] == name:
                        itm = i2
                        break
                if itm is not None:
                    break
            if itm is None:
                self.data["TE"]["tlMatrix"][mx][my][layer] = {"tp": "default", "data": 0}
                return
            backx = mx - int((itm["size"][0] * .5) + .5) + 1
            backy = my - int((itm["size"][1] * .5) + .5) + 1
            if backx + itm["size"][0] > len(self.data["TE"]["tlMatrix"]) or backy + itm["size"][1] > len(self.data["TE"]["tlMatrix"][0]):
                return
            # startcell = self.data["TE"]["tlMatrix"][backx][backy][layer]
            sp = itm["cols"][0]
            sp2 = itm["cols"][1]
            w, h = itm["size"]
            for x2 in range(w):
                for y2 in range(h):
                    posx = backx + x2
                    posy = backy + y2
                    csp = sp[x2 * h + y2]
                    if csp != -1:
                        self.data["TE"]["tlMatrix"][posx][posy][layer] = {"tp": "default", "data": 0}
                    if sp2 != 0:
                        try:
                            csp = sp2[x2 * h + y2]
                        except IndexError:
                            csp = -1
                        if csp != -1 and layer + 1 <= 2:
                            self.data["TE"]["tlMatrix"][posx][posy][layer + 1] = {"tp": "default", "data": 0}

        if not self.canplaceit(x, y, x, y):
            return
        tile = self.data["TE"]["tlMatrix"][x][y][self.layer]
        if tile["tp"] != "default":
            match tile["tp"]:
                case "tileBody":
                    posx, posy = toarr(tile["data"][0], "point")
                    clearitem(posx - 1, posy - 1, tile["data"][1] - 1)
                case "tileHead":
                    clearitem(x, y, self.layer)
                case "material":
                    self.data["TE"]["tlMatrix"][x][y][self.layer] = {"tp": "default", "data": 0}
        self.data["TE"]["tlMatrix"][x][y][self.layer] = {"tp": "default", "data": 0}


    def getcamerarect(self, cam):
        pos = pg.Vector2(toarr(cam, "point"))
        p = (pos / image1size) * self.size + self.field.rect.topleft + pg.Vector2(self.xoffset * self.size,
                                                                                  self.yoffset * self.size)
        return pg.Rect([p, [camw * self.size, camh * self.size]])

    def rendergrid(self):
        w, h = self.f.get_size()
        for x in range(0, w, image1size):
            pg.draw.line(self.f, grid, [x, 0], [x, h])
        for y in range(0, h, image1size):
            pg.draw.line(self.f, grid, [0, y], [w, y])
