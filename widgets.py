import math
import pygame as pg
import copy
import files
import render
from files import settings, fs, path, map, allleters, loadimage
from lingotojson import ItemData
from render import gray, darkgray

pg.font.init()

enablebuttons = True
bol = True
keybol = True
mul = settings["global"]["colormul"]
black = [0, 0, 0]
white = [255, 255, 255]
try:
    tooltipcolor = settings["global"]["colors"]["tooltip"]
    buttontextcolor = settings["global"]["colors"]["buttontext"]
    buttontextcolorlight = settings["global"]["colors"]["buttontextlight"]
    mosttextcolor = settings["global"]["colors"]["mosttextcolor"]
except KeyError:
    tooltipcolor = white
    buttontextcolor = black
    buttontextcolorlight = white
    mosttextcolor = black


def fastmts(window, text: str, x: int | float, y: int | float, col=None, fontsize=settings["global"]["fontsize"], centered=False):
    if col is None:
        col = mosttextcolor
    fontr: pg.font.Font = fs(fontsize)[0]
    surf = fontr.render(text, True, col, None)
    textblit(window, surf, x, y, centered)


def mts(text: str = "", col=None, fontsize=settings["global"]["fontsize"]):
    if col is None:
        col = black
    fontr: pg.font.Font = fs(fontsize)[0]
    sz: int = fs(fontsize)[1]
    if text == "RWE+":
        fontr: pg.font.Font = pg.font.Font(path + "/" + settings["global"]["titlefont"], fontsize)
        sz: int = fontr.size(allleters)[1]
    items = text.split("\n")
    rendered = []
    w = 0
    poses = []
    for l in items:
        render = fontr.render(l, True, col, None)
        rendered.append(render)
        h = render.get_height()
        poses.append(h)
        if render.get_width() > w:
            w = render.get_width()

    surf = pg.Surface([w, (sz - 2) * len(poses)])
    surf = surf.convert_alpha(surf)
    surf.fill([0, 0, 0, 0])

    for i, r in enumerate(rendered):
        surf.blit(r, [0, (fontsize - 2) * i])
    return surf


def textblit(window: pg.Surface, screen_text: pg.Surface, x: int | float, y: int | float, centered: bool = False):
    if centered:
        window.blit(screen_text, [x - screen_text.get_width() / 2, y - screen_text.get_height() / 2])
    else:
        ypos = min(y, window.get_height() - screen_text.get_height()) if centered else y
        if x + screen_text.get_width() < window.get_width():
            window.blit(screen_text, [x, ypos])
        elif x - screen_text.get_width() > 0:
            window.blit(screen_text, [window.get_width() - screen_text.get_width(), ypos])
        else:
            window.blit(screen_text, [x, ypos])


def resetpresses():
    global bol, enablebuttons
    bol = True
    enablebuttons = False


def restrict(a, minimum, maximum):
    return max(min(a, maximum), minimum)


class Button:
    def __init__(self, surface: pg.surface.Surface, rect: pg.rect.Rect, col, text: str, icon=None, onpress=None,
                 onrelease=None, tooltip: str = ""):
        self.surface = surface
        self.rect = copy.deepcopy(rect)
        self.lastrect = copy.deepcopy(rect)
        self.col = pg.Color(col)
        self.col2 = pg.Color(abs(self.col.r - mul), abs(self.col.g - mul), abs(self.col.b - mul))
        self.glow = 0
        self.fontsize = sum(pg.display.get_window_size()) // 74
        self.enabled = True
        self.visible = True

        self.text = text
        self.originaltext = text
        self.textimage = mts(self.originaltext, buttontextcolor, self.fontsize)
        self.tooltip = tooltip
        if files.globalsettings["godmode"]:
            self.tooltipimage = pg.transform.scale(files.god, fs(self.fontsize)[0].size(self.tooltip))
        else:
            self.tooltipimage = mts(self.tooltip, tooltipcolor, self.fontsize)

        self.icon = None
        if files.globalsettings["godmode"]:
            icon = files.god
        self.loadicon = icon
        if type(icon) is list:
            cut = [icon[1][0] * settings["global"]["size"], icon[1][1] * settings["global"]["size"],
                   settings["global"]["size"], settings["global"]["size"]]
            image = loadimage(path + icon[0]).subsurface(cut)
            wh = image.get_height() / settings["global"]["size"] * (rect.height / 100 * surface.get_height())
            size = [wh, wh]
            image = pg.transform.scale(image, size)
            self.icon = image
        elif type(icon) is pg.Surface:
            self.icon = pg.transform.scale(icon, self.rect.size)
        self.onpress = onpress
        self.onrelease = onrelease
        self.bol = True
        self.buttondata = {}
        self.set_text(self.text)

    def set_color(self, color):
        self.col = pg.Color(color)
        self.col2 = pg.Color(abs(self.col.r - mul), abs(self.col.g - mul), abs(self.col.b - mul))

    def blit(self, fontsize=None):
        global bol
        if not self.enabled:
            pg.draw.rect(self.surface, darkgray, self.rect, 0, settings["global"]["roundbuttons"])
            textblit(self.surface, self.textimage, self.rect.center[0], self.rect.center[1], True)
            return
        if not self.visible:
            return
        if fontsize is not None and fontsize != self.fontsize:
            self.set_text(self.text, fontsize)
            if files.globalsettings["godmode"]:
                self.tooltipimage = pg.transform.scale(files.god, fs(self.fontsize)[0].size(self.tooltip))
            else:
                self.tooltipimage = mts(self.tooltip, tooltipcolor, self.fontsize)
        cp = False
        if self.onmouseover():
            pg.mouse.set_cursor(pg.Cursor(pg.SYSTEM_CURSOR_HAND))
            cp = True
            self.glow = min(self.glow + 1, 100)
            if pg.mouse.get_pressed(3)[0] and bol and enablebuttons:
                self.bol = False
                bol = False
                if self.onpress is not None:
                    try:
                        self.onpress(self)
                    except TypeError:
                        self.onpress()
            elif not pg.mouse.get_pressed(3)[0] and not bol and enablebuttons:
                self.bol = True
                bol = True
                if self.onrelease is not None:
                    try:
                        self.onrelease(self)
                    except TypeError:
                        self.onrelease()
        else:
            # if not self.bol:
            #    bol = True
            #    self.bol = True
            self.glow = max(0, self.glow - 1)
        if files.globalsettings["godmode"]:
            px = self.rect.w / 2 - self.icon.get_width() / 2
            py = self.rect.h / 2 - self.icon.get_height() / 2
            pos = [px + self.rect.x, py + self.rect.y]
            self.surface.blit(self.icon, pos)
            return
        paintcol = self.col.lerp(self.col2, self.glow / 100)

        pg.draw.rect(self.surface, paintcol, self.rect, 0, settings["global"]["roundbuttons"])
        if self.icon is None:
            textblit(self.surface, self.textimage, self.rect.center[0], self.rect.center[1], True)
            # mts(self.surface, self.text, self.rect.center[0], self.rect.center[1],
            # black, centered=True, fontsize=fontsize)
        else:
            g255 = int(self.glow / 100 * 255)
            self.textimage.set_alpha(g255)
            textblit(self.surface, self.textimage, self.rect.center[0], self.rect.center[1], True)
            self.icon.set_alpha(255 - g255)
            if cp:
                self.icon.set_alpha(255 - g255)
            px = self.rect.w / 2 - self.icon.get_width() / 2
            py = self.rect.h / 2 - self.icon.get_height() / 2
            pos = [px + self.rect.x, py + self.rect.y]
            self.surface.blit(self.icon, pos)

    def blitshadow(self):
        if not self.enabled or not self.visible:
            return
        invglow = 100 - self.glow
        r2 = self.rect.copy()
        r2 = r2.move(settings["global"]["doublerectoffsetx"] / 100 * invglow,
                     settings["global"]["doublerectoffsety"] / 100 * invglow)
        pg.draw.rect(self.surface, self.col2, r2, 0, settings["global"]["roundbuttons"])

    def blittooltip(self, blittext=True):
        if not self.visible:
            return False
        if self.onmouseover():
            if blittext:
                textblit(self.surface, self.tooltipimage, pg.mouse.get_pos()[0], pg.mouse.get_pos()[1] - 20, False)
            # mts(self.surface, self.tooltip, pg.mouse.get_pos()[0], pg.mouse.get_pos()[1] - 20, white, centered=False)
            return True
        return False

    def resize(self):
        x = self.lastrect.x / 100 * self.surface.get_width()
        y = self.lastrect.y / 100 * self.surface.get_height()
        w = self.lastrect.w / 100 * self.surface.get_width() + 1
        h = self.lastrect.h / 100 * self.surface.get_height() + 1
        self.rect.update(x, y, w, h)
        self.set_text(self.text)
        if type(self.loadicon) is list:
            cut = [self.loadicon[1][0] * settings["global"]["size"], self.loadicon[1][1] * settings["global"]["size"],
                   settings["global"]["size"], settings["global"]["size"]]
            image = loadimage(path + self.loadicon[0]).subsurface(cut)
            wh = image.get_height() / settings["global"]["size"] * self.rect.height
            size = [wh, wh]
            image = pg.transform.scale(image, size)
            self.icon = image
        elif type(self.loadicon) is pg.Surface:
            self.icon = pg.transform.scale(self.loadicon, self.rect.size)
        self.set_text(self.text, self.fontsize)

    def onmouseover(self):
        return self.rect.collidepoint(pg.mouse.get_pos()) and self.visible and self.enabled

    def set_tooltip(self, text, fontsize=None):
        if text == self.tooltip:
            return
        self.tooltip = text
        if files.globalsettings["godmode"]:
            self.tooltipimage = pg.transform.scale(files.god, fs(self.fontsize)[0].size(self.tooltip))
        if fontsize is not None:
            self.tooltipimage = mts(text, tooltipcolor, self.fontsize)
            return
        self.tooltipimage = mts(text, tooltipcolor, sum(pg.display.get_window_size()) // 74)

    def set_text(self, text, fontsize=None):
        if text == self.text and self.fontsize == fontsize:
            return
        self.text = text
        self.fontsize = sum(pg.display.get_window_size()) // 74
        luma = ((self.col.r * 229) + (self.col.g * 587) + (self.col.b * 114)) / 1000 < 40
        bc = buttontextcolorlight if luma else buttontextcolor
        if fontsize is not None:
            self.fontsize = fontsize
            self.textimage = mts(text, bc, self.fontsize)
            return
        self.textimage = mts(text, bc, sum(pg.display.get_window_size()) // 74)

    @property
    def xy(self):
        return [self.rect.x, self.rect.y]


class Window:
    def __init__(self, surface: pg.surface.Surface, data):
        self.surface = surface
        self.rect = copy.deepcopy(pg.rect.Rect(data["rect"]))
        self.rect2 = copy.deepcopy(pg.rect.Rect(data["rect"]))
        self.field = pg.surface.Surface(
            [self.rect.width / 100 * surface.get_width(), self.rect.height / 100 * surface.get_height()])
        self.color = data["color"]
        self.border = data["border"]
        self.visible = True

    def blit(self, draw=True):
        if not self.visible:
            return
        if draw:
            pg.draw.rect(self.surface, self.color, self.rect)
        self.surface.blit(self.field, self.rect.topleft)
        w = 6
        b = pg.Rect(self.rect)
        b.update(b.x - w, b.y - w, b.w + w + w, b.h + w + w)
        pg.draw.rect(self.surface, self.border, b, 6, 6)

    def resize(self):
        self.field = pg.surface.Surface(
            [self.rect2.width / 100 * self.surface.get_width(), self.rect2.height / 100 * self.surface.get_height()])
        self.rect = pg.rect.Rect(
            self.rect2.x / 100 * self.surface.get_width(),
            self.rect2.y / 100 * self.surface.get_height(),
            self.rect2.width / 100 * self.surface.get_width(),
            self.rect2.height / 100 * self.surface.get_height())

    def copy(self):
        wcopy = Window(self.surface, {"rect": [0, 0, 1, 1], "color": [0, 0, 0], "border": [0, 0, 0]})
        wcopy.rect = self.rect.copy()
        wcopy.rect2 = self.rect2.copy()
        wcopy.field = self.field.copy()
        self.color = self.color.copy()
        self.border = self.border.copy()
        return wcopy

    def onmouseover(self):
        return self.rect.collidepoint(pg.mouse.get_pos())


class Label:
    def __init__(self, surface: pg.surface.Surface, text: str, pos: pg.Vector2, color, fontsize=15):
        self.surface = surface
        self.text = text
        self.originaltext = text
        if files.globalsettings["godmode"]:
            self.textimage = pg.transform.scale(files.god, fs(fontsize)[0].size(text))
        else:
            self.textimage = mts(text, color, fontsize)
        self.pos = copy.deepcopy(pos)
        self.posp = copy.deepcopy(pos)
        self.color = color
        self.fontsize = fontsize
        self.visible = True

    def blit(self):
        if not self.visible:
            return
        textblit(self.surface, self.textimage, self.pos[0], self.pos[1])
        # mts(self.surface, self.text, self.pos[0], self.pos[1], self.color, self.fontsize)

    def resize(self):
        self.pos[0] = self.posp[0] / 100 * self.surface.get_width()
        self.pos[1] = self.posp[1] / 100 * self.surface.get_height()
        if files.globalsettings["godmode"]:
            self.textimage = pg.transform.scale(files.god, fs(self.fontsize)[0].size(self.text))
        else:
            self.textimage = mts(self.text, self.color, self.fontsize)

    def set_text(self, text=None):
        if text is None:
            text = self.text
        self.text = text
        if files.globalsettings["godmode"]:
            self.textimage = pg.transform.scale(files.god, fs(self.fontsize)[0].size(text))
        else:
            self.textimage = mts(self.text, self.color, self.fontsize)


class Slider:
    def __init__(self, surface: pg.surface.Surface, text, pos, len, min, max, value, step):
        self.surface = surface
        self.text = text
        self.originaltext = text
        self.textimage = mts(text, buttontextcolor)
        self.pos = pg.Vector2(copy.deepcopy(pos)) / 100 * pg.display.get_window_size()[0]
        self.posp = pg.Vector2(copy.deepcopy(pos))

        self.len = len / 100 * pg.display.get_window_size()[0]
        self.lens = len
        self.min = min
        self.max = max
        self.value = value
        self.step = step

        self.held = False
        self.mp = False
        self.set_text(f"{self.originaltext}: {self.value}")
        self.resize()

    def blit(self):
        screensize = sum(pg.display.get_window_size())
        s = screensize // 100
        mpos = pg.Vector2(pg.mouse.get_pos())
        sliderpos = self.pos.lerp(self.pos + pg.Vector2(self.len, 0), map(self.value, self.min, self.max, 0, 1))
        pos2 = self.pos + pg.Vector2(self.len, 0)

        pg.draw.line(self.surface, buttontextcolor, self.pos, pos2, 5)
        pg.draw.circle(self.surface, pg.Color(settings["global"]["colors"]["slidebar"]), sliderpos, s)
        textblit(self.surface, self.textimage, self.pos.x, self.pos.y)

        if pg.mouse.get_pressed()[0] and self.mp:
            self.mp = False
            if pg.Rect([sliderpos.x - s / 2, sliderpos.y - s / 2, s, s]).collidepoint(list(mpos)):
                self.held = True
        elif pg.mouse.get_pressed()[0] and not self.mp:
            if self.held:
                val = max(min(map(mpos.x, self.pos.x, pos2.x, self.min, self.max), self.max), self.min)
                self.value = val - val % self.step
                self.set_text(f"{self.originaltext}: {int(self.value)}")
        elif not pg.mouse.get_pressed()[0] and not self.mp:
            self.mp = True
            self.held = False

    def resize(self):
        screensize = pg.Vector2(pg.display.get_window_size())
        self.pos = pg.Vector2(copy.deepcopy(self.posp)) / 100
        self.pos.x *= screensize.x
        self.pos.y *= screensize.y
        self.len = self.lens / 100 * pg.display.get_window_size()[0]

    def set_text(self, text):
        self.text = text
        self.textimage = mts(text, buttontextcolor)


class Selector():
    def __init__(self, menu, data, selectorid, favouritesfile=None):
        self.cursorcolor = pg.Color(255, 0, 0)
        self.drawrect = True
        self.callbackafterchange = True
        self.data: ItemData = data
        self.buttonslist: list[Button, ] = []
        self.menu = menu

        self.itemrect = pg.Rect(self.menu.settings[selectorid]["itempos"])
        self.buttonoffset = pg.Vector2(self.itemrect.topleft)
        self.bigbuttonrect = pg.Rect(self.menu.settings[selectorid]["catpos"])
        self.itemrect.topleft = self.bigbuttonrect.bottomleft

        self.bigbutton = None  # Button(surface, self.bigbuttonrect, white, "")
        self.favsbutton: Button = None

        self.currentcategory = 0
        self.currentitem = 0
        self.lastcategory = 0
        self.lastitem = 0

        self.surface = menu.surface
        self.favouritefile = files.resolvepath(files.path2favs + favouritesfile) if favouritesfile is not None else None

        self.pos = pg.Vector2()
        self.lastshow = "items"
        self.show = "items"  # NOQA cats, items, favs
        self.callback = self.defaultcallback

        self.catsnum = len(self.data)
        self.itemsnum = 1
        self._favourites = ItemData()
        '''
        data format:
        [{
            name,
            color,
            items:
            {nm, description, data},
            descvalue - optional, big button value
        }, ...]
        '''
        self.items()
        self.resize()

    def reload_data(self, data: ItemData, discardselected=True):
        self.data = data
        if discardselected or self.data.isempty():
            self.currentcategory = 0
            self.currentitem = 0
        if not self.data.isempty():
            self.currentcategory = restrict(self.currentcategory, 0, len(self.data.categories) - 1)
            self.currentitem = restrict(self.currentitem, 0, len(self.data[self.currentcategory]["items"]) - 1)
        self.items()

    def loadfavorites(self):
        print(f"loading favourites from file: {self.favouritefile}")
        if self.favouritefile is None:
            return
        try:
            file = open(self.favouritefile, "r")
        except FileNotFoundError:
            print("File not found!!!")
            return
        lines = file.readlines()
        self._favourites = ItemData()
        catdata = {"name": "", "color": pg.color.THECOLORS["black"], "items": []}
        for i, line in enumerate(lines):
            line: str = line.strip()
            if len(line) <= 0:
                continue
            if line[0] == "#":
                if len(catdata["name"]) > 0:
                    self._favourites.append(catdata)
                catdata = {"name": line[1:], "color": pg.color.THECOLORS["black"], "items": []}
            else:
                tile = self.data[line].copy()
                if tile is None:
                    print(f"couldn't load item: {line} in category {catdata['name']}")
                    continue
                tile["category"] = catdata["name"]
                catdata["items"].append(tile)
        if len(catdata["name"]) > 0:
            self._favourites.append(catdata)

    def savefavourites(self):
        if self.favouritefile is None:
            return
        with open(self.favouritefile, "w") as file:
            for indx, cat in enumerate(self._favourites.categories):
                file.write(f"#{cat}\n")
                for item in self._favourites.data[indx]["items"]:
                    file.write(f'{item["nm"]}\n')

    def resize(self):
        for i in self.buttonslist:
            i.resize()
        if self.bigbutton is not None:
            self.bigbutton.resize()
        if self.favsbutton is not None:
            self.favsbutton.resize()
        self.restrict()

    def addtofavs(self):
        if self._favourites.isempty():
            self.loadfavorites()
        if self.show != "items":
            return
        cats = {}
        for indx, catname in enumerate(self._favourites.categories):
            print(indx, catname, self._favourites[indx])
            cats[catname] = "\n".join([i["nm"] for i in self._favourites[indx]["items"]])
            cats[catname] += "\n\nRemove tile from here" * int(self._favourites[catname, self.selecteditem["nm"]] is not None)
        cats["New category"] = "creates a new category"
        foundcat = self.menu.find(cats, "Select a category")
        if foundcat is None:
            return
        if foundcat == "New category":
            cat = self.menu.askstr("Name of category")
            if cat is None:
                print("Canceled")
                return
            self._favourites.addcat(cat, white)
            foundcat = cat
        item = self.selecteditem.copy()
        item["category"] = foundcat

        tile = self._favourites[foundcat, self.selecteditem["nm"]]
        if tile is not None:
            self.setbyname(self.selecteditem["nm"], dorecreate=False)
            self.removefromfavs()
            print("Item removed!")
            return
        self._favourites[self._favourites.categories.index(foundcat)]["items"].append(item)
        self.savefavourites()

    def items(self):
        self.buttonslist = []
        if self.data.isempty():
            self.itemsnum = 0
            self.catsnum = 0
            return
        if self.show == "cats":
            self.currentcategory = self.currentitem + (self.currentcategory * self.menu.settings["category_count"])
            self.currentitem = 0
        elif self.show == "favs":
            item = self.selecteditem
            founditem = self.data[item["nm"]]
            self.currentcategory = self.data.categories.index(founditem["category"])
            self.currentitem = self.data.getnameindex(self.currentcategory, founditem["nm"])
            self.setbyname(founditem["nm"], dorecreate=False, fromfavs=False)
        catdata = self.data[self.currentcategory]

        self.itemsnum = len(catdata["items"])
        self.catsnum = len(self.data)

        rect: pg.Rect = copy.deepcopy(self.bigbuttonrect)
        self.show = "items"
        if self.favouritefile is not None:
            rect.w = math.ceil(self.bigbuttonrect.w * .8)

        self.bigbutton = Button(self.surface, rect, settings["global"]["color"], catdata["name"],
                                tooltip=catdata.get("descvalue", self.menu.returnkeytext("Open category list(<[-changematshow]>)")),
                                onpress=self.catswap)
        rect2: pg.rect = pg.Rect(rect.topright, pg.Vector2(math.floor(self.bigbuttonrect.w * .2), self.bigbuttonrect.h))
        if self.itemsnum == 0:
            self.resize()
            return
        if self.favouritefile is not None:
            self.favsbutton = Button(self.surface, rect2, settings["global"]["color"], "F",
                                     ["icons.png", [5, 0]],
                                     tooltip=self.menu.returnkeytext("Add or remove selected item to favourites(<[-addtofavs]>)"),
                                     onpress=self.addtofavs)
        for count, item in enumerate(catdata["items"]):
            rect = self.itemrect.copy()
            rect = rect.move(*(self.buttonoffset * count).xy)
            btn = Button(self.surface, rect, item["color"], item["nm"], tooltip=item["description"],
                         onpress=self.onclick)
            btn.buttondata = item
            self.buttonslist.append(btn)
        self.resize()

    def categories(self):
        self.buttonslist = []
        self.favsbutton = None
        if self.show == "items":
            self.currentitem = self.currentcategory % self.menu.settings["category_count"]
            self.currentcategory = self.currentcategory // self.menu.settings["category_count"]
        currenttab = self.currentcategory * self.menu.settings["category_count"]

        self.itemsnum = len(self.data.categories[currenttab:currenttab + self.menu.settings["category_count"]])
        self.catsnum = math.ceil(len(self.data.categories) / self.menu.settings["category_count"])

        self.show = "cats"
        self.bigbutton = Button(self.surface, self.bigbuttonrect, settings["global"]["color"],
                                "categories" if self.catsnum <= 1 else
                                "categories " + str(self.currentcategory),
                                tooltip=self.menu.returnkeytext("Select category(<[-changematshow]>)"),
                                onpress=self.catswap)
        for count, item in enumerate(self.data.categories[currenttab:currenttab + self.menu.settings["category_count"]]
                                     ):
            itemindx = currenttab + count
            rect = self.itemrect.copy()
            rect = rect.move(*(self.buttonoffset * count).xy)
            tooltip = "\n".join(i["nm"] for i in self.data[itemindx]["items"])
            btn = Button(self.surface, rect, self.data.colors[itemindx], item, tooltip=tooltip, onpress=self.selectcat)
            btn.buttondata = {"name": item, "tp": "cat", "index": itemindx}
            self.buttonslist.append(btn)
        self.resize()

    def selectcat(self, buttondata: Button):
        self.currentcategory = buttondata.buttondata["index"]
        self.currentitem = 0
        self.show = "items"
        self.items()
        self.onclick("set")

    def catswap(self):
        if self.show == "items":
            self.categories()
        else:
            self.items()

    # self.recreate()

    def favourites(self):
        if self._favourites.isempty():
            self.loadfavorites()
        if self._favourites.isempty():
            print("No favourite items!!!")
            self.items()
            return
        self.buttonslist = []
        if self.show != "favs":
            self.currentitem = 0
            self.currentcategory = 0
        self.itemsnum = len(self._favourites[self.currentcategory]["items"])
        self.catsnum = len(self._favourites.categories)

        self.show = "favs"
        rect: pg.Rect = copy.deepcopy(self.bigbuttonrect)
        rect.w = math.ceil(self.bigbuttonrect.w * .8)
        self.bigbutton = Button(self.surface, rect, settings["global"]["color"],
                                self._favourites.categories[self.currentcategory],
                                tooltip=self.menu.returnkeytext("Select category(<[-changematshow]>)"),
                                onpress=self.catswap)
        rect2: pg.rect = pg.Rect(rect.topright, pg.Vector2(math.floor(self.bigbuttonrect.w * .2), self.bigbuttonrect.h))
        self.favsbutton = Button(self.surface, rect2, settings["global"]["color"], "F", ["icons.png", [4, 0]],
                                 tooltip=self.menu.returnkeytext("Remove selected item from favourites(<[-addtofavs]>)"),
                                 onpress=self.removefromfavs)
        for count, item in enumerate(self._favourites[self.currentcategory]["items"]):
            rect = self.itemrect.copy()
            rect = rect.move(*(self.buttonoffset * count).xy)
            btn = Button(self.surface, rect, item["color"], item["nm"], tooltip=item["description"],
                         onpress=self.onclick)
            btn.buttondata = item
            self.buttonslist.append(btn)
        self.resize()

    def removefromfavs(self):
        self._favourites.data[self.currentcategory]["items"].pop(self.currentitem)
        if len(self._favourites[self.currentcategory]["items"]) <= 0:
            self._favourites.pop(self.currentcategory)
            self.currentcategory = 0
        if self._favourites.isempty():
            self.show = "items"
        self.lastshow = ""
        self.currentitem = 0
        self.savefavourites()
        self.recreate()
        self.onclick(self.buttonslist[0])

    def defaultcallback(self, item):
        pass

    def onclick(self, button: Button | str):
        if type(button) is Button:
            self.callback(button.buttondata)
        if type(button) is str and self.show != "cats" and button == "set" and self.callbackafterchange:
            self.callback(self.selecteditem)

    def blit(self):
        if len(self.buttonslist) > 0 and self.drawrect:
            pg.draw.rect(self.surface, settings["TE"]["menucolor"], pg.rect.Rect(self.buttonslist[0].xy,
                                                                             [self.buttonslist[0].rect.w,
                                                                              len(self.buttonslist[:-1]) *
                                                                              self.buttonslist[0].rect.h + 1]))
        for button in self.buttonslist:
            button.blitshadow()
        if self.bigbutton is not None:
            self.bigbutton.blitshadow()
        if self.favsbutton is not None:
            self.favsbutton.blitshadow()
        if self.bigbutton is not None:
            self.bigbutton.blit(sum(pg.display.get_window_size()) // 100)
        if self.favsbutton is not None:
            self.favsbutton.blit()
        for button in self.buttonslist:
            button.blit(sum(pg.display.get_window_size()) // 120)

    def blittooltip(self):
        if len(self.buttonslist) > 0:
            cir = [self.buttonslist[self.currentitem].rect.x + 3,
                   self.buttonslist[self.currentitem].rect.y + self.buttonslist[self.currentitem].rect.h / 2]
            pg.draw.circle(self.surface, self.cursorcolor, cir, min(self.buttonslist[self.currentitem].rect.h / 2, 15))
        for button in self.buttonslist:
            if button.blittooltip(False):
                mwfpos = button.rect.topright
                import menuclass
                import TE
                if issubclass(type(self.menu), menuclass.MenuWithField):
                    mwf: menuclass.MenuWithField = self.menu
                    mwfpos = mwf.field.rect.topleft
                if button.buttondata.get("preview"):
                    self.surface.blit(button.buttondata["preview"], mwfpos)
                if button.buttondata.get("image"):
                    if button.buttondata.get("size"):
                        w, h = button.buttondata["size"]
                        w *= self.menu.size
                        h *= self.menu.size
                        self.surface.blit(pg.transform.scale(button.buttondata["image"], [w, h]), mwfpos)
                    else:
                        self.surface.blit(button.buttondata["images"][0], mwfpos)
                if button.buttondata.get("images"):
                    if button.buttondata.get("size"):
                        w, h = button.buttondata["size"]
                        w *= self.menu.size
                        h *= self.menu.size
                        self.surface.blit(pg.transform.scale(button.buttondata["images"][0], [w, h]), mwfpos)
                    else:
                        self.surface.blit(button.buttondata["images"][0], mwfpos)
                if type(self.menu) is TE.TE and button.buttondata.get("printcols", False):
                    m: TE.TE = self.menu
                    m.printcols(0, 0, button.buttondata, True)
                button.blittooltip()
                break
        if self.favsbutton is not None:
            self.favsbutton.blittooltip()
        if self.bigbutton is not None:
            self.bigbutton.blittooltip()

    def up(self):
        if self.itemsnum <= 0 or self.data.isempty():
            return
        self.currentitem = (self.currentitem - 1) % self.itemsnum
        self.onclick("set")

    def down(self):
        if self.itemsnum <= 0 or self.data.isempty():
            return
        self.currentitem = (self.currentitem + 1) % self.itemsnum
        self.onclick("set")

    def right(self):
        if self.catsnum <= 0 or self.data.isempty():
            return
        self.currentcategory = (self.currentcategory + 1) % self.catsnum
        self.recreate()
        self.onclick("set")

    def left(self):
        if self.catsnum <= 0 or self.data.isempty():
            return
        self.currentcategory = (self.currentcategory - 1) % self.catsnum
        self.recreate()
        self.onclick("set")

    def recreate(self):
        if (self.currentcategory == self.lastcategory and self.currentitem == self.lastitem and
                self.show == self.lastshow):
            return
        self.lastshow = copy.deepcopy(self.show)
        self.lastitem = copy.deepcopy(self.currentitem)
        self.lastcategory = copy.deepcopy(self.currentcategory)
        match self.show:
            case "items":
                self.items()
            case "cats":
                self.categories()
            case "favs":
                self.favourites()

    def setcat(self, index):
        self.currentcategory = index
        self.currentitem = 0
        self.show = "items"
        self.recreate()

    def setbyname(self, name, dorecreate=True, fromfavs=True, category=None):
        #todo make it look better
        if category is not None:
            if self.show == "favs" and fromfavs:
                tile = self._favourites[category, name]
                self.currentcategory = self._favourites.categories.index(category)
                self.currentitem = self._favourites[self.currentcategory]["items"].index(tile)
            elif self.show == "favs":
                foundtile = self.data[category, name]
                self.currentcategory = self.data.categories.index(category)
                self.currentitem = self.data.getnameindex(self.currentcategory, foundtile["nm"])
            else:
                tile = self.data[category, name]
                self.currentcategory = self.data.categories.index(category)
                self.currentitem = self.data[self.currentcategory]["items"].index(tile)
                self.show = "items"
        else:
            if self.show == "favs" and fromfavs:
                tile = self._favourites[name]
                self.currentcategory = self._favourites.categories.index(tile["category"])
                self.currentitem = self._favourites[self.currentcategory]["items"].index(tile)
            elif self.show == "favs":
                foundtile = self.data[name]
                self.currentcategory = self.data.categories.index(foundtile["category"])
                self.currentitem = self.data.getnameindex(self.currentcategory, foundtile["nm"])
            else:
                tile = self.data[name]
                self.currentcategory = self.data.categories.index(tile["category"])
                self.currentitem = self.data[self.currentcategory]["items"].index(tile)
                self.show = "items"
        if dorecreate:
            self.recreate()

    def setbybuttondata(self, object):
        self.currentitem = self.data[self.currentcategory]["items"].index(object)

    def restrict(self):
        self.currentitem = restrict(self.currentitem, 0, self.itemsnum - 1)
        self.currentcategory = restrict(self.currentcategory, 0, self.catsnum - 1)

    @property
    def selecteditem(self):
        self.restrict()
        if self.show == "favs":
            return self._favourites[self.currentcategory]["items"][self.currentitem]
        return self.data[self.currentcategory]["items"][self.currentitem]

    @property
    def touchesanything(self):
        for i in self.buttonslist:
            if i.onmouseover():
                return True
        if self.favsbutton is not None and self.favsbutton.onmouseover():
            return True
        if self.bigbutton is not None:
            return self.bigbutton.onmouseover()
        return False

    def selectlast(self):
        self.items()
        self.currentcategory = len(self.data) - 1
        self.currentitem = len(self.data[self.currentcategory]["items"]) - 1
        self.items()


class Notification:
    def __init__(self, surface: pg.Surface, message: str):
        self.surface = surface
        self.message = message
        self.pos = pg.Vector2()
        self.anim = 0
        self.messagelabel = Label(surface, message, self.pos, white, 30)
        padding = 20
        self.pos.update([-self.messagelabel.textimage.get_width() - padding * 2,
                         pg.display.get_window_size()[1] - padding - self.messagelabel.textimage.get_height()])
        self.startpos = copy.deepcopy(self.pos)
        self.endpos = pg.Vector2(padding, self.pos.y)
        self.delete = False

    def blit(self):
        ranim = self.anim / 100
        if self.anim < 100:
            self.pos = self.startpos.lerp(self.endpos, 1 - (1 - ranim) ** 3)
        elif 500 < self.anim < 600:
            ranim = (self.anim - 500) / 100
            self.pos = self.endpos.lerp(self.startpos, ranim ** 3)
        elif self.anim > 600:
            self.delete = True
        self.anim += 1
        pg.draw.rect(self.surface, gray, pg.Rect.inflate(
            pg.Rect([self.pos, self.messagelabel.textimage.get_size()]), 20, 20), border_radius=20)
        self.messagelabel.pos = self.pos
        self.messagelabel.blit()
