from menuclass import *
from lingotojson import *
import random


class FE(MenuWithField):
    def __init__(self, surface: pg.surface.Surface, renderer):
        self.menu = "FE"

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

        super().__init__(surface, "FE", renderer)
        #self.fieldadd.set_colorkey(None)
        self.selector = widgets.Selector(surface, self, self.props, "s1", "props.txt")
        self.fieldadd.set_alpha(200)
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

        for i in self.params:
            i.blit()
        for i in self.buttonslist[:-1]:
            i.blit(ts)
            if i.onmouseover():
                effect = self.geteffect(i.text)
                if effect is not None and effect.get("preview"):
                    self.surface.blit(effect["preview"], i.rect.bottomright)
        for i in self.buttonslist2:
            i.blit(ts)
            if i.onmouseover():
                effect = self.geteffect(i.text)
                if effect is not None and effect.get("preview"):
                    if effect["preview"].get_height() + i.rect.y > self.surface.get_height():
                        self.surface.blit(effect["preview"], [i.rect.x + i.rect.w,
                                                              self.surface.get_height()-effect["preview"].get_height()])
                    else:
                        self.surface.blit(effect["preview"], i.rect.bottomright)

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
        bp = self.getmouse

        if self.onfield and len(self.data["FE"]["effects"]) > 0:
            if not self.copymode:
                pg.draw.circle(self.surface, cursor, mpos, self.brushsize * self.size, 4)

            posoffset = self.posoffset
            pos2 = self.pos2

            if posoffset != self.mpos:
                self.mpos = posoffset
                self.mmove = True

            if bp[0] == 1 and self.mousp and (self.mousp2 and self.mousp1):
                self.mousp = False
                self.mmove = True
                self.rectdata = [posoffset, pg.Vector2(0, 0), pos2]
            elif bp[0] == 1 and not self.mousp and (self.mousp2 and self.mousp1):
                self.rectdata[1] = posoffset - self.rectdata[0]
                if (0 <= posoffset.x < self.levelwidth) and (0 <= posoffset.y < self.levelheight) and self.mmove:
                    if not self.copymode:
                        self.paint(posoffset.x, posoffset.y, 1)
                    self.mmove = False
                if self.copymode:
                    rect = self.vec2rect(self.rectdata[2], pos2)
                    tx = f"{int(rect.w / self.size)}, {int(rect.h / self.size)}"
                    widgets.fastmts(self.surface, tx, *mpos, white)
                    pg.draw.rect(self.surface, blue, rect, 5)
            elif bp[0] == 0 and not self.mousp and (self.mousp2 and self.mousp1):
                rect = self.vec2rect(self.rectdata[0], posoffset)
                if self.copymode:
                    data1 = self.data["FE"]["effects"][self.selectedeffect]["mtrx"][rect.x:rect.w + rect.x]
                    data1 = [i[rect.y:rect.w + rect.y] for i in data1]
                    pyperclip.copy(str(data1))
                    print("Copied!")
                self.updatehistory()
                #self.detecthistory(["FE", "effects", self.selectedeffect, "mtrx"])
                self.mousp = True
                self.renderfield()
                self.renderer.rerendereffect()

            if bp[2] == 1 and self.mousp2 and (self.mousp and self.mousp1):
                self.mousp2 = False
                self.mmove = True
            elif bp[2] == 1 and not self.mousp2 and (self.mousp and self.mousp1):
                if (0 <= posoffset[0] < self.levelwidth) and (0 <= posoffset[1] < self.levelheight) and self.mmove:
                    if not self.copymode:
                        self.paint(posoffset[0], posoffset[1], -1)
                        self.mmove = False
            elif bp[2] == 0 and not self.mousp2 and (self.mousp and self.mousp1):
                self.updatehistory()
                self.mousp2 = True
                self.renderfield()
                self.renderer.rerendereffect()

            self.movemiddle(bp)
        for i in self.buttonslist:
            i.blittooltip()
        for i in self.buttonslist2:
            i.blittooltip()
        for i in self.buttons:
            i.blittooltip()

    def geteffect(self, text):
        for cat in effects:
            for c, i in enumerate(cat["efs"]):
                if i["nm"] == text:
                    return i
        return None

    def rebuttons(self):
        self.buttonslist = []
        self.matshow = False
        btn2 = None
        for count, item in enumerate(effects[self.currentcategory]["efs"]):
            cat = pg.rect.Rect(self.settings["catpos"])
            btn2 = widgets.Button(self.surface, cat, settings["global"]["color"], effects[self.currentcategory]["nm"], onpress=self.cats,
                                  tooltip=self.returnkeytext("Select category(<[-changematshow]>)"))

            rect = pg.rect.Rect(self.settings["itempos"])
            rect = rect.move(0, rect.h * count)
            btn = widgets.Button(self.surface, rect, pg.Color(settings["global"]["color2"]), item["nm"], onpress=self.addeffect)
            self.buttonslist.append(btn)
        if btn2 is not None:
            self.buttonslist.append(btn2)

        self.buttonslist2 = []
        #instead of scroll
        split2 = self.settings["itempos2"][1] + self.settings["itempos2"][3] * len(self.data["FE"]["effects"]) >= 100
        count2 = 0
        for count, item in enumerate(self.data["FE"]["effects"]):
            rect = pg.rect.Rect(self.settings["itempos2"])
            rect = rect.move(0, rect.h * count)
            if rect.y >= 100 and split2:
                rect = rect.move(rect.width / 2, 0)
                rect.y = self.settings["itempos2"][1] + self.settings["itempos2"][3] * count2
                count2 += 1
            if split2:
                rect.width = rect.width / 2
            btn = widgets.Button(self.surface, rect, pg.Color(settings["global"]["color2"]), item["nm"], onpress=self.selectmouseeffect)
            self.buttonslist2.append(btn)
        self.resize()
        self.chtext()

    def duplicate(self):
        self.data["FE"]["effects"].append(copy.deepcopy(self.data["FE"]["effects"][self.selectedeffect]))
        self.updatehistory()
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
                    pa = pg.Vector2(0, 0)
                    if self.field.rect.collidepoint(pg.mouse.get_pos()):
                        pa = self.pos
                    xpos = -self.xoffset + xi + int(pa.x)
                    ypos = -self.yoffset + yi + int(pa.y)
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
            btn2 = widgets.Button(self.surface, cat, settings["global"]["color"], "Categories",
                                  onpress=self.changematshow)
            rect = pg.rect.Rect(self.settings["itempos"])
            rect = rect.move(0, rect.h * count)
            col = item["color"]
            if col is None:
                col = gray
            if count == self.currentcategory:
                col = darkgray
            btn = widgets.Button(self.surface, rect, col, item["nm"], onpress=self.selectcat)
            self.buttonslist.append(btn)
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

        if len(self.data["FE"]["effects"][self.selectedeffect]["options"][self.paramindex][1]) < 1:
            rect = pg.Rect([ppos, self.settings["seedchange_size"]])
            btn = widgets.Button(self.surface, rect, pg.Color(settings["global"]["color2"]), "Set seed",
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
            btn = widgets.Button(self.surface, rect, pg.Color(settings["global"]["color2"]), i, onpress=self.changeparam)
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
                self.updatehistory()
                self.selectedeffect = se
                self.rebuttons()
                self.makeparams()
                self.renderer.rerendereffect()
                return
            case "Move Forth":
                se = self.selectedeffect + 1
                if se < len(self.data["FE"]["effects"]):
                    self.data["FE"]["effects"].insert(se, self.data["FE"]["effects"].pop(self.selectedeffect))
                    self.updatehistory()
                    self.selectedeffect = se
                    self.rebuttons()
                    self.makeparams()
                    self.renderer.rerendereffect()
                return

        self.data["FE"]["effects"][self.selectedeffect]["options"][self.paramindex][2] = text
        self.updatehistory()
        self.chtext()

    def changeseed(self):
        try:
            value = self.askint("Enter velue(type -1 for random)", False)
            if value == -1:
                self.data["FE"]["effects"][self.selectedeffect]["options"][self.paramindex][2] = random.randint(0, 500)
            if 0 <= value <= 500:
                print("Seed changed!")
            self.data["FE"]["effects"][self.selectedeffect]["options"][self.paramindex][2] = value
            self.updatehistory()
            self.makeparams()
            return
        except ValueError:
            print("Invalid input!")

    def findeffect(self):
        nd = {}
        for cat in effects:
            for item in cat["efs"]:
                nd[item["nm"]] = cat["nm"]
        name = self.find(nd, "Select a prop")
        if name is None:
            return
        self.addeffect(name)

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
        super().renderfield()
        self.fieldadd.set_alpha(200)
        self.rf3()
        self.recaption()
        self.makeparams()

    def rf3(self):
        if len(self.data["FE"]["effects"]) > 0:
            fillcol = mixcol_empty
            if self.draweffects != 0:
                fillcol = pg.Color(mixcol_empty.r, mixcol_empty.g, mixcol_empty.b, 0)
            #self.fieldadd.fill(white)
            self.rendermatrix(self.fieldadd, self.size, self.data["FE"]["effects"][self.selectedeffect]["mtrx"], fillcol)

    def deleteeffect(self):
        try:
            self.data["FE"]["effects"].pop(self.selectedeffect)
            if self.draweffects > len(self.data['FE']['effects']):
                self.draweffects = 0
                self.rfa()
        except IndexError:
            print("No elements in list!")
        self.selectedeffect = 0
        self.paramindex = 0
        self.updatehistory()
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
                    image = effect.get("preview")
                    if image:
                        del effect["preview"]
                        ef = copy.deepcopy(effect)
                        effect["preview"] = image
                    else:
                        ef = copy.deepcopy(effect)
                    mtrx = [[0 for _ in range(self.levelheight)] for _ in range(self.levelwidth)]
                    ef["mtrx"] = mtrx
                    for n, i in enumerate(ef["options"]):
                        if i[0].lower() == "seed":
                            ef["options"][n][2] = random.randint(0, 500)
                    self.data["FE"]["effects"].append(ef.copy())
                    self.innew = False
                    self.selectedeffect = len(self.data["FE"]["effects"]) - 1
                    self.recaption()
                    self.updatehistory()
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
        if self.brushsize - 1 > 0:
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

    @property
    def custom_info(self):
        try:
            return f"{super().custom_info} | Selected effect: {self.data['FE']['effects'][self.selectedeffect]['nm']}[{self.selectedeffect}]"
        except TypeError:
            return super().custom_info
        except IndexError:
            return super().custom_info
