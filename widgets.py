import pygame as pg
import copy
from files import settings, fs, path, map, allleters, loadimage
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
except KeyError:
    tooltipcolor = white
    buttontextcolor = black
    buttontextcolorlight = white


def fastmts(window, text: str, x: int, y: int, col=None, fontsize=settings["global"]["fontsize"], centered=False):
    if col is None:
        col = black
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
        if x + screen_text.get_width() < window.get_width():
            window.blit(screen_text, [x, y])
        elif x - screen_text.get_width() > 0:
            window.blit(screen_text, [window.get_width() - screen_text.get_width(), y])
        else:
            window.blit(screen_text, [x, y])


def resetpresses():
    global bol, enablebuttons
    bol = True
    enablebuttons = False


class button:
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
        self.tooltipimage = mts(self.tooltip, tooltipcolor, self.fontsize)

        self.icon = None
        self.loadicon = icon
        if icon is not None:
            cut = [icon[1][0] * settings["global"]["size"], icon[1][1] * settings["global"]["size"],
                   settings["global"]["size"], settings["global"]["size"]]
            image = loadimage(path + icon[0]).subsurface(cut)
            wh = image.get_height() / settings["global"]["size"] * (rect.height / 100 * surface.get_height())
            size = [wh, wh]
            image = pg.transform.scale(image, size)
            self.icon = image
        self.onpress = onpress
        self.onrelease = onrelease
        self.bol = True
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
                        self.onpress(self.text)
                    except TypeError:
                        self.onpress()
            elif not pg.mouse.get_pressed(3)[0] and not bol and enablebuttons:
                self.bol = True
                bol = True
                if self.onrelease is not None:
                    try:
                        self.onrelease(self.text)
                    except TypeError:
                        self.onrelease()
        else:
            # if not self.bol:
            #    bol = True
            #    self.bol = True
            self.glow = max(0, self.glow - 1)
        paintcol = self.col.lerp(self.col2, self.glow / 100)

        pg.draw.rect(self.surface, paintcol, self.rect, 0, settings["global"]["roundbuttons"])
        if self.icon is None:
            textblit(self.surface, self.textimage, self.rect.center[0], self.rect.center[1], True)
            # mts(self.surface, self.text, self.rect.center[0], self.rect.center[1], black, centered=True, fontsize=fontsize)
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

    def blittooltip(self):
        if not self.visible:
            return
        if self.onmouseover():
            textblit(self.surface, self.tooltipimage, pg.mouse.get_pos()[0], pg.mouse.get_pos()[1] - 20, False)
            # mts(self.surface, self.tooltip, pg.mouse.get_pos()[0], pg.mouse.get_pos()[1] - 20, white, centered=False)

    def resize(self):
        x = self.lastrect.x / 100 * self.surface.get_width()
        y = self.lastrect.y / 100 * self.surface.get_height()
        w = self.lastrect.w / 100 * self.surface.get_width() + 1
        h = self.lastrect.h / 100 * self.surface.get_height() + 1
        self.rect.update(x, y, w, h)
        self.set_text(self.text)

        if self.icon is not None:
            cut = [self.loadicon[1][0] * settings["global"]["size"], self.loadicon[1][1] * settings["global"]["size"],
                   settings["global"]["size"], settings["global"]["size"]]
            image = loadimage(path + self.loadicon[0]).subsurface(cut)
            wh = image.get_height() / settings["global"]["size"] * self.rect.height
            size = [wh, wh]
            image = pg.transform.scale(image, size)
            self.icon = image
        self.set_text(self.text, self.fontsize)

    def onmouseover(self):
        return self.rect.collidepoint(pg.mouse.get_pos())

    def set_tooltip(self, text, fontsize=None):
        if text == self.tooltip:
            return
        self.tooltip = text
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


class window:
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
        wcopy = window(self.surface, {"rect": [0, 0, 1, 1], "color": [0, 0, 0], "border": [0, 0, 0]})
        wcopy.rect = self.rect.copy()
        wcopy.rect2 = self.rect2.copy()
        wcopy.field = self.field.copy()
        self.color = self.color.copy()
        self.border = self.border.copy()
        return wcopy

    def onmouseover(self):
        return self.rect.collidepoint(pg.mouse.get_pos())


class lable:
    def __init__(self, surface: pg.surface.Surface, text, pos, color, fontsize=15):
        self.surface = surface
        self.text = text
        self.originaltext = text
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
        self.textimage = mts(self.text, self.color, self.fontsize)

    def set_text(self, text=None):
        if text is None:
            text = self.text
        self.text = text
        self.textimage = mts(text, self.color, self.fontsize)


class slider:
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
                self.set_text(f"{self.originaltext}: {self.value}")
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
