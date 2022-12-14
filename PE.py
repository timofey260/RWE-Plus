from menuclass import *
import cv2
import numpy as np
import random as rnd

values = {
    "release": {
        -1: "left",
        1: "right",
        "def": "none"
    },
    "renderTime": {
        0: "Pre Effcts", # ?
        "def": "Post Effcts"
    },
    "variation": {
        0: "random"
    },
    "applyColor": {
        0: "NO",
        "def": "YES"
    },
    "color": {
        0: "NONE"
    },
}


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


def rotatepoint(point, angle):
    px, py = point
    angle = math.radians(angle)
    qx = math.cos(angle) * px - math.sin(angle) * py
    qy = math.sin(angle) * px + math.cos(angle) * py
    return pg.Vector2([qx, qy])


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
        self.snap = False
        self.notes = []

        self.quads = [[0, 0], [0, 0], [0, 0], [0, 0]]
        self.quadsnor = self.quads.copy() # quad's default position

        self.prop_settings = {}

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

    def getval(self, params, value):
        if params not in values.keys():
            return value
        if value in values[params].keys():
            return values[params][value]
        elif "def" in values[params].keys():
            return values[params]["def"]
        else:
            if params == "color":
                return self.propcolors[value]
            return value

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
                                 tooltip=str(self.getval(name, val)))
            self.settignslist.append(btn)
        self.resize()

    def changesettings(self, name):
        try:
            match name:
                case "release":
                    val = (self.prop_settings[name] + 2) % 3 - 1
                case "renderTime":
                    val = (self.prop_settings[name] + 1) % 2
                case "variation":
                    val = (self.prop_settings[name] + 1) % len(self.selectedprop["images"])
                    self.updateproptransform()
                case "applyColor":
                    val = (self.prop_settings[name] + 1) % 2
                case "color":
                    val = (self.prop_settings[name] + 1) % len(self.propcolors)
                case _:
                    print(f"value for {name} property({self.prop_settings[name]}):")
                    val = input(">>> ")
                    val = int(val)
            self.prop_settings[name] = val
        except ValueError:
            print("non-valid value!")
        self.settingsupdate()

    def change_variation_up(self):
        if self.prop_settings.get("variation") is None:
            return
        val = (self.prop_settings["variation"] + 1) % len(self.selectedprop["images"])
        self.prop_settings["variation"] = val
        self.updateproptransform()

    def change_variation_down(self):
        if self.prop_settings.get("variation") is None:
            return
        val = (self.prop_settings["variation"] - 1)
        if val < 0:
            val = len(self.selectedprop["images"]) - 1
        self.prop_settings["variation"] = val
        self.updateproptransform()

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

        self.labels[2].set_text(self.labels[2].originaltext + str(self.prop_settings))
        self.labels[0].set_text(self.labels[0].originaltext + "\n".join(self.notes))
        cir = [self.buttonslist[self.itemindx].rect.x + 3,
               self.buttonslist[self.itemindx].rect.y + self.buttonslist[self.itemindx].rect.h / 2]
        pg.draw.circle(self.surface, cursor, cir, self.buttonslist[self.itemindx].rect.h / 2)
        if self.field.rect.collidepoint(pg.mouse.get_pos()) or any(self.helds):
            mpos = pg.Vector2(pg.mouse.get_pos())

            pos = [math.floor((mpos.x - self.field.rect.x) / self.size),
                   math.floor((mpos.y - self.field.rect.y) / self.size)]
            pos2 = [round(math.floor(mpos.x / image1size) * image1size - self.selectedimage.get_width() / 2, 4),
                    round(math.floor(mpos.y / image1size) * image1size - self.selectedimage.get_height() / 2, 4)]

            posoffset = [(pos[0] - self.xoffset) * spritesize, (pos[1] - self.yoffset) * spritesize]
            bp = pg.mouse.get_pressed(3)
            delmode = self.findparampressed("delete_mode")
            copymode = self.findparampressed("copy_mode")
            render = not delmode and not copymode
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

            if bp[0] == 1 and self.mousp and (self.mousp2 and self.mousp1):
                self.mousp = False
                if self.findparampressed("propvariation_change"):
                    self.change_variation_up()
                    self.settingsupdate()
                elif delmode:
                    *_, near = self.find_nearest(*posoffset)
                    self.data["PR"]["props"].pop(near)
                    self.rfa()
                elif copymode:
                    name, _, near = self.find_nearest(*posoffset)
                    self.setprop(name[1])
                    self.depth = -name[0]
                    quad = []
                    for q in name[3]:
                        quad.append(pg.Vector2(toarr(q, "point")))
                    quads2 = quad.copy()
                    qv = sum(quad, start=pg.Vector2(0, 0)) / 4
                    for i, q in enumerate(quad):
                        vec = pg.Vector2(q) - qv
                        vec = [round(vec.x, 4), round(vec.y, 4)]
                        quads2[i] = vec
                    self.quads = quads2
                    self.prop_settings = name[4]["settings"]
                    self.updateproptransform()
                elif self.selectedprop["tp"] == "long":
                    self.rectdata[0] = posoffset
                    self.rectdata[1] = mpos
                    self.transform_reset()
                else:
                    self.place()
            elif bp[0] == 1 and not self.mousp and (self.mousp2 and self.mousp1):
                if self.selectedprop["tp"] == "long":
                    self.transform_reset()
                    p1 = pg.Vector2(self.rectdata[0])
                    p2 = pg.Vector2(posoffset)
                    vec = p2 - p1
                    angle = math.degrees(math.atan2(vec.y, vec.x))
                    distance = p1.distance_to(p2)
                    newquads = self.quadsnor.copy()
                    newquads[1][0] = distance + newquads[0][0]
                    newquads[2][0] = distance + newquads[0][0]
                    q = []
                    point = pg.Vector2(newquads[0])
                    for quad in newquads:
                        newq = pg.Vector2(quad).rotate(angle)
                        if quad[0] < point.x:
                            point.x = quad[0]
                        if quad[1] < point.y:
                            point.y = quad[1]
                        q.append(newq)
                    self.quads = q
                    i, *_, ww, wh = quadtransform(q, self.selectedimage)
                    self.rectdata[2] = pg.Vector2(i.get_size())
                    i = pg.transform.scale(i, [ww / spritesize * self.size, wh / spritesize * self.size])
                    i.set_colorkey(white)
                    self.surface.blit(i, (pg.Vector2(self.rectdata[1]) + mpos) / 2 - pg.Vector2(i.get_size()) / 2)


            elif bp[0] == 0 and not self.mousp and (self.mousp2 and self.mousp1):
                self.mousp = True
                if self.selectedprop["tp"] == "long" and not delmode and not copymode:
                    self.place((pg.Vector2(self.rectdata[0]) + posoffset) / 2)
                    self.transform_reset()

            if bp[2] == 1 and self.mousp2 and (self.mousp and self.mousp1):
                self.mousp2 = False
                if self.findparampressed("propvariation_change"):
                    self.change_variation_down()
                    self.settingsupdate()
                elif self.findparampressed("cursor_propdepth_inverse"):
                    self.depth_down()
                else:
                    self.depth_up()
            elif bp[2] == 0 and not self.mousp2 and (self.mousp and self.mousp1):
                self.mousp2 = True

            if render:
                if not any(self.helds):
                    if self.snap:
                        self.surface.blit(self.selectedimage, pos2)
                    else:
                        self.surface.blit(self.selectedimage, mpos - pg.Vector2(self.selectedimage.get_size()) / 2)
                else:
                    q2s = pg.Vector2(mosts[0], mosts[1])
                    self.surface.blit(self.selectedimage, self.helppoins + q2s)
            depthpos = [mpos[0] + 20, mpos[1]]
            if self.findparampressed("propvariation_change"):
                varpos = [mpos[0] + 20, mpos[1] + 20]
                if self.prop_settings.get('variation') == 0:
                    widgets.fastmts(self.surface, "Variation: Random", *varpos, white)
                else:
                    widgets.fastmts(self.surface, f"Variation: {self.prop_settings.get('variation')}", *varpos, white)
            rl = sum(self.selectedprop["repeatL"]) if self.selectedprop.get("repeatL") else self.selectedprop["depth"]
            widgets.fastmts(self.surface, f"Depth: {self.depth} to {rl + self.depth}", *depthpos, white)
            if copymode or delmode:
                _, near, _ = self.find_nearest(*posoffset)
                ofc = pg.Vector2(self.xoffset, self.yoffset)
                pos2 = (near / spritesize + ofc) * self.size + self.field.rect.topleft
                pg.draw.line(self.surface, red, mpos, pos2, 10)
            self.movemiddle(bp, pos)

    def find_nearest(self, x, y):
        mpos = pg.Vector2(x, y)
        near = pg.Vector2(bignum, bignum)
        propnear = []
        nindx = 0
        for indx, prop in enumerate(self.data["PR"]["props"]):
            vec = pg.Vector2(toarr(prop[3][0], "point"))
            if vec.distance_to(mpos) < near.distance_to(mpos):
                near = vec
                nindx = indx
                propnear = prop
        return propnear, near, nindx

    def depth_up(self):
        maxdepth = self.layer * 10 + 10
        self.depth = (self.depth + 1) % maxdepth
        self.add_warning()

    def depth_down(self):
        maxdepth = self.layer * 10 + 10
        self.depth -= 1
        if self.depth < 0:
            self.depth = maxdepth - 1
        self.add_warning()

    def add_warning(self):
        if self.selectedprop["tp"] not in ["simpleDecal", "variedDecal"]:
            rl = sum(self.selectedprop["repeatL"]) if self.selectedprop.get("repeatL") else self.selectedprop["depth"]
            if self.layer * 10 + self.depth <= 5 and self.layer * 10 + self.depth + rl >= 6:
                self.labels[1].set_text(self.labels[1].originaltext + "this prop will intersect with the play layer!")
                if self.selectedprop["tp"] == "antimatter":
                    self.labels[1].set_text(self.labels[1].originaltext + "Antimatter prop intersecting play layer - remember to use a restore effect on affected play relevant terrain")
            else:
                self.labels[1].set_text(self.labels[1].originaltext)

    def swichlayers(self):
        super().swichlayers()
        self.depth = self.depth % 10 + self.layer * 10
        self.add_warning()

    def swichlayers_back(self):
        super().swichlayers_back()
        self.depth = self.depth % 10 + self.layer * 10
        self.add_warning()

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
        self.itemindx = 0
        self.currentcategory = (self.currentcategory + 1) % len(self.props)
        self.rebuttons()

    def cat_prev(self):
        self.itemindx = 0
        self.currentcategory -= 1
        if self.currentcategory < 0:
            self.currentcategory = len(self.props) - 1
        self.rebuttons()

    def setprop(self, name):
        prop, ci = self.findprop(name)
        if prop is None:
            print("Prop not found in memory! Try relaunch the app")
            return
        self.selectedprop = prop.copy()
        self.currentcategory = ci[0]
        self.itemindx = ci[1]
        self.snap = "snapToGrid" in self.selectedprop["tags"]
        self.add_warning()
        self.reset_settings()
        self.transform_reset()
        self.applysettings()
        self.applytags()
        self.rebuttons()

    def togglesnap(self):
        self.snap = not self.snap

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
            self.f.blit(surf, [mostleft / spritesize * image1size, mosttop / spritesize * image1size])
            if prop[4].get("points") is not None: # rope showing for future
                for point in prop[4]["points"]:
                    px, py = toarr(point, "point")
                    px = px / spritesize * image1size
                    py = py / spritesize * image1size
                    pg.draw.circle(self.f, rope, [px, py], 5)
        self.renderfield()

    def findprop(self, name):
        for cati, cats in self.props.items():
            for itemi, item in enumerate(cats):
                if item["nm"] == name:
                    return item, [list(self.props.keys()).index(cati), itemi]
        return None, None

    def rotate(self, a):
        for indx, quad in enumerate(self.quads):
            rot = rotatepoint(quad, a)
            qx, qy = rot.x, rot.y
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
        if self.selectedprop["tp"] in ["standard", "variedStandard"]:
                if self.selectedprop["colorTreatment"] == "bevel":
                    notes.append("The highlights and shadows on this prop are generated by code,\nso it can be rotated to any degree and they will remain correct.\n")
                else:
                    notes.append("Be aware that shadows and highlights will not rotate with the prop,\nso extreme rotations may cause incorrect shading.\n")
                if self.selectedprop["tp"] == "variedStandard":
                    self.prop_settings["variation"] = 0 if random else 1

                if random:
                    notes.append(f"Will put down a random variation.\nA specific variation can be selected from settings.\n")
                else:
                    notes.append(f"This prop comes with many variations.\nWhich variation can be selected from settings.\n")
        elif self.selectedprop['tp'] == "rope":
                self.prop_settings["release"] = 0
        elif self.selectedprop["tp"] in ["variedDecal", "variedSoft"]:
            self.prop_settings["variation"] = 0 if random else 1
            self.prop_settings["customDepth"] = self.selectedprop["depth"]
            if self.selectedprop["tp"] == "variedSoft" and self.selectedprop.get("colorize"):
                self.prop_settings["applyColor"] = 1
                notes.append("It's recommended to render this prop after the effects\nif the color is activated, as the effects won't affect the color layers.\n")
        elif self.selectedprop["tp"] in ["simpleDecal", "soft", "softEffect", "antimatter"]:
            self.prop_settings["customDepth"] = self.selectedprop["depth"]

        if self.selectedprop["tp"] == "soft" or self.selectedprop["tp"] == "softEffect" or self.selectedprop["tp"] == "variedSoft":
            if self.selectedprop.get("selfShade") == 1:
                notes.append("The highlights and shadows on this prop are generated by code,\nso it can be rotated to any degree and they will remain correct.\n")
            else:
                notes.append("Be aware that shadows and highlights will not rotate with the prop,\nso extreme rotations may cause incorrect shading.\n")
        match self.selectedprop["nm"]:
            case "wire", "Zero-G Wire":
                self.prop_settings["thickness"] = 2
                notes.append("The thickness of the wire can be set in settings.\n")
            case "Zero-G Tube":
                self.prop_settings["applyColor"] = 0
                notes.append("The tube can be colored white through the settings.\n")
        for tag in self.selectedprop["tags"]:
            match tag:
                case "customColor":
                    self.prop_settings["color"] = 0
                    notes.append("Custom color available\n")
                case "customColorRainBow":
                    self.prop_settings["color"] = 1
                    notes.append("Custom color available\n")
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
        var = rnd.randint(0, len(self.selectedprop["images"]) - 1)
        if self.prop_settings.get("variation") not in [None, 0]:
            var = self.prop_settings["variation"] - 1
        self.selectedimage: pg.Surface = self.selectedprop["images"][var]

    def transform_reset(self):
        self.loadimage()

        w, h = self.selectedimage.get_size()
        wd, hd = w / 2, h / 2
        self.quads = [[-wd, -hd], [wd, -hd], [wd, hd], [-wd, hd]]
        self.quadsnor = self.quads.copy()
        self.updateproptransform()

    def place(self, longpos=None):
        quads = self.quads.copy()
        quads2 = quads.copy()
        mousepos = pg.Vector2(pg.mouse.get_pos())
        posonfield = ((mousepos - pg.Vector2(self.field.rect.topleft)) / self.size - pg.Vector2(self.xoffset, self.yoffset)) * spritesize
        if self.snap:
            posonfield = [round(math.floor(posonfield[0] / image1size) * image1size, 4),
                          round(math.floor(posonfield[1] / image1size) * image1size, 4)]
        qv = []
        for i, q in enumerate(quads):
            vec = pg.Vector2(q)
            qv.append(vec)
        qv = sum(qv, start=pg.Vector2(0, 0)) / 4
        for i, q in enumerate(quads):
            vec = pg.Vector2(q) - qv * 2 + posonfield
            if longpos:
                vec = pg.Vector2(q) - qv + longpos # I literally have no idea how this works
            vec = [round(vec.x, 4), round(vec.y, 4)]
            quads2[i] = makearr(vec, "point")
        newpropsettings = self.prop_settings.copy()
        if self.prop_settings.get("variation") is not None:
            if self.prop_settings["variation"] == 0: # random
                newpropsettings["variation"] = rnd.randint(1, len(self.selectedprop["images"]))
        prop = [-self.depth, self.selectedprop["nm"], makearr([self.currentcategory + 1, self.itemindx + 1], "point"), quads2, {"settings": newpropsettings}]
        self.data["PR"]["props"].append(prop.copy())
        self.applytags()
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
