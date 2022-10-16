from menuclass import *
from lingotojson import *
import random

class FE(menu_with_field):
    def __init__(self, surface: pg.surface.Surface, data, items):
        self.menu = "FE"
        super().__init__(surface, data, "FE")
        self.items = items

        self.buttonslist = []

        self.currentcategory = 0
        self.currentindex = 0
        self.selectedeffect = 0
        self.paramindex = 0

        self.mpos = [0, 0]
        self.mmove = False

        self.innew = True # if you in new effects tab or in added effects tab

        self.buttonslist = [] # effects to be added
        self.buttonslist2 = [] # added effects
        self.params = [] # parameters of effects as buttons

        self.brushsize = 5

        self.init()
        self.makeparams()
        self.renderfield_all(rendersecond=True, items=self.items)
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
        cir = [self.buttonslist[self.currentindex].rect.x + 3,
               self.buttonslist[self.currentindex].rect.y + self.buttonslist[self.currentindex].rect.h / 2]

        cir2 = [self.buttonslist2[self.selectedeffect].rect.x + 3,
               self.buttonslist2[self.selectedeffect].rect.y + self.buttonslist2[self.selectedeffect].rect.h / 2]

        if self.innew:
            pg.draw.circle(self.surface, cursor, cir, self.buttonslist[self.currentindex].rect.h / 2)
            pg.draw.circle(self.surface, cursor2, cir2, self.buttonslist2[self.selectedeffect].rect.h / 2)
        else:
            pg.draw.circle(self.surface, cursor2, cir, self.buttonslist[self.currentindex].rect.h / 2)
            pg.draw.circle(self.surface, cursor, cir2, self.buttonslist2[self.selectedeffect].rect.h / 2)

        if self.field.rect.collidepoint(pg.mouse.get_pos()):
            pg.draw.circle(self.surface, cursor, pg.mouse.get_pos(), self.brushsize * self.size, 4)
            # cords = [math.floor(pg.mouse.get_pos()[0] / self.size) * self.size, math.floor(pg.mouse.get_pos()[1] / self.size) * self.size]
            # self.surface.blit(self.tools, pos, [curtool, graphics["tilesize"]])

            pos = [math.floor((pg.mouse.get_pos()[0] - self.field.rect.x) / self.size),
                   math.floor((pg.mouse.get_pos()[1] - self.field.rect.y) / self.size)]
            pos2 = [pos[0] * self.size + self.field.rect.x, pos[1] * self.size + self.field.rect.y]
            posoffset = [pos[0] - self.xoffset, pos[1] - self.yoffset]

            if posoffset != self.mpos:
                self.mpos = posoffset
                self.mmove = True

            bp = pg.mouse.get_pressed(3)

            if bp[0] == 1 and mousp and (mousp2 and mousp1):
                mousp = False
                self.mmove = True
            elif bp[0] == 1 and not mousp and (mousp2 and mousp1):
                if (0 <= posoffset[0] < len(self.data["GE"])) and (0 <= posoffset[1] < len(self.data["GE"][0])) and self.mmove:
                    self.paint(posoffset[0], posoffset[1], 1)
                    self.mmove = False
                    # pg.draw.rect(self.fieldadd, red, [posoffset[0] * self.size, posoffset[1] * self.size, self.size, self.size])
            elif bp[0] == 0 and not mousp and (mousp2 and mousp1):
                # self.fieldadd.fill(white)
                mousp = True
                self.renderfield()

            if bp[2] == 1 and mousp2 and (mousp and mousp1):
                mousp2 = False
                self.mmove = True
            elif bp[2] == 1 and not mousp2 and (mousp and mousp1):
                if (0 <= posoffset[0] < len(self.data["GE"])) and (0 <= posoffset[1] < len(self.data["GE"][0])) and self.mmove:
                    self.paint(posoffset[0], posoffset[1], -1)
            elif bp[2] == 0 and not mousp2 and (mousp and mousp1):
                mousp2 = True
                self.renderfield()

            self.movemiddle(bp, pos)

    def rebuttons(self):
        self.buttonslist = []
        btn2 = None
        for count, item in enumerate(effects[self.currentcategory]["efs"]):
            cat = pg.rect.Rect([settings[self.menu]["buttons"][settings[self.menu]["itemsposindex"]][1][0], 6, 22, 4])
            btn2 = widgets.button(self.surface, cat, settings["global"]["color"], effects[self.currentcategory]["nm"])

            rect = pg.rect.Rect([settings[self.menu]["buttons"][settings[self.menu]["itemsposindex"]][1][0], count * settings[self.menu]["itemsize"] + settings[self.menu]["buttons"][settings[self.menu]["itemsposindex"]][1][1] + settings[self.menu]["buttons"][settings[self.menu]["itemsposindex"]][1][3] + 4, 22, settings[self.menu]["itemsize"]])
            btn = widgets.button(self.surface, rect, pg.Color(settings["global"]["color2"]), item["nm"], onpress=self.addeffect)
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
        self.chtext()

    def makeparams(self):
        self.params = []
        self.chtext()
        if len(self.data["FE"]["effects"]) == 0:
            return
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

    def chtext(self):
        if len(self.data["FE"]["effects"]) > 0:
            self.labels[0].set_text(self.labels[0].originaltext % (self.data["FE"]["effects"][self.selectedeffect]["options"][self.paramindex][0], self.data["FE"]["effects"][self.selectedeffect]["options"][self.paramindex][2]))
            self.labels[1].set_text(self.labels[1].originaltext + self.data["FE"]["effects"][self.selectedeffect]["nm"])
            self.buttons[settings[self.menu]["currentparamindex"]].text = str(self.paramindex)
        else:
            self.labels[0].set_text("")
            self.labels[1].set_text("")
            self.buttons[settings[self.menu]["currentparamindex"]].text = "0"

    def changeparam(self, text): # "Delete", "Move Back", "Move Forth"
        match text:
            case "Delete":
                self.deleteeffect()
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
            if seed == -1:
                self.data["FE"]["effects"][self.selectedeffect]["options"][self.paramindex][2] = random.randint(0, 500)
            if 0 <= seed <= 500:
                print("Unvalid input!")
            self.data["FE"]["effects"][self.selectedeffect]["options"][self.paramindex][2] = seed
            return
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

    def nextcat(self):
        self.innew = True
        if self.currentcategory + 1 >= len(effects):
            self.currentcategory = 0
            self.rebuttons()
            return
        self.currentcategory += 1
        self.rebuttons()
    def prevcat(self):
        self.innew = True
        if self.currentcategory - 1 < 0:
            self.currentcategory = len(effects) - 1
            self.rebuttons()
            return
        self.currentcategory -= 1
        self.rebuttons()

    def resize(self):
        super().resize()
        if hasattr(self, "field"):
            for i in self.buttonslist:
                i.resize()
            for i in self.buttonslist2:
                i.resize()
            self.makeparams()

    def renderfield(self):
        self.fieldadd = pg.transform.scale(self.fieldadd,
                                           [len(self.data["GE"]) * self.size, len(self.data["GE"][0]) * self.size])
        self.fieldadd.fill(white)
        super().renderfield()
        self.rf3()
        self.makeparams()

    def rf3(self):
        if len(self.data["FE"]["effects"]) > 0:
            renderfield3(self.fieldmap, self.size, self.data["FE"]["effects"][self.selectedeffect]["mtrx"])

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
                self.renderfield_all(rendersecond=True, items=self.items)
            case "swichlayers_back":
                self.layer -= 1
                if self.layer < 0:
                    self.layer = 2
                self.mpos = 1
                self.renderfield_all(rendersecond=True, items=self.items)

    def deleteeffect(self):
        self.data["FE"]["effects"].pop(self.selectedeffect)
        self.selectedeffect = 0
        self.rebuttons()
        self.makeparams()

    def addordeleteselectedeffect(self):
        if self.innew:
            self.addeffect(self.buttonslist[self.currentindex].text)
            return
        self.deleteeffect()

    def addeffect(self, text):
        self.innew = True
        for cat in effects:
            for effect in cat["efs"]:
                if effect["nm"] == text:
                    ef = effect.copy()
                    mtrx = [[0 for _ in range(len(self.data["GE"][0]))] for _ in range(len(self.data["GE"]))]
                    ef["mtrx"] = mtrx
                    for n, i in enumerate(ef["options"]):
                        if i[0].lower() == "seed":
                            ef["options"][n][2] = random.randint(0, 500)
                    self.data["FE"]["effects"].append(ef.copy())
                    self.innew = False
                    self.selectedeffect = len(self.data["FE"]["effects"]) - 1
                    self.renderfield()
                    self.rebuttons()

    def selectmouseeffect(self):
        self.innew = False
        for indx, i in enumerate(self.buttonslist2):
            if i.onmouseover():
                self.selectedeffect = indx
                self.paramindex = 0
                self.renderfield()
                return

    def paint(self, x, y, st):
        currenteffect = self.data["FE"]["effects"][self.selectedeffect]["nm"]
        strength = 10 + (90 * self.findparampressed("str100"))
        if currenteffect in e["maxstr"]:
            strength = 10000

        for xp, xd in enumerate(self.data["FE"]["effects"][self.selectedeffect]['mtrx']):
            for yp, yd in enumerate(xd):
                val = yd
                dist = 1.0 - (pg.Vector2(xp, yp).distance_to(pg.Vector2(x, y)) / self.brushsize)
                if dist > 0:

                    val = min(max(val + strength * dist * st, 0), 100)

                    self.data["FE"]["effects"][self.selectedeffect]['mtrx'][xp][yp] = val

        self.rf3()

    def bsup(self):
        self.brushsize += 1

    def bsdown(self):
        if self.brushsize - 1 > 1:
            self.brushsize -= 1

    def innewtab(self):
        self.innew = True

    def notinnewtab(self):
        self.innew = False

    def scrl_up_new(self):
        self.innewtab()
        print(' do')
        self.currentindex -= 1
        if self.currentindex < 0:
            self.currentindex = len(effects[self.paramindex]["efs"]) - 1

    def scrl_up_menu(self):
        self.notinnewtab()
        self.selectedeffect -= 1
        if self.selectedeffect < 0:
            self.selectedeffect = len(self.data["FE"]["effects"]) - 1
        self.renderfield()

    def scrl_down_new(self):
        self.innewtab()
        self.currentindex += 1
        if self.currentindex > len(effects[self.paramindex]["efs"]) - 1:
            self.currentindex = 0

    def scrl_down_menu(self):
        self.notinnewtab()
        self.selectedeffect += 1
        if self.selectedeffect > len(self.data["FE"]["effects"]) - 1:
            self.selectedeffect = 0
        self.renderfield()

    def scrl_up(self):
        if self.innew:
            self.scrl_up_new()
            return
        self.scrl_up_menu()
    def scrl_down(self):
        if self.innew:
            self.scrl_down_new()
            return
        self.scrl_down_menu()
