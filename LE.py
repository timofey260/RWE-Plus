from menuclass import *
from lingotojson import *


class LE(menu):

    def __init__(self, surface: pg.surface.Surface, data):
        self.menu = "LE"
        self.surface = surface
        self.field = widgets.window(self.surface, settings[self.menu]["d1"])
        self.field2 = widgets.window(self.surface, settings[self.menu]["d1"])
        self.field2.field.set_alpha(50)
        self.btiles = data["EX2"]["extraTiles"]
        self.data = data

        self.rectdata = [[0, 0], [0, 0], [0, 0]]
        self.xoffset = 0
        self.yoffset = 0

        self.size = settings["TE"]["cellsize"]

        self.message = ''

        self.selectedimage = 0
        self.mode = True
        self.tileimage = None
        self.tileimage2 = None

        self.images = []

        for i in settings[self.menu]["images"]:
            self.images.append(pg.image.load(path2cast + i))

        self.retile()
        self.init()
        self.renderfield()
        self.blit()
        self.resize()

    def blit(self):
        global mousp, mousp2, mousp1
        self.field.blit()
        self.field2.blit()
        super().blit()
        if self.field.rect.collidepoint(pg.mouse.get_pos()):
            pos = [math.floor((pg.mouse.get_pos()[0] - self.field.rect.x) / self.size),
                   math.floor((pg.mouse.get_pos()[1] - self.field.rect.y) / self.size)]
            pos2 = [pos[0] * self.size + self.field.rect.x, pos[1] * self.size + self.field.rect.y]
            bp = pg.mouse.get_pressed(3)
            self.movemiddle(bp, pos)
        rect = [self.xoffset * self.size, self.yoffset * self.size, len(self.data["GE"]) * self.size,
                len(self.data["GE"][0]) * self.size]
        pg.draw.rect(self.field.field, black, rect, 5)
        fig = [(self.btiles[0] + self.xoffset) * self.size, (self.btiles[1] + self.yoffset) * self.size,
               (len(self.data["GE"]) - self.btiles[2] - self.btiles[0]) * self.size,
               (len(self.data["GE"][0]) - self.btiles[3] - self.btiles[1]) * self.size]
        rect = pg.rect.Rect(fig)
        pg.draw.rect(self.field.field, white, rect, 5)

    def resize(self):
        super().resize()
        self.field.resize()
        self.field2.resize()
        self.renderfield()

    def renderfield(self):
        renderfield(self.field, self.size, 0, [self.xoffset, self.yoffset], self.data["GE"])

    def send(self, message):
        if message[0] == "-":
            self.mpos = 1
            getattr(self, message[1:])()
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
                self.renderfield()
            case "right":
                self.xoffset -= 1
                self.renderfield()
            case "up":
                self.yoffset += 1
                self.renderfield()
            case "down":
                self.yoffset -= 1
                self.renderfield()
    def retile(self):
        self.tileimage2 = self.images[self.selectedimage]
        self.tileimage = self.tileimage2.copy()

    def changeup(self):
        pass

