from menuclass import *
from lingotojson import *


class FE(menu):

    def __init__(self, surface: pg.surface.Surface, data, items):
        self.menu = "FE"
        self.surface = surface
        self.field = widgets.window(self.surface, settings["FE"]["d1"])
        self.btiles = data["EX2"]["extraTiles"]
        self.data = data

        self.fieldmap = self.field.field

        self.fieldadd = self.fieldmap
        self.fieldadd.fill(white)
        self.fieldadd.set_colorkey(white)

        self.xoffset = 0
        self.yoffset = 0
        self.size = settings["TE"]["cellsize"]

        self.message = ''

        self.rectdata = [[0, 0], [0, 0], [0, 0]]
        self.items = items

        self.buttonslist = []

        self.currentcategory = 0
        self.currentindex = 0
        self.selectedeffect = 0
        self.paramindex = 0

        self.layer = 0
        self.mpos = [0, 0]

        self.innew = True # if you in new effects tab or in added effects tab

        self.buttonslist = [] # effects to be added
        self.buttonslist2 = [] # added effects
        self.params = [] # parameters of effects as buttons

        self.init()
        self.makeparams()
        self.renderfield()
        self.rebuttons()
        self.blit()
        self.resize()

    def blit(self):
        global mousp, mousp2, mousp1
        self.drawmap()

        self.buttonslist[-1].blit(sum(pg.display.get_window_size()) // 100)
        pg.draw.rect(self.surface, settings["TE"]["menucolor"], pg.rect.Rect(self.buttonslist[:-1][0].xy,
                                                                             [self.buttonslist[:-1][0].rect.w,
                                                                              len(self.buttonslist[:-1]) *
                                                                              self.buttonslist[:-1][0].rect.h + 1]))
        ts = sum(pg.display.get_window_size()) // 120
        for i in self.buttonslist[:-1]:
            i.blit(ts)
        for i in self.buttonslist2:
            i.blit(ts)
        for i in self.params:
            i.blit()
        super().blit()
        if self.field.rect.collidepoint(pg.mouse.get_pos()):
            pg.draw.circle(self.surface, cursor, pg.mouse.get_pos(), 120, 4)
            # cords = [math.floor(pg.mouse.get_pos()[0] / self.size) * self.size, math.floor(pg.mouse.get_pos()[1] / self.size) * self.size]
            # self.surface.blit(self.tools, pos, [curtool, graphics["tilesize"]])

            pos = [math.floor((pg.mouse.get_pos()[0] - self.field.rect.x) / self.size),
                   math.floor((pg.mouse.get_pos()[1] - self.field.rect.y) / self.size)]
            pos2 = [pos[0] * self.size + self.field.rect.x, pos[1] * self.size + self.field.rect.y]
            posoffset = [pos[0] - self.xoffset, pos[1] - self.yoffset]

            bp = pg.mouse.get_pressed(3)

            self.movemiddle(bp, pos)

    def rebuttons(self):
        self.buttonslist = []
        btn2 = None
        for count, item in enumerate(effects[self.currentcategory]["efs"]):
            # rect = pg.rect.Rect([0, count * settings[self.menu]["itemsize"], self.field2.field.get_width(), settings[self.menu]["itemsize"]])
            # rect = pg.rect.Rect(0, 0, 100, 10)
            cat = pg.rect.Rect([settings[self.menu]["buttons"][settings[self.menu]["itemsposindex"]][1][0], 6, 22, 4])
            btn2 = widgets.button(self.surface, cat, settings["global"]["color"], effects[self.currentcategory]["nm"])

            rect = pg.rect.Rect([settings[self.menu]["buttons"][settings[self.menu]["itemsposindex"]][1][0], count * settings[self.menu]["itemsize"] + settings[self.menu]["buttons"][settings[self.menu]["itemsposindex"]][1][1] + settings[self.menu]["buttons"][settings[self.menu]["itemsposindex"]][1][3] + 4, 22, settings[self.menu]["itemsize"]])
            btn = widgets.button(self.surface, rect, pg.Color(settings["global"]["color2"]), item["nm"], onpress=self.addmouseeffect)
            self.buttonslist.append(btn)
            count += 1
        if btn2 is not None:
            self.buttonslist.append(btn2)

        self.buttonslist2 = []
        for count, item in enumerate(self.data["FE"]["effects"]):
            # rect = pg.rect.Rect([0, count * settings[self.menu]["itemsize"], self.field2.field.get_width(), settings[self.menu]["itemsize"]])
            # rect = pg.rect.Rect(0, 0, 100, 10)

            rect = pg.rect.Rect([settings[self.menu]["buttons"][settings[self.menu]["itemsposindex2"]][1][0], count * settings[self.menu]["itemsize"] + settings[self.menu]["buttons"][settings[self.menu]["itemsposindex2"]][1][1] + settings[self.menu]["buttons"][settings[self.menu]["itemsposindex2"]][1][3], 22, settings[self.menu]["itemsize"]])
            btn = widgets.button(self.surface, rect, pg.Color(settings["global"]["color2"]), item["nm"], onpress=self.selectmouseeffect)
            self.buttonslist2.append(btn)
            count += 1
        self.resize()

    def makeparams(self):
        self.params = []
        ws = pg.display.get_window_size()
        addspace = settings[self.menu]["additionspace"] / 100 * ws[0]
        ppos = settings[self.menu]["paramspos"]

        if self.data["FE"]["effects"][self.selectedeffect]["options"][self.paramindex][0].lower() == "seed":
            rect = pg.Rect([ppos, settings[self.menu]["seedchange_size"]])
            btn = widgets.button(self.surface, rect, pg.Color(settings["global"]["color2"]), "Set seed",
                                 onpress=self.changeseed)
            btn.resize()
            self.params.append(btn)
            return

        for c, i in enumerate(self.data["FE"]["effects"][self.selectedeffect]["options"][self.paramindex][1]):
            w, h = fs(sum(pg.display.get_window_size()) // 70).size(i)
            try:
                rect = pg.Rect(self.params[-1].rect.topright[0], ppos[1] / 100 * ws[1], w + addspace, h + addspace)
            except IndexError:
                rect = pg.Rect(ppos[0] / 100 * ws[0], ppos[1] / 100 * ws[1], w + addspace, h + addspace)
            btn = widgets.button(self.surface, rect, pg.Color(settings["global"]["color2"]), i, onpress=self.changeparam)
            self.params.append(btn)
        self.buttons[settings[self.menu]['currentparamindex']].text = str(self.paramindex)
        self.chtext()

    def chtext(self):
        self.labels[0].set_text(self.labels[0].originaltext % (self.data["FE"]["effects"][self.selectedeffect]["options"][self.paramindex][0], self.data["FE"]["effects"][self.selectedeffect]["options"][self.paramindex][2]))

    def changeparam(self, text): # "Delete", "Move Back", "Move Forth"
        match text:
            case "Delete":
                self.data["FE"]["effects"].pop(self.selectedeffect)
                self.selectedeffect = 0
                self.rebuttons()
                self.makeparams()
                return
            case "Move Back":
                se = self.selectedeffect - 1
                if se < 0:
                    se = 0
                self.data["FE"]["effects"].insert(se, self.data["FE"]["effects"].pop(self.selectedeffect))
                self.selectedeffect = se
                self.rebuttons()
                self.makeparams()
                return
            case "Move Forth":
                se = self.selectedeffect + 1
                if se < len(self.data["FE"]["effects"]):
                    self.data["FE"]["effects"].insert(se, self.data["FE"]["effects"].pop(self.selectedeffect))
                    self.selectedeffect = se
                    self.rebuttons()
                    self.makeparams()
                return

        self.data["FE"]["effects"][self.selectedeffect]["options"][self.paramindex][2] = text
        self.chtext()

    def changeseed(self):
        try:
            seed = int(input("Enter seed: "))
            self.data["FE"]["effects"][self.selectedeffect]["options"][self.paramindex][2] = seed
        except ValueError:
            print("Unvalid input!")

    def prevparam(self):
        if self.paramindex - 1 >= 0:
            self.paramindex -= 1
        self.makeparams()

    def nextparam(self):
        if self.paramindex + 1 < len(self.data["FE"]["effects"][self.selectedeffect]["options"]):
            self.paramindex += 1
        self.makeparams()

    def resize(self):
        super().resize()
        self.field.resize()
        for i in self.buttonslist:
            i.resize()
        for i in self.buttonslist2:
            i.resize()
        self.renderfield()
        self.makeparams()

    def renderfield(self):
        self.fieldmap = pg.surface.Surface([len(self.data["GE"]) * self.size, len(self.data["GE"][0]) * self.size])
        self.fieldadd = pg.transform.scale(self.fieldadd,
                                           [len(self.data["GE"]) * self.size, len(self.data["GE"][0]) * self.size])
        self.fieldadd.fill(white)
        renderfield(self.fieldmap, self.size, self.layer, self.data["GE"])
        renderfield2(self.fieldmap, self.size, self.layer, self.data, self.items)
        if len(self.data["FE"]["effects"]) > 0:
            renderfield3(self.fieldmap, self.size, self.data["FE"]["effects"][self.selectedeffect]["mtrx"])
        self.makeparams()

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
            case "swichlayers":
                self.layer = (self.layer + 1) % 3
                self.mpos = 1
                self.renderfield()
            case "swichlayers_back":
                self.layer -= 1
                if self.layer < 0:
                    self.layer = 2
                self.mpos = 1
                self.renderfield()

    def addeffect(self, effect):
        self.innew = True

    def addmouseeffect(self):
        pass

    def selectmouseeffect(self):
        self.innew = False
        for indx, i in enumerate(self.buttonslist2):
            if i.onmouseover():
                self.selectedeffect = indx
                self.paramindex = 0
                self.renderfield()
                return