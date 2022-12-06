from menuclass import *
import cv2
import numpy as np
import random as rnd


def quadsize(quad):
    mostleft = bignum
    mostright = 0
    mosttop = bignum
    mostbottom = 0
    for q in quad:
        x, y = q
        if x < mostleft:
            mostleft = x
        if x > mostright:
            mostright = x

        if y < mosttop:
            mosttop = y
        if y > mostbottom:
            mostbottom = y
    ww = round(mostright - mostleft)
    wh = round(mostbottom - mosttop)
    return ww, wh, [mostleft, mosttop, mostright, mostbottom]


def quadtransform(quads, image: pg.Surface):
    ww, wh, mosts = quadsize(quads)

    colkey = image.get_colorkey()
    view = pg.surfarray.array3d(image)
    view = view.transpose([1, 0, 2])

    img = cv2.cvtColor(view, cv2.COLOR_RGB2RGBA) # NOQA
    ws, hs = img.shape[1::-1]
    pts1 = np.float32([[0, 0], [ws, 0],
                       [ws, hs], [0, hs]])
    q2 = []
    for q in quads:
        q2.append([q[0] - mosts[0], q[1] - mosts[1]])

    pts2 = np.float32(q2)
    persp = cv2.getPerspectiveTransform(pts1, pts2) # NOQA
    result = cv2.warpPerspective(img, persp, (ww, wh)) # NOQA

    img = pg.image.frombuffer(result.tostring(), result.shape[1::-1], "RGBA")
    img.set_colorkey(colkey)

    return [img, mosts[0], mosts[1], ww, wh]


class PE(menu_with_field):
    def __init__(self, surface: pg.surface.Surface, data, props, propcolors):
        self.menu = "PE"

        self.props = props
        self.propcolors = propcolors

        self.reset_settings()

        self.buttonslist = []
        self.settignslist = []

        self.currentcategory = 0
        self.itemindx = 0

        self.depth = 0

        self.selectedprop = self.props[list(self.props.keys())[self.currentcategory]][0]
        self.selectedimage: pg.Surface = self.selectedprop["images"][0]
        self.notes = []

        self.helds = [False, False, False, False]
        self.helppoins = pg.Vector2(0, 0)
        self.helppoins2 = pg.Vector2(0, 0)

        super().__init__(surface, data, "PE")
        self.setprop(self.props[list(self.props.keys())[self.currentcategory]][0]["nm"])
        self.init()
        self.resize()
        self.rebuttons()
        self.rfa()

    def renderfield(self):
        super().renderfield()
        self.updateproptransform()

    def rebuttons(self):
        self.buttonslist = []
        btn2 = None
        itemcat = list(self.props.keys())[self.currentcategory]
        for count, item in enumerate(self.props[itemcat]):
            # rect = pg.rect.Rect([0, count * self.settings["itemsize"], self.field2.field.get_width(), self.settings["itemsize"]])
            # rect = pg.rect.Rect(0, 0, 100, 10)
            cat = pg.rect.Rect([self.settings["buttons"][self.settings["itemsposindex"]][1][0], 6, 22, 4])
            btn2 = widgets.button(self.surface, cat, settings["global"]["color"], itemcat)
            rect = pg.rect.Rect([self.settings["buttons"][self.settings["itemsposindex"]][1][0],
                                 count * self.settings["itemsizey"] +
                                 self.settings["buttons"][self.settings["itemsposindex"]][1][1] +
                                 self.settings["buttons"][self.settings["itemsposindex"]][1][3] + 4,
                                 self.settings["itemsizex"],
                                 self.settings["itemsizey"]])
            btn = widgets.button(self.surface, rect, item["color"], item["nm"], onpress=self.setprop)
            self.buttonslist.append(btn)
        if btn2 is not None:
            self.buttonslist.append(btn2)
        if self.itemindx > len(self.props[itemcat]):
            self.itemindx = 0
        self.resize()
        self.settingsupdate()

    def settingsupdate(self):
        self.settignslist = []
        for count, item in enumerate(self.prop_settings.items()):
            name, val = item
            rect = pg.rect.Rect([self.settings["buttons"][self.settings["settingsposindex"]][1][0],
                                 count * self.settings["settingssizey"] +
                                 self.settings["buttons"][self.settings["settingsposindex"]][1][1] +
                                 self.settings["buttons"][self.settings["settingsposindex"]][1][3],
                                 self.settings["settingssizex"],
                                 self.settings["settingssizey"]])
            btn = widgets.button(self.surface, rect, self.settings["settingscolor"], name, onpress=self.changesettings,
                                 tooltip=str(val))
            self.settignslist.append(btn)
        self.resize()

    def changesettings(self, name):
        try:
            print(f"value for {name} property({self.prop_settings[name]}):")
            val = input(">>> ")
            val = int(val)
            self.prop_settings["name"] = val
        except ValueError:
            print("non-valid value!")

    def resize(self):
        super().resize()
        if hasattr(self, "field"):
            self.field.resize()
            for i in self.buttonslist:
                i.resize()
            for i in self.settignslist:
                i.resize()
            self.renderfield()

    def blit(self):
        global mousp, mousp2, mousp1

        super().blit()
        if len(self.buttonslist) > 2:
            self.buttonslist[-1].blit(sum(pg.display.get_window_size()) // 100)
            pg.draw.rect(self.surface, settings["TE"]["menucolor"], pg.rect.Rect(self.buttonslist[0].xy, [self.buttonslist[0].rect.w, len(self.buttonslist[:-1]) * self.buttonslist[0].rect.h + 1]))
            for button in self.buttonslist[:-1]:
                button.blit(sum(pg.display.get_window_size()) // 120)
            for button in self.settignslist:
                button.blit(sum(pg.display.get_window_size()) // 120)
            for button in self.settignslist:
                button.blittooltip()

        self.labels[0].set_text(self.labels[0].originaltext + "\n".join(self.notes))
        if self.field.rect.collidepoint(pg.mouse.get_pos()) or any(self.helds):

            pos = [math.floor((pg.mouse.get_pos()[0] - self.field.rect.x) / self.size),
                   math.floor((pg.mouse.get_pos()[1] - self.field.rect.y) / self.size)]
            pos2 = [round((pg.mouse.get_pos()[0] - self.field.rect.x) / self.size * image1size, 4),
                    round((pg.mouse.get_pos()[1] - self.field.rect.y) / self.size * image1size, 4)]
            posoffset = [pos2[0] - self.xoffset * image1size, pos2[1] - self.yoffset * image1size]
            bp = pg.mouse.get_pressed(3)
            # pg.draw.circle(self.fieldmap, red, pg.Vector2(posoffset) / image1size * self.size, 20)

            s = [self.findparampressed("stretch_topleft"),
                 self.findparampressed("stretch_topright"),
                 self.findparampressed("stretch_bottomright"),
                 self.findparampressed("stretch_bottomleft")]

            qd = quadsize(self.quads)
            mosts = qd[2]

            self.if_set(s[0], 0)
            self.if_set(s[1], 1)
            self.if_set(s[2], 2)
            self.if_set(s[3], 3)

            if bp[0] == 1 and mousp and (mousp2 and mousp1):
                mousp = False
                self.place()
            elif bp[0] == 0 and not mousp and (mousp2 and mousp1):
                mousp = True
                # pg.draw.circle(self.f, red, posoffset, 20)

            if not any(self.helds):
                self.surface.blit(self.selectedimage, pg.Vector2(pg.mouse.get_pos()) - pg.Vector2(self.selectedimage.get_size()) / 2)
            else:
                q2s = pg.Vector2(mosts[0], mosts[1])
                self.surface.blit(self.selectedimage, self.helppoins + q2s)

            self.movemiddle(bp, pos)

    def if_set(self, pressed, quadindx):
        if pressed and not self.helds[quadindx]:
            self.helds[quadindx] = True
            self.helppoins = pg.Vector2(pg.mouse.get_pos())
        elif pressed and self.helds[quadindx]:
            self.quads[quadindx] = list(pg.Vector2(pg.mouse.get_pos()) - self.helppoins)
            self.quads[quadindx] = [round(self.quads[quadindx][0], 4), round(self.quads[quadindx][1], 4)]
            self.updateproptransform()
        elif not pressed and self.helds[quadindx]:
            self.helds[quadindx] = False
            self.updateproptransform()

    def browse_next(self):
        self.itemindx = (self.itemindx + 1) % (len(self.buttonslist) - 1)
        self.setprop(self.buttonslist[self.itemindx].text)

    def browse_prev(self):
        self.itemindx -= 1
        if self.itemindx < 0:
            self.itemindx = len(self.buttonslist) - 2
        self.setprop(self.buttonslist[self.itemindx].text)

    def cat_next_propupdate(self):
        self.cat_next()
        self.setprop(self.buttonslist[self.itemindx].text)

    def cat_prev_propupdate(self):
        self.cat_prev()
        self.setprop(self.buttonslist[self.itemindx].text)

    def cat_next(self):
        self.currentcategory = (self.currentcategory + 1) % len(self.props)
        self.rebuttons()

    def cat_prev(self):
        self.currentcategory -= 1
        if self.currentcategory < 0:
            self.currentcategory = len(self.props) - 1
        self.rebuttons()

    def setprop(self, name):
        prop, ci = self.findprop(name)
        if prop is None:
            print("Prop not found in memory! Try relaunch the app")
            return
        self.selectedprop = prop
        self.currentcategory = ci[0]
        self.itemindx = ci[1]
        self.transform_reset()
        self.applysettings()
        self.applytags()
        self.rebuttons()

    def rfa(self):
        super().rfa()
        for indx, prop in enumerate(self.data["PR"]["props"]):
            var = 0
            if prop[4]["settings"].get("variation") is not None:
                var = prop[4]["settings"]["variation"] - 1
            found, _ = self.findprop(prop[1])
            if found is None:
                print(f"Prop {prop[1]} not Found! image not loaded")
            image = found["images"][var] # .save(path2hash + str(id(self.data["PR"]["props"][indx][1])) + ".png")
            qd = prop[3]
            quads = []
            for q in qd:
                quads.append(toarr(q, "point"))

            # surf = pg.image.fromstring(string, [ws, hs], "RGBA")
            surf, mostleft, mosttop, ww, wh = quadtransform(quads, image)
            surf = pg.transform.scale(surf, [ww * sprite2image, wh * sprite2image])
            surf.set_colorkey(white)
            surf.set_alpha(100)
            self.f.blit(surf, [mostleft / 16 * 20, mosttop / 16 * 20])
        self.renderfield()

    def findprop(self, name):
        for cati, cats in self.props.items():
            for itemi, item in enumerate(cats):
                if item["nm"] == name:
                    return item, [list(self.props.keys()).index(cati), itemi]
        return None, None

    def rotate(self, a):
        for indx, quad in enumerate(self.quads):
            px, py = quad
            angle = math.radians(a)
            qx = math.cos(angle) * px - math.sin(angle) * py
            qy = math.sin(angle) * px + math.cos(angle) * py
            self.quads[indx] = [round(qx, 4), round(qy, 4)]
        self.updateproptransform()

    def flipx(self):
        for indx, quad in enumerate(self.quads):
            self.quads[indx][0] = -quad[0]
        self.updateproptransform()

    def flipy(self):
        for indx, quad in enumerate(self.quads):
            self.quads[indx][1] = -self.quads[indx][1]
        self.updateproptransform()

    def applytags(self):
        tags = self.selectedprop["tags"]
        for tag in tags:
            match tag:
                case "randomRotat":
                    self.rotate(rnd.randint(0, 360))
                case "randomFlipX":
                    self.flipx() if rnd.choice([True, False]) else False
                case "randomFlipY":
                    self.flipy() if rnd.choice([True, False]) else False

    def reset_settings(self):
        self.prop_settings = {"renderorder": 0, "seed": 500, "renderTime": 0}

    def applysettings(self):
        self.prop_settings = {"renderorder": 0, "seed": rnd.randint(0, 1000), "renderTime": 0}
        random = self.selectedprop["random"] if self.selectedprop.get("random") is not None else 1
        notes = self.selectedprop["notes"].copy()
        match self.selectedprop["tp"]:
            case "standard", "variedStandard":
                if self.selectedprop["colorTreatment"] == "bevel":
                    notes.append("The highlights and shadows on this prop are generated by code,\nso it can be rotated to any degree and they will remain correct.\n")
                else:
                    notes.append("Be aware that shadows and highlights will not rotate with the prop,\nso extreme rotations may cause incorrect shading.\n")
                if self.selectedprop["tp"] == "variedStandard":
                    self.prop_settings["variation"] = 0 if random else 1

                if random:
                    notes.append(f"Will put down a random variation.\nA specific variation can be selected from settings ('{self.findkey('-propoptions_toggle')}\n' key).")
                else:
                    notes.append(f"This prop comes with many variations.\nWhich variation can be selected from settings ('{self.findkey('-propoptions_toggle')}' key).\n")
            case "rope":
                self.prop_settings["release"] = 0
            case "variedDecal", "variedSoft":
                self.prop_settings["variation"] = 0 if random else 1
                self.prop_settings["customDepth"] = self.depth
                if self.selectedprop["tp"] == "variedSoft" and self.selectedprop.get("colorize"):
                    self.prop_settings["applyColor"] = 1
                    notes.append("It's recommended to render this prop after the effects if the color is activated, as the effects won't affect the color layers.")
            case "simpleDecal", "soft", "softEffect", "antimatter":
                self.prop_settings["customDepth"] = self.depth
        if self.selectedprop["tp"] == "soft" or self.selectedprop["tp"] == "softEffect" or self.selectedprop["tp"] == "variedSoft":
            if self.selectedprop.get("selfShade") == 1:
                notes.append("The highlights and shadows on this prop are generated by code,\nso it can be rotated to any degree and they will remain correct.")
            else:
                notes.append("Be aware that shadows and highlights will not rotate with the prop,\nso extreme rotations may cause incorrect shading.")
        match self.selectedprop["nm"]:
            case "wire", "Zero-G Wire":
                self.prop_settings["thickness"] = 2
                notes.append("The thickness of the wire can be set in settings.")
            case "Zero-G Tube":
                self.prop_settings["applyColor"] = 0
                notes.append("The tube can be colored white through the settings.")
        for tag in self.selectedprop["tags"]:
            match tag:
                case "customColor":
                    self.prop_settings["color"] = 0
                    notes.append("Custom color available")
                case "customColorRainBow":
                    self.prop_settings["color"] = 1
                    notes.append("Custom color available")
        newnotes = []
        for note in self.notes:
            if note in newnotes:
                pass
            else:
                newnotes.append(note)
        self.notes = notes
        self.settingsupdate()

    def updateproptransform(self):
        self.loadimage()
        self.selectedimage = quadtransform(self.quads, self.selectedimage)[0]
        self.selectedimage = pg.transform.scale(self.selectedimage, pg.Vector2(self.selectedimage.get_size()) / spritesize * self.size)
        self.selectedimage.set_colorkey(white)

    def loadimage(self):
        var = self.selectedprop["vars"] - 1 if self.selectedprop.get("vars") is not None else 0
        self.selectedimage: pg.Surface = self.selectedprop["images"][var]

    def transform_reset(self):
        self.loadimage()

        w, h = self.selectedimage.get_size()
        wd, hd = w / 2, h / 2
        self.quads = [[-wd, -hd], [wd, -hd], [wd, hd], [-wd, hd]]
        self.updateproptransform()

    def place(self):
        quads = self.quads.copy()
        mousepos = pg.Vector2(pg.mouse.get_pos())
        posonfield = ((mousepos - pg.Vector2(self.field.rect.topleft)) / self.size - pg.Vector2(self.xoffset, self.yoffset)) * spritesize
        for i, q in enumerate(quads):
            vec = pg.Vector2(q) + posonfield
            quads[i] = makearr(list(vec), "point")
        prop = [self.depth, self.selectedprop["nm"], makearr([self.currentcategory, self.itemindx], "point"), quads, {"settings": self.prop_settings}]
        self.applytags()
        self.data["PR"]["props"].append(prop)
        self.rfa()

    def rotate_right(self):
        if self.findparampressed("rotate_speedup"):
            self.rotate(self.settings["rotate_speedup"])
        else:
            self.rotate(self.settings["rotate_speed"])

    def rotate_left(self):
        if self.findparampressed("rotate_speedup"):
            self.rotate(-self.settings["rotate_speedup"])
        else:
            self.rotate(-self.settings["rotate_speed"])

    def rotate0(self):
        self.transform_reset()

    def rotate90(self):
        self.transform_reset()
        self.rotate(90)

    def rotate180(self):
        self.transform_reset()
        self.rotate(180)

    def rotate270(self):
        self.transform_reset()
        self.rotate(270)

    def stretch(self, axis, pos):
        for i, q in enumerate(self.quads):
            if q[axis] > 0:
                self.quads[i][axis] += pos
            else:
                self.quads[i][axis] -= pos
        self.updateproptransform()
    def stretchy_up(self):
        self.stretch(1, self.settings["stretch_speed"])

    def stretchy_down(self):
        self.stretch(1, -self.settings["stretch_speed"])

    def stretchx_up(self):
        self.stretch(0, self.settings["stretch_speed"])

    def stretchx_down(self):
        self.stretch(0, -self.settings["stretch_speed"])
