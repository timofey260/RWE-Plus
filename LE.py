from lingotojson import *
from menuclass import *


class LE(menu_with_field):

    def __init__(self, surface: pg.surface.Surface, data):
        self.menu = "LE"
        super().__init__(surface, data, "LE")
        self.field2 = widgets.window(self.surface, settings[self.menu]["d1"])

        self.ofstop = ofstop
        self.ofsleft = ofsleft

        sc = [(len(self.data["GE"]) + self.ofsleft) * image1size, (len(self.data["GE"][0]) + self.ofstop) * image1size]
        try:
            lev = os.path.splitext(data["path"])[0] + ".png"
            self.field2.field = pg.transform.scale(pg.image.load(lev), sc)
        except FileNotFoundError:
            self.field2.field = pg.surface.Surface(sc)
            self.field2.field.fill(white)


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

        super().__init__(surface, data, "LE")
        self.rs()
        self.retile()
        self.init()
        self.renderfield_all()
        self.blit()
        self.resize()

    def blit(self):
        global mousp, mousp2, mousp1
        self.fieldadd.fill(white)
        if not pg.key.get_pressed()[pg.K_LCTRL]:
            self.drawmap()
        else:
            self.field.field.fill(self.field.color)

        xos = self.xoffset * self.size
        yos = self.yoffset * self.size

        fieldpos = [xos - (self.ofsleft * self.size), yos - (self.ofstop * self.size)]
        fieldpos2 = [fieldpos[0] + math.cos(math.radians(self.lightAngle)) * self.flatness * (self.size/10),
                     fieldpos[1] + math.sin(math.radians(self.lightAngle)) * self.flatness * (self.size/10)]

        super().blit()
        self.field.field.blit(self.field3.field, fieldpos)
        if not pg.key.get_pressed()[pg.K_LSHIFT]:
            self.field.field.blit(self.field3.field, fieldpos2)
        self.field.blit(False)
        if self.field.rect.collidepoint(pg.mouse.get_pos()):
            pos = [math.floor((pg.mouse.get_pos()[0] - self.field.rect.x) / self.size),
                   math.floor((pg.mouse.get_pos()[1] - self.field.rect.y) / self.size)]
            #  pos2 = [pos[0] * self.size + self.field.rect.x, pos[1] * self.size + self.field.rect.y]
            mouspos = pg.mouse.get_pos()
            mouspos_onfield = [mouspos[0] - self.field.rect.x - fieldpos[0], mouspos[1] - self.field.rect.y - fieldpos[1]]
            curpos = [mouspos[0] - self.tileimage.get_width() / 2, mouspos[1] - self.tileimage.get_height() / 2]

            curpos_on_field = [mouspos_onfield[0] - self.tileimage.get_width() / 2,
                               mouspos_onfield[1] - self.tileimage.get_height() / 2]

            curpos_on_field2 = self.map_to_field(curpos_on_field[0], curpos_on_field[1])

            self.labels[0].set_text("Image: " + settings[self.menu]["images"][self.selectedimage])
            self.labels[1].set_text(f"X: {curpos_on_field[0]}, Y: {curpos_on_field[1]}")

            self.surface.blit(self.tileimage, curpos)
            bp = pg.mouse.get_pressed(3)

            if bp[0] == 1 and mousp and (mousp2 and mousp1):
                mousp = False
            elif bp[0] == 1 and not mousp and (mousp2 and mousp1):
                sizepr = self.map_to_field(self.tileimage.get_width(), self.tileimage.get_height())
                self.field3.field.blit(self.tileimage, curpos_on_field)
                self.fieldadd.blit(self.field3.field, fieldpos)
                self.field2.field.blit(pg.transform.scale(self.tileimage, sizepr), curpos_on_field2)
            elif bp[0] == 0 and not mousp and (mousp2 and mousp1):
                self.fieldadd.fill(white)
                mousp = True
                self.renderfield()
            self.movemiddle(bp, pos)

    def map_to_field(self, x, y):
        return [x / ((len(self.data["GE"]) + self.ofsleft) * self.size) * self.field2.field.get_width(),
                y / ((len(self.data["GE"][0]) + self.ofstop) * self.size) * self.field2.field.get_height()]

    def rs(self):
        self.field3 = self.field2.copy()
        self.field3.field = pg.transform.scale(self.field2.field,
                                               [(len(self.data["GE"]) + self.ofsleft) * self.size,
                                                (len(self.data["GE"][0]) + self.ofstop) * self.size])
        self.field3.field.set_alpha(100)
        self.field3.field.set_colorkey(white)

    def renderfield(self):
        self.rs()
        super().renderfield()
        self.fieldadd = pg.transform.scale(self.fieldadd,
                                           [len(self.data["GE"]) * self.size, len(self.data["GE"][0]) * self.size])
        self.fieldadd.fill(white)

    def save(self):
        if self.data["path"] == "":
            level = asksaveasfilename(defaultextension="wep")
            self.data["level"] = os.path.basename(level)
            self.data["path"] = level
            self.data["dir"] = os.path.abspath(level)
            self.message = "save"
            lev = os.path.splitext(self.data["path"])[0] + ".png"
            pg.image.save(self.field2.field, lev)
        else:
            lev = os.path.splitext(self.data["path"])[0] + ".png"
            pg.image.save(self.field2.field, lev)

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
        self.data[self.menu]["flatness"] = self.flatness

    def fm(self):
        self.flatness -= 1
        self.data[self.menu]["flatness"] = self.flatness

    def lp(self):
        self.lightAngle += 1
        self.data[self.menu]["lightAngle"] = self.lightAngle

    def lm(self):
        self.lightAngle -= 1
        self.data[self.menu]["lightAngle"] = self.lightAngle

    def lightmod(self):
        if self.mode:
            self.inverse()

    def darkmod(self):
        if not self.mode:
            self.inverse()
