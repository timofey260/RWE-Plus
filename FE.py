from menuclass import *
from lingotojson import *
import random


class FE(menu_with_field):
    def __init__(self, surface: pg.surface.Surface, data, items, props, propcolors):
        self.menu = "FE"
        super().__init__(surface, data, "FE", items, props, propcolors)

        self.buttonslist = []

        self.currentcategory = 0
        self.currentindex = 0
        self.selectedeffect = 0
        self.paramindex = 0
        
        self.matshow = False

        self.mpos = [0, 0]
        self.mmove = False

        self.innew = True # if you in new effects tab or in added effects tab

        self.buttonslist = [] # effects to be added
        self.buttonslist2 = [] # added effects
        self.params = [] # parameters of effects as buttons

        self.brushsize = 5

        self.copymode = False

        self.init()
        self.makeparams()
        self.rfa()
        self.rebuttons()
        self.blit()
        self.resize()

    def blit(self):
        pg.draw.rect(self.surface, settings["TE"]["menucolor"], pg.rect.Rect(self.buttonslist[:-1][0].xy,
                                                                             [self.buttonslist[:-1][0].rect.w,
                                                                              len(self.buttonslist[:-1]) *
                                                                              self.buttonslist[:-1][0].rect.h + 1]))
        ts = sum(pg.display.get_window_size()) // 120
        super().blit()
        for i in self.buttonslist:
            i.blitshadow()
        for i in self.buttonslist2:
            i.blitshadow()
        for i in self.params:
            i.blitshadow()
        self.buttonslist[-1].blit(sum(pg.display.get_window_size()) // 100)

        for i in self.buttonslist[:-1]:
            i.blit(ts)
        for i in self.buttonslist2:
            i.blit(ts)
        for i in self.params:
            i.blit()

        cir = [self.buttonslist[self.currentindex].rect.x + 3,
               self.buttonslist[self.currentindex].rect.y + self.buttonslist[self.currentindex].rect.h / 2]
        if self.innew:
            pg.draw.circle(self.surface, cursor, cir, self.buttonslist[self.currentindex].rect.h / 2)
        else:
            pg.draw.circle(self.surface, cursor2, cir, self.buttonslist[self.currentindex].rect.h / 2)
        if len(self.buttonslist2) > 0:
            cir2 = [self.buttonslist2[self.selectedeffect].rect.x + 3,
                    self.buttonslist2[self.selectedeffect].rect.y + self.buttonslist2[self.selectedeffect].rect.h / 2]

            if self.innew:
                pg.draw.circle(self.surface, cursor2, cir2, self.buttonslist2[self.selectedeffect].rect.h / 2)
            else:
                pg.draw.circle(self.surface, cursor, cir2, self.buttonslist2[self.selectedeffect].rect.h / 2)
        mpos = pg.Vector2(pg.mouse.get_pos())
        pos = [math.floor((mpos.x - self.field.rect.x) / self.size),
               math.floor((mpos.y - self.field.rect.y) / self.size)]
        bp = pg.mouse.get_pressed(3)

        if self.field.rect.collidepoint(mpos) and len(self.data["FE"]["effects"]) > 0:
            if not self.copymode:
                pg.draw.circle(self.surface, cursor, mpos, self.brushsize * self.size, 4)

            posoffset = [pos[0] - self.xoffset, pos[1] - self.yoffset]
            pos2 = [pos[0] * self.size + self.field.rect.x, pos[1] * self.size + self.field.rect.y]

            if posoffset != self.mpos:
                self.mpos = posoffset
                self.mmove = True

            if bp[0] == 1 and self.mousp and (self.mousp2 and self.mousp1):
                self.mousp = False
                self.mmove = True
                self.rectdata = [posoffset, [0, 0], pos2]
            elif bp[0] == 1 and not self.mousp and (self.mousp2 and self.mousp1):
                self.rectdata[1] = [posoffset[0] - self.rectdata[0][0], posoffset[1] - self.rectdata[0][1]]
                if (0 <= posoffset[0] < len(self.data["GE"])) and (0 <= posoffset[1] < len(self.data["GE"][0])) and self.mmove:
                    if not self.copymode:
                        self.paint(posoffset[0], posoffset[1], 1)
                    self.mmove = False
                if self.copymode:
                    rect = pg.Rect(
                        [self.rectdata[2], [pos2[0] - self.rectdata[2][0], pos2[1] - self.rectdata[2][1]]])
                    tx = f"{int(rect.w / image1size)}, {int(rect.h / image1size)}"
                    widgets.fastmts(self.surface, tx, *mpos, white)
                    pg.draw.rect(self.surface, blue, rect, 5)
            elif bp[0] == 0 and not self.mousp and (self.mousp2 and self.mousp1):
                if self.copymode:
                    data1 = self.data["FE"]["effects"][self.selectedeffect]["mtrx"][self.rectdata[0][0]:posoffset[0]]
                    data1 = [i[self.rectdata[0][1]:posoffset[1]] for i in data1]
                    pyperclip.copy(str(data1))
                    print("Copied!")
                self.updatehistory([["FE", "effects", self.selectedeffect, "mtrx"]])
                #self.detecthistory(["FE", "effects", self.selectedeffect, "mtrx"])
                self.mousp = True
                self.renderfield()

            if bp[2] == 1 and self.mousp2 and (self.mousp and self.mousp1):
                self.mousp2 = False
                self.mmove = True
            elif bp[2] == 1 and not self.mousp2 and (self.mousp and self.mousp1):
                if (0 <= posoffset[0] < len(self.data["GE"])) and (0 <= posoffset[1] < len(self.data["GE"][0])) and self.mmove:
                    if not self.copymode:
                        self.paint(posoffset[0], posoffset[1], -1)
                        self.mmove = False
            elif bp[2] == 0 and not self.mousp2 and (self.mousp and self.mousp1):
                self.mousp2 = True
                self.renderfield()

            self.movemiddle(bp, pos)
        for i in self.buttonslist:
            i.blittooltip()
        for i in self.buttonslist2:
            i.blittooltip()
        for i in self.buttons:
            i.blittooltip()

    def rebuttons(self):
        self.buttonslist = []
        self.matshow = False
        btn2 = None
        for count, item in enumerate(effects[self.currentcategory]["efs"]):
            cat = pg.rect.Rect(self.settings["catpos"])
            btn2 = widgets.button(self.surface, cat, settings["global"]["color"], effects[self.currentcategory]["nm"], onpress=self.cats,
                                  tooltip=self.returnkeytext("Select category(<[-changematshow]>)"))

            rect = pg.rect.Rect(self.settings["itempos"])
            rect = rect.move(0, rect.h * count)
            btn = widgets.button(self.surface, rect, pg.Color(settings["global"]["color2"]), item["nm"], onpress=self.addeffect)
            self.buttonslist.append(btn)
            count += 1
        if btn2 is not None:
            self.buttonslist.append(btn2)

        self.buttonslist2 = []
        for count, item in enumerate(self.data["FE"]["effects"]):
            rect = pg.rect.Rect(self.settings["itempos2"])
            rect = rect.move(0, rect.h * count)
            btn = widgets.button(self.surface, rect, pg.Color(settings["global"]["color2"]), item["nm"], onpress=self.selectmouseeffect)
            self.buttonslist2.append(btn)
            count += 1
        self.resize()
        self.chtext()

    def dublicate(self):
        self.data["FE"]["effects"].append(copy.deepcopy(self.data["FE"]["effects"][self.selectedeffect]))
        self.updatehistory([["FE", "effects"]])
        self.rebuttons()

    def copytool(self):
        self.copymode = not self.copymode

    def pastedata(self):
        try:
            geodata = eval(pyperclip.paste())
            if type(geodata) != list:
                return
            for xi, x in enumerate(geodata):
                for yi, y in enumerate(x):
                    xpos = -self.xoffset + xi
                    ypos = -self.yoffset + yi
                    if not self.canplaceit(xpos, ypos, xpos, ypos):
                        continue
                    self.data["FE"]["effects"][self.selectedeffect]["mtrx"][xpos][ypos] = y
            self.detecthistory(["FE", "effects", self.selectedeffect, "mtrx"])
            self.rfa()
        except:
            print("Error pasting data!")

    def cats(self):
        self.buttonslist = []
        self.settignslist = []
        self.matshow = True
        btn2 = None
        for count, item in enumerate(effects):
            cat = pg.rect.Rect(self.settings["catpos"])
            btn2 = widgets.button(self.surface, cat, settings["global"]["color"], "Categories",
                                  onpress=self.changematshow)
            rect = pg.rect.Rect(self.settings["itempos"])
            rect = rect.move(0, rect.h * count)
            col = item["color"]
            if col is None:
                col = gray
            if count == self.currentcategory:
                col = darkgray
            btn = widgets.button(self.surface, rect, col, item["nm"], onpress=self.selectcat)
            self.buttonslist.append(btn)
            count += 1
        if btn2 is not None:
            self.buttonslist.append(btn2)
        self.resize()

    def changematshow(self):
        if self.matshow:
            self.currentcategory = self.currentindex
            self.currentindex = 0
            self.rebuttons()
        else:
            self.currentindex = self.currentcategory
            self.innew = True
            self.cats()

    def selectcat(self, name):
        for indx, effect in enumerate(effects):
            if effect["nm"] == name:
                self.currentcategory = indx
                self.currentindex = 0
                self.rebuttons()
                return

    def makeparams(self):
        self.params = []
        self.chtext()
        if len(self.data["FE"]["effects"]) == 0:
            return
        ws = pg.display.get_window_size()
        addspace = self.settings["additionspace"] / 100 * ws[0]
        ppos = self.settings["paramspos"]

        if self.data["FE"]["effects"][self.selectedeffect]["options"][self.paramindex][0].lower() == "seed":
            rect = pg.Rect([ppos, self.settings["seedchange_size"]])
            btn = widgets.button(self.surface, rect, pg.Color(settings["global"]["color2"]), "Set seed",
                                 onpress=self.changeseed)
            btn.resize()
            self.params.append(btn)
            return

        for c, i in enumerate(self.data["FE"]["effects"][self.selectedeffect]["options"][self.paramindex][1]):
            w, h = fs(sum(pg.display.get_window_size()) // 70)[0].size(i)
            try:
                rect = pg.Rect(self.params[-1].rect.topright[0], ppos[1] / 100 * ws[1], w + addspace, h + addspace)
            except IndexError:
                rect = pg.Rect(ppos[0] / 100 * ws[0], ppos[1] / 100 * ws[1], w + addspace, h + addspace)
            btn = widgets.button(self.surface, rect, pg.Color(settings["global"]["color2"]), i, onpress=self.changeparam)
            self.params.append(btn)
        self.buttons[self.settings['currentparamindex']].set_text(str(self.paramindex))

    def chtext(self):
        if len(self.data["FE"]["effects"]) > 0:
            self.labels[0].set_text(self.labels[0].originaltext % (self.data["FE"]["effects"][self.selectedeffect]["options"][self.paramindex][0], self.data["FE"]["effects"][self.selectedeffect]["options"][self.paramindex][2]))
            self.labels[1].set_text(self.labels[1].originaltext + self.data["FE"]["effects"][self.selectedeffect]["nm"])
            self.buttons[self.settings["currentparamindex"]].set_text(str(self.paramindex))
        else:
            self.labels[0].set_text("")
            self.labels[1].set_text("")
            self.buttons[self.settings["currentparamindex"]].set_text("0")

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
                self.updatehistory([["FE"]])
                self.selectedeffect = se
                self.rebuttons()
                self.makeparams()
                return
            case "Move Forth":
                se = self.selectedeffect + 1
                if se < len(self.data["FE"]["effects"]):
                    self.data["FE"]["effects"].insert(se, self.data["FE"]["effects"].pop(self.selectedeffect))
                    self.updatehistory([["FE"]])
                    self.selectedeffect = se
                    self.rebuttons()
                    self.makeparams()
                return

        self.data["FE"]["effects"][self.selectedeffect]["options"][self.paramindex][2] = text
        self.updatehistory([["FE", "effects", self.selectedeffect, "options", self.paramindex, 2]])
        self.chtext()

    def changeseed(self):
        try:
            seed = self.askint("Enter seed")
            if seed == -1:
                self.data["FE"]["effects"][self.selectedeffect]["options"][self.paramindex][2] = random.randint(0, 500)
            if 0 <= seed <= 500:
                print("Seed changed!")
            self.data["FE"]["effects"][self.selectedeffect]["options"][self.paramindex][2] = seed
            self.updatehistory([["FE", "effects", self.selectedeffect, "options", self.paramindex, 2]])
            self.makeparams()
            return
        except ValueError:
            print("Invalid input!")

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
        self.currentindex = 0
        if self.currentcategory + 1 >= len(effects):
            self.currentcategory = 0
            self.rebuttons()
            return
        self.currentcategory += 1
        self.rebuttons()
    def prevcat(self):
        self.innew = True
        self.currentindex = 0
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
            fillcol = mixcol_empty
            if self.draweffects != 0:
                fillcol = pg.Color(mixcol_empty.r, mixcol_empty.g, mixcol_empty.b, 0)
            self.rendermatrix(self.fieldmap, self.size, self.data["FE"]["effects"][self.selectedeffect]["mtrx"], fillcol)

    def deleteeffect(self):
        try:
            self.data["FE"]["effects"].pop(self.selectedeffect)
            if self.draweffects > len(self.data['FE']['effects']):
                self.draweffects = 0
                self.rfa()
        except IndexError:
            print("No elements in list!")
        self.selectedeffect = 0
        self.updatehistory([["FE"]])
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
                    ef = copy.deepcopy(effect)
                    mtrx = [[0 for _ in range(len(self.data["GE"][0]))] for _ in range(len(self.data["GE"]))]
                    ef["mtrx"] = mtrx
                    for n, i in enumerate(ef["options"]):
                        if i[0].lower() == "seed":
                            ef["options"][n][2] = random.randint(0, 500)
                    self.data["FE"]["effects"].append(ef.copy())
                    self.innew = False
                    self.selectedeffect = len(self.data["FE"]["effects"]) - 1
                    self.updatehistory([["FE"]])
                    self.renderfield()
                    self.rebuttons()
                    return


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

                    if val == 100:
                        val = 100
                    self.data["FE"]["effects"][self.selectedeffect]['mtrx'][xp][yp] = round(val)

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
        self.currentindex -= 1
        if self.currentindex < 0:
            self.currentindex = len(self.buttonslist) - 2

    def scrl_up_menu(self):
        self.notinnewtab()
        self.selectedeffect -= 1
        if self.selectedeffect < 0:
            self.selectedeffect = len(self.data["FE"]["effects"]) - 1
        self.renderfield()

    def scrl_down_new(self):
        self.innewtab()
        self.currentindex += 1
        if self.currentindex > len(self.buttonslist) - 2:
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
