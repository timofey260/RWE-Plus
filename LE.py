from menuclass import *
from lingotojson import *


class LE(menu):

    def __init__(self, surface: pg.surface.Surface, data):
        self.menu = "LE"
        self.surface = surface
        self.field = widgets.window(self.surface, settings[self.menu]["d1"])
        self.field2 = widgets.window(self.surface, settings[self.menu]["d1"])

        self.fieldmap = self.field.field

        self.fieldadd = self.fieldmap
        self.fieldadd.fill(white)
        self.fieldadd.set_colorkey(white)

        try:
            self.field2.field = pg.image.load(data["level"])
        except:
            self.field2.field.fill(white)
        self.field3 = self.field2
        self.btiles = data["EX2"]["extraTiles"]
        self.data = data

        self.rectdata = [[0, 0], [0, 0], [0, 0]]
        self.xoffset = 0
        self.yoffset = 0

        self.size = settings["TE"]["cellsize"]

        self.message = ''

        self.imagerect = [375, 375]
        self.direction = 0
        self.selectedimage = 0
        self.mode = True
        self.tileimage = None
        self.tileimage2 = None

        self.lightAngle = self.data[self.menu]["lightAngle"]
        self.flatness = self.data[self.menu]["flatness"]

        self.images = {True: [], False: []}

        for i in settings[self.menu]["images"]:
            img = pg.image.load(path2cast + i)
            img.set_colorkey(white)
            self.images[True].append(img)

            img = pg.image.load(path2cast + i)
            arr = pg.pixelarray.PixelArray(img)
            arr.replace(black, red)
            arr.replace(white, black)
            arr.replace(red, white)
            img = arr.make_surface()
            img.set_colorkey(black)

            self.images[False].append(img)

        self.retile()
        self.init()
        self.renderfield()
        self.blit()
        self.resize()

    def blit(self):
        global mousp, mousp2, mousp1
        self.drawmap()

        fieldpos = [self.field.rect.x + self.xoffset * self.size, self.field.rect.y + self.yoffset * self.size]
        fieldpos2 = [fieldpos[0] + math.cos(math.radians(self.lightAngle)) * self.flatness, fieldpos[1] + math.sin(math.radians(self.lightAngle)) * self.flatness]
        self.surface.blit(self.field3.field, fieldpos)
        self.surface.blit(self.field3.field, fieldpos2)
        super().blit()
        if self.field.rect.collidepoint(pg.mouse.get_pos()):
            pos = [math.floor((pg.mouse.get_pos()[0] - self.field.rect.x) / self.size),
                   math.floor((pg.mouse.get_pos()[1] - self.field.rect.y) / self.size)]
            pos2 = [pos[0] * self.size + self.field.rect.x, pos[1] * self.size + self.field.rect.y]
            mouspos = pg.mouse.get_pos()
            curpos = [mouspos[0] - self.tileimage.get_width() / 2, mouspos[1] - self.tileimage.get_height() / 2]
            curpos_on_field = [curpos[0] - fieldpos[0], curpos[1] - fieldpos[1]]

            self.labels[0].set_text("Image: " + settings[self.menu]["images"][self.selectedimage])
            self.labels[1].set_text(f"X: {curpos[0]}, Y: {curpos[1]}")


            self.surface.blit(self.tileimage, curpos)
            bp = pg.mouse.get_pressed(3)

            if bp[0] == 1 and mousp and (mousp2 and mousp1):
                mousp = False
            elif bp[0] == 1 and not mousp and (mousp2 and mousp1):
                self.field2.field.blit(self.tileimage, curpos_on_field)
            elif bp[0] == 0 and not mousp and (mousp2 and mousp1):
                # self.field2.field = pg.transform.scale(self.field3.field, [])
                mousp = True
                self.renderfield()
            self.movemiddle(bp, pos)

    def resize(self):
        super().resize()
        self.field.resize()
        self.field2.field = self.field2.field.subsurface(pg.rect.Rect(0, 0, len(self.data["GE"]) * self.size, len(self.data["GE"][0]) * self.size))
        self.field2.field = self.field2.field.convert_alpha()
        self.field2.field.set_alpha(50)
        self.field2.field.fill(white)
        self.renderfield()

    def renderfield(self):
        renderfield(self.fieldmap, self.size, 0, self.data["GE"])

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
            case "right":
                self.xoffset -= 1
            case "up":
                self.yoffset += 1
            case "down":
                self.yoffset -= 1

    def retile(self):
        self.tileimage2 = self.images[self.mode][self.selectedimage].copy()
        self.setwh()
        self.updateTile()

    def changeup(self):
        self.selectedimage = (self.selectedimage + 1) % len(self.images[self.mode])
        self.retile()
        self.updateTile()

    def changedown(self):
        self.selectedimage = (self.selectedimage - 1)
        if self.selectedimage == -1:
            self.selectedimage = len(self.images[self.mode]) - 1
        self.retile()
        self.updateTile()

    def rotate(self):
        self.tileimage = pg.transform.rotate(self.tileimage2, self.direction)

    def setwh(self):
        rect = [abs(self.imagerect[0]), abs(self.imagerect[1])]
        self.tileimage2 = pg.transform.scale(self.tileimage2, rect)

    def updateTile(self):
        self.tileimage = self.tileimage2.copy()
        self.rotate()

    def inverse(self):
        self.mode = not self.mode
        self.retile()

    def rl(self):
        self.direction += 1
        self.rotate()

    def rr(self):
        self.direction -= 1
        self.rotate()

    def hp(self):
        self.imagerect[1] += 1
        if self.imagerect[1] == 0:
            self.imagerect[1] = 1
        self.setwh()
        self.retile()

    def hm(self):
        self.imagerect[1] -= 1
        if self.imagerect[1] == 0:
            self.imagerect[1] = -1
        self.setwh()
        self.retile()

    def wp(self):
        self.imagerect[0] += 1
        if self.imagerect[0] == 0:
            self.imagerect[0] = 1
        self.setwh()
        self.retile()

    def wm(self):
        self.imagerect[0] -= 1
        if self.imagerect[0] == 0:
            self.imagerect[0] = -1
        self.setwh()
        self.retile()

    def fp(self):
        self.flatness += 1

    def fm(self):
        self.flatness -= 1

    def lp(self):
        self.lightAngle += 1

    def lm(self):
        self.lightAngle -= 1
