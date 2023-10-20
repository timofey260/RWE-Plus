import render
from menuclass import *
from lingotojson import *

error = globalsettings["snap_error"] # snap error

class CE(MenuWithField):
    def __init__(self, surface: pg.surface.Surface, renderer: render.Renderer):
        self.menu = "CE"
        self.mode = "move"  # move, edit
        super().__init__(surface, "CE", renderer, renderall=False)

        self.held = False
        self.heldindex = 0
        self.drawcameras = True
        self.camoffset = pg.Vector2(0, 0)
        self.pressed = [False] * 4
        self.heldpointindex = 0

        self.rfa()
        self.blit()
        self.resize()

    def blit(self):
        super().blit()
        self.labels[0].set_text(self.labels[0].originaltext % len(self.data["CM"]["cameras"]))

        if self.onfield and len(self.data["CM"]["cameras"]) > 0:

            bp = self.getmouse
            s = [self.findparampressed("-addup"),
                 self.findparampressed("-adddown"),
                 self.findparampressed("-addleft"),
                 self.findparampressed("-addright")]

            self.if_set(s[0], 0)
            self.if_set(s[1], 1)
            self.if_set(s[2], 2)
            self.if_set(s[3], 3)
            mpos = pg.Vector2(pg.mouse.get_pos()) / self.size * image1size
            if self.held and self.heldindex < len(self.data["CM"]["cameras"]) and self.mode == "move":
                val = list(self.camoffset + mpos)
                val[0] = round(val[0], 4)
                val[1] = round(val[1], 4)
                for indx, camera in enumerate(self.data["CM"]["cameras"]):
                    if indx == self.heldindex:
                        continue
                    xpos, ypos = toarr(camera, "point")
                    valx, valy = val
                    s = False
                    if xpos - error < valx < xpos + error:
                        val[0] = xpos
                        s = True
                    if ypos - error < valy < ypos + error:
                        val[1] = ypos
                        s = True
                    if s:
                        v = pg.Vector2(self.field.rect.topleft) + (pg.Vector2(camw/2, camh/2) * self.size)
                        v += self.offset * self.size
                        startpos = pg.Vector2(val) / image1size * self.size + v
                        endpos = pg.Vector2(xpos, ypos) / image1size * self.size + v
                        pg.draw.line(self.surface, purple, startpos, endpos, 3)
                val = makearr(val, "point")
                self.changedata(["CM", "cameras", self.heldindex], val)

            if bp[0] == 1 and self.mousp and (self.mousp2 and self.mousp1):
                self.mousp = False
                if self.mode == "move":
                    if not self.held:
                        self.pickupcamera()
                    else:
                        self.placecamera()
                else:
                    self.setcursor(pg.SYSTEM_CURSOR_SIZEALL)
            elif bp[0] == 1 and not self.mousp and (self.mousp2 and self.mousp1):
                if self.mode == "edit" and self.held:
                    quadindx = self.getquad(self.heldindex)
                    rect = self.getcamerarect(self.data["CM"]["cameras"][self.heldindex])
                    qlist = [rect.topleft, rect.topright, rect.bottomright, rect.bottomleft]
                    mouse = pg.Vector2(pg.mouse.get_pos()) - qlist[quadindx]
                    r, o = mouse.rotate(90).as_polar()
                    self.changedata(["CM", "quads", self.heldindex, quadindx], [round(o, 4), round(min(r / 100 / self.size * image1size, 1), 4)])
                    # self.data["CM", "quads", self.heldindex, quadindx] = [round(o, 4), round(min(r / 100 / self.size * image1size, 1), 4)]

            elif bp[0] == 0 and not self.mousp and (self.mousp2 and self.mousp1):
                self.setcursor()
                if self.mode == "edit":
                    self.updatehistory()
                # self.detecthistory(["CM", "quads", self.heldindex])
                self.mousp = True
                self.rfa()

            self.movemiddle(bp)

    def togglemode(self):
        if self.mode == "move":
            self.edit()
        else:
            self.move()


    def edit(self):
        if self.held:
            self.mode = "edit"
            self.recaption()
        else:
            print("First pick up camera!")

    def move(self):
        self.mode = "move"
        self.recaption()

    def camup(self):
        if self.held and self.heldindex + 1 < len(self.data["CM"]["cameras"]):
            self.historymove(["CM", "cameras"], self.heldindex, 1)
            self.historymove(["CM", "quads"], self.heldindex, self.heldindex + 1)
            self.heldindex += 1
            self.updatehistory()

    def camdown(self):
        if self.held and self.heldindex - 1 >= 0:
            self.historymove(["CM", "cameras"], self.heldindex, 1)
            self.historymove(["CM", "quads"], self.heldindex, self.heldindex - 1)
            self.heldindex -= 1
            self.updatehistory()

    def copycamera(self):
        if self.held:
            pyperclip.copy(str(self.data["CM"]["quads"][self.heldindex]))

    def pastedata(self):
        if not self.held:
            try:
                geodata = eval(pyperclip.paste())
                if type(geodata) != list or len(pyperclip.paste()) <= 2:
                    return
                self.historyappend(["CM", "cameras"], makearr([0, 0], "point"))
                self.historyappend(["CM", "quads"], geodata)
                self.held = True
                self.heldindex = len(self.data["CM"]["cameras"]) - 1
                self.detecthistory(["CM"])
                self.rfa()
            except:
                print("Error pasting data!")

    def if_set(self, pressed, indx):
        if pressed and not self.pressed[indx]:
            self.pressed[indx] = True
        elif pressed and self.pressed[indx]:
            pass
        elif not pressed and self.pressed[indx]:
            self.pressed[indx] = False
            i = self.closestcameraindex()
            self.updatehistory()

    def pickupcamera(self):
        mpos = pg.Vector2(pg.mouse.get_pos()) / self.size * image1size
        closeindex = self.closestcameraindex()

        self.heldindex = closeindex
        self.held = True
        self.camoffset = pg.Vector2(toarr(self.data["CM"]["cameras"][self.heldindex], "point")) - mpos

    def placecamera(self):
        self.held = False
        self.updatehistory()

    def deletecamera(self):
        if len(self.data["CM"]["cameras"]) > 0 and self.heldindex < len(self.data["CM"]["cameras"]) and self.held:
            self.historypop(["CM", "cameras"], self.heldindex)
            self.historypop(["CM", "quads"], self.heldindex)
            self.held = False
            self.updatehistory()

    def addcamera(self):
        self.historyappend(["CM", "cameras"], makearr([0, 0], "point"))
        self.historyappend(["CM", "quads"], [[0, 0], [0, 0], [0, 0], [0, 0]])
        self.heldindex = len(self.data["CM"]["cameras"]) - 1
        self.held = True
        self.camoffset = pg.Vector2(0, 0)
        self.updatehistory()

    def closestcameraindex(self):
        mpos = pg.Vector2(pg.mouse.get_pos())

        closeindex = 0
        dist = 10000

        for indx, cam in enumerate(self.data["CM"]["cameras"]):
            center = pg.Vector2(self.getcamerarect(cam).center)
            dist2 = center.distance_to(mpos)
            if dist2 < dist:
                dist = dist2
                closeindex = indx
        return closeindex

    def addup(self):
        if not self.held:
            cam = self.closestcameraindex()
            quadindx = self.getquad(cam)
            self.changedata(["CM", "quads", cam, quadindx, 1],
                            round(min(self.data["CM"]["quads"][cam][quadindx][1] + self.settings["addspeed"], 1), 4))

    def adddown(self):  # ddddddddddd
        if not self.held:
            cam = self.closestcameraindex()
            quadindx = self.getquad(cam)
            self.changedata(["CM", "quads", cam, quadindx, 1], round(
                max(self.data["CM"]["quads"][cam][quadindx][1] - self.settings["addspeed"], 0), 4))

    def addleft(self):
        if not self.held:
            cam = self.closestcameraindex()
            quadindx = self.getquad(cam)
            self.changedata(["CM", "quads", cam, quadindx, 0],
                            math.floor(self.data["CM"]["quads"][cam][quadindx][0] - self.settings["rotatespeed"]) % 360)

    def addright(self):
        if not self.held:
            cam = self.closestcameraindex()
            quadindx = self.getquad(cam)
            self.changedata(["CM", "quads", cam, quadindx, 0],
                            math.ceil(self.data["CM"]["quads"][cam][quadindx][0] + self.settings["rotatespeed"]) % 360)

    @property
    def custom_info(self):
        return f"{super().custom_info} | Mode: {self.mode}"