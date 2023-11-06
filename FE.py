from menuclass import *
from lingotojson import *
import random


class FE(MenuWithField):
    def __init__(self, process):
        self.menu = "FE"

        self.mpos = [0, 0]
        self.mmove = False

        self.innew = True # if you in new effects tab or in added effects tab
        self.effects: ItemData = process.manager.effects

        self.brushsize = 5

        self.copymode = False

        super().__init__(process, "FE")
        #self.fieldadd.set_colorkey(None)
        self.selector = widgets.Selector(self, self.effects, "s1", "effects.txt")
        self.activeeffects = widgets.Selector(self, self.generate_activeeffects(), "s2")
        self.paramsselector = widgets.Selector(self, self.generate_params(), "s3")

        self.selector.callback = self.selectorset
        self.selector.callbackafterchange = False
        self.paramsselector.callbackafterchange = False
        self.paramsselector.drawrect = False
        self.activeeffects.callback = self.activeeffectsset
        self.paramsselector.callback = self.paramscallback
        self.fieldadd.set_alpha(200)
        # self.makeparams()
        self.rfa()
        #self.rebuttons()
        self.blit()
        self.resize()
        self.chtext()

    def remakeparams(self):
        self.paramsselector.reload_data(self.generate_params())
        self.chtext()

    def remakeactive(self):
        self.activeeffects.reload_data(self.generate_activeeffects())
        self.remakeparams()

    def paramscallback(self, buttondata):
        self.paramsselector.setbybuttondata(buttondata)
        self.changeparam(buttondata["nm"])
        self.chtext()
        self.paramsselector.reload_data(self.generate_params(), False)

    def activeeffectsset(self, buttondata):
        self.notinnewtab()
        self.activeeffects.setbybuttondata(buttondata)
        self.remakeparams()
        self.activeeffects.reload_data(self.generate_activeeffects(), False)
        self.renderfield()

    def generate_params(self) -> ItemData:
        data = ItemData()
        # print(self.activeeffects.selecteditem)
        for i, option in enumerate(self.data["FE"]["effects"][self.activeeffects.selecteditem['param']]["options"]):
            items = []
            for opi, optionname in enumerate(option[1]):
                items.append({
                    "nm": optionname,
                    "color": darkgray if option[2] == optionname else gray,
                    "description": "",
                    "param": i,
                    "category": option[0],
                    "selected": option[2] == optionname
                })
            if option[0].lower() == "seed":
                items.append({
                    "nm": "Change seed",
                    "color": gray,
                    "description": "Click to change seed",
                    "param": i,
                    "category": option[0],
                    "selected": True
                })
            selectedi = str(option[2])
            data.append({"name": option[0], "color": gray, "items": items, "descvalue": selectedi})
        # print(data)
        return data

    def generate_activeeffects(self) -> ItemData:
        data = ItemData()
        items_in_cat = 0
        datacat = {"name": "1", "color": gray, "items": []}
        for i, effect in enumerate(self.data["FE"]["effects"]):
            foundeffect: dict = self.effects[effect["nm"]]
            appenddata = {
                "nm": effect["nm"],
                "color": gray,
                "param": i,
                "description": foundeffect["description"],
                "category": datacat["name"]
            }
            if foundeffect.get("preview", None) is not None:
                appenddata["preview"] = foundeffect["preview"]
            datacat["items"].append(appenddata)
            items_in_cat += 1
            if items_in_cat > self.settings["category_count"]:
                data.append(datacat)
                datacat = {"name": str(len(data) + 1), "color": gray, "items": []}
                items_in_cat = 0
        data.append(datacat)
        return data

    def selectorset(self, buttondata):
        self.addeffect(buttondata["nm"])
        self.selector.setbyname(buttondata["nm"])

    def blit(self):
        # super().blit()
        self.selector.blit()
        self.activeeffects.blit()
        self.paramsselector.blit()

        self.activeeffects.cursorcolor = blue if self.innew else red
        self.selector.cursorcolor = red if self.innew else blue
        mpos = pg.Vector2(pg.mouse.get_pos())
        bp = self.getmouse
        super().blit()
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
        self.selector.blittooltip()
        self.paramsselector.blittooltip()
        self.activeeffects.blittooltip()

    def geteffect(self, text):
        for cat in self.effects:
            for c, i in enumerate(cat["items"]):
                if i["nm"] == text:
                    return i
        return None

    def duplicate(self):
        self.historyappend(["FE", "effects"], copy.deepcopy(self.data["FE"]["effects"][self.selectedeffect]))
        self.updatehistory()

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
                    self.changedata(["FE", "effects", self.selectedeffect, "mtrx", xpos, ypos], y)
                    # self.data["FE"]["effects"][self.selectedeffect]["mtrx"][xpos][ypos] = y
            self.detecthistory(["FE", "effects", self.selectedeffect, "mtrx"])
            self.rfa()
        except:
            print("Error pasting data!")

    def chtext(self):
        if len(self.data["FE"]["effects"]) > 0:
            self.labels[0].set_text(self.labels[0].originaltext + self.data["FE"]["effects"][self.selectedeffect]["nm"])
            self.buttons[self.settings["currentparamindex"]].set_text(str(self.paramindex))
        else:
            self.labels[0].set_text("")
            self.buttons[self.settings["currentparamindex"]].set_text("0")

    def changeparam(self, text: str): # "Delete", "Move Back", "Move Forth"
        match text.lower():
            case "delete":
                self.deleteeffect()
                return
            case "move back":
                se = self.selectedeffect - 1
                if se < 0:
                    se = 0
                self.historymove(["FE", "effects"], self.selectedeffect, se)
                # self.data["FE"]["effects"].insert(se, self.data["FE"]["effects"].pop(self.selectedeffect))
                self.updatehistory()
                self.activeeffects.currentitem = se
                self.remakeactive()
                self.renderer.rerendereffect()
                return
            case "move forth":
                se = self.selectedeffect + 1
                if se < len(self.data["FE"]["effects"]):
                    self.historymove(["FE", "effects"], self.selectedeffect, se)
                    # self.data["FE"]["effects"].insert(se, self.data["FE"]["effects"].pop(self.selectedeffect))
                    self.updatehistory()
                    self.activeeffects.currentitem = se
                    self.remakeactive()
                    self.renderer.rerendereffect()
                return
            case "change seed":
                self.changeseed()
                return

        # self.data["FE"]["effects"][self.selectedeffect]["options"][self.paramsselector.currentitem][2] = text
        self.changedata(["FE", "effects", self.selectedeffect, "options", self.paramsselector.currentcategory, 2], text)
        self.updatehistory()
        self.chtext()

    def changeseed(self):
        try:
            value = self.askint("Enter velue(type -1 for random)", False)
            if value is None:
                print("Abort")
            print(value)
            if value == -1:
                self.changedata(["FE", "effects", self.selectedeffect, "options", self.paramindex, 2], random.randint(0, 500))
                # self.data["FE"]["effects"][self.selectedeffect]["options"][self.paramindex][2] = random.randint(0, 500)
            if 0 <= value <= 500:
                print("Seed changed!")
            # self.data["FE"]["effects"][self.selectedeffect]["options"][self.paramindex][2] = value
            self.changedata(["FE", "effects", self.selectedeffect, "options", self.paramindex, 2], value)
            self.updatehistory()
            self.chtext()
            self.paramsselector.data = self.generate_params()
            return
        except ValueError:
            print("Invalid input!")

    def findeffect(self):
        nd = {}
        for cat in self.effects:
            for item in cat["items"]:
                nd[item["nm"]] = cat["name"]
        name = self.find(nd, "Select a prop")
        if name is None:
            return
        self.addeffect(name)

    def prevparam(self):
        self.paramsselector.left()
        self.chtext()

    def nextparam(self):
        self.paramsselector.right()
        self.chtext()

    def nextcat(self):
        self.innew = True
        self.selector.right()

    def prevcat(self):
        self.innew = True
        self.selector.left()

    def resize(self):
        super().resize()
        if hasattr(self, "field"):
            self.selector.resize()
            self.activeeffects.resize()
            self.paramsselector.resize()

    def renderfield(self):
        super().renderfield()
        self.fieldadd.set_alpha(200)
        self.rf3()
        self.recaption()
        #if hasattr(self, "selector"):
        #    self.remakeactive()

    def rf3(self):
        if len(self.data["FE"]["effects"]) > 0 and hasattr(self, "selector"):
            fillcol = mixcol_empty
            if self.draweffects != 0:
                fillcol = pg.Color(mixcol_empty.r, mixcol_empty.g, mixcol_empty.b, 0)
            #self.fieldadd.fill(white)
            self.rendermatrix(self.fieldadd, self.size, self.data["FE"]["effects"][self.selectedeffect]["mtrx"], fillcol)

    def deleteeffect(self):
        try:
            self.historypop(["FE", "effects"], deepcopy(self.selectedeffect))
            # self.data["FE"]["effects"].pop(self.selectedeffect)
            if self.draweffects > len(self.data['FE']['effects']):
                self.draweffects = 0
                self.rfa()
        except IndexError:
            print("No elements in list!")
        self.activeeffects.currentitem = 0
        self.paramsselector.currentitem = 0
        self.updatehistory()
        self.remakeactive()

    def addordeleteselectedeffect(self):
        if self.innew:
            self.addeffect(self.selector.selecteditem["nm"]) #TODO fix this
            return
        self.deleteeffect()

    def addeffect(self, text):
        self.innew = True
        for cat in self.effects:
            for effect in cat["items"]:
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
                    self.historyappend(["FE", "effects"], ef.copy())
                    # self.data["FE"]["effects"].append(ef.copy())
                    self.innew = False
                    self.activeeffects.currentitem = len(self.data["FE"]["effects"]) - 1
                    self.recaption()
                    self.updatehistory()
                    self.renderfield()
                    self.remakeactive()
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
                    self.changedata(["FE", "effects", self.selectedeffect, 'mtrx', xp, yp], round(val))
                    # self.data["FE"]["effects"][self.selectedeffect]['mtrx'][xp][yp] = round(val)

        self.rf3()

    def bsup(self):
        self.brushsize += 1

    def bsdown(self):
        self.brushsize = widgets.restrict(self.brushsize, 1, bignum)

    def innewtab(self):
        self.innew = True

    def notinnewtab(self):
        self.innew = False

    def scrl_up_new(self):
        self.innewtab()
        self.selector.up()

    def scrl_up_menu(self):
        self.notinnewtab()
        self.activeeffects.up()
        self.renderfield()

    def scrl_down_new(self):
        self.innewtab()
        self.selector.down()

    def scrl_down_menu(self):
        self.notinnewtab()
        self.activeeffects.down()
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

    def onundo(self):
        self.remakeactive()

    def onredo(self):
        self.remakeactive()

    @property
    def touchesanything(self):
        return super().touchesanything or getattr(self, "activeeffects").touchesanything \
                or getattr(self, "paramsselector").touchesanything

    @property
    def selectedeffect(self):
        return self.activeeffects.selecteditem["param"]

    @property
    def paramindex(self):
        return self.paramsselector.selecteditem["param"]

    @property
    def custom_info(self):
        try:
            if hasattr(self, "selector"):
                return f"{super().custom_info} | Selected effect: {self.data['FE']['effects'][self.selectedeffect]['nm']}[{self.selectedeffect}]"
            else:
                return super().custom_info()
        except TypeError:
            return super().custom_info
        except IndexError:
            return super().custom_info
