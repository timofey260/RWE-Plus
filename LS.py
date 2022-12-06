from lingotojson import *
from menuclass import *


class LS(menu):

    def __init__(self, surface: pg.surface.Surface, data, items):
        self.menu = "LS"
        self.btiles = data["EX2"]["extraTiles"]

        self.items = items

        self.message = ''

        self.ofstop = ofstop
        self.ofsleft = ofsleft

        self.field = None

        self.shadowmode = True

        super().__init__(surface, data, "LS")
        self.recount()
        self.init()
        self.blit()
        self.resize()

    def recount(self):
        self.gw = len(self.data["GE"])
        self.gh = len(self.data["GE"][0])
        self.tw = len(self.data["TE"]["tlMatrix"])
        self.th = len(self.data["TE"]["tlMatrix"][0])

        self.recount_image()

    def blit(self):
        if self.field is not None:
            self.labels[0].set_text(self.labels[0].originaltext % (self.imagew, self.imageh, self.imagewp, self.imagehp))
        else:
            self.labels[0].set_text("Image not found! try make it in light editor!")

        mt = self.settings["tm" + str(int(self.shadowmode) + 1)]
        tt = self.settings["tt" + str(int(self.shadowmode) + 1)]
        self.buttons[0].text = self.buttons[0].originaltext + mt
        self.buttons[0].tooltip = self.buttons[0].originaltext + tt

        self.labels[1].set_text(self.labels[1].originaltext % (self.gw, self.gh))
        self.labels[2].set_text(self.labels[2].originaltext % (self.tw, self.th))
        self.labels[3].set_text(self.labels[3].originaltext % (str(self.btiles)))
        super().blit()

    def resize(self):
        super().resize()

    def send(self, message):
        if message[0] == "-":
            getattr(self, message[1:])()

    def as_left(self):
        try:
            val = int(input("Enter number of tiles to be deleted/added: "))
            self.cuteverydata(val, 0, 0, 0)
        except ValueError:
            print("non valid answer")

    def as_top(self):
        try:
            val = int(input("Enter number of tiles to be deleted/added: "))
            self.cuteverydata(0, val, 0, 0)
        except ValueError:
            print("non valid answer")

    def set_width(self):
        try:
            val = int(input(f"Enter width({self.gw}): "))
            self.cuteverydata(0, 0, val, 0)
        except ValueError:
            print("non valid answer")

    def set_height(self):
        try:
            val = int(input(f"Enter height({self.gh}): "))
            self.cuteverydata(0, 0, 0, val)
        except ValueError:
            print("non valid answer")

    def cuteverydata(self, x, y, w, h):
        ans = input("Are you sure?(y/n)>> ")
        if ans.lower() != "y":
            print("Not changed")
            return
        self.data["GE"] = self.cutdata(x, y, w, h, self.data["GE"], [[0, []], [0, []], [0, []]])
        self.cuttiles(x, y, w, h)
        for num, effect in enumerate(self.data["FE"]["effects"]):
            self.data["FE"]["effects"][num]["mtrx"] = self.cutdata(x, y, w, h, effect["mtrx"], 0)
        self.recount()
        self.resizeimage(x, y, w, h)
        self.recount_image()
        self.data["EX2"]["size"] = makearr([len(self.data["GE"]), len(self.data["GE"][0])], "point")
        print("done")

    def cutdata(self, x, y, w, h, array, default_instance):
        arr = array
        if x >= 0:
            for _ in range(x):
                arr.insert(0, [default_instance for _ in range(len(arr[0]))])
        else:
            arr = arr[-x:]

        if w != 0:
            if w < self.gw:
                arr = arr[:w]
            else:
                for _ in range(w - self.gw):
                    arr.append([default_instance for _ in range(len(arr[0]))])

        if y >= 0:
            for i in range(len(arr)):
                for _ in range(y):
                    arr[i].insert(0, default_instance)
        else:
            for i in range(len(arr)):
                arr[i] = arr[i][-y:]

        if h != 0:
            for i in range(len(arr)):
                if h < self.gh:
                    arr[i] = arr[i][:h]
                else:
                    for _ in range(h - self.gh):
                        arr[i].append(default_instance)
        return arr

    def cuttiles(self, x, y, w, h):
        cutted = self.cutdata(x, y, w, h, self.data["TE"]["tlMatrix"], [{"tp": "default", "data": 0},
                                                                        {"tp": "default", "data": 0},
                                                                        {"tp": "default", "data": 0}])
        for xp, xv in enumerate(cutted):
            for yp, yv in enumerate(xv):
                for layer, item in enumerate(yv):
                    if item["tp"] == "tileBody":
                        dat = toarr(item["data"][0], "point")
                        dat[0] -= x
                        dat[1] -= y
                        if dat[0] < 0 or dat[1] < 0 or dat[0] > len(self.data["GE"]) or dat[1] > len(self.data["GE"][0]):
                            cutted[xp][yp][layer] = {"tp": "default", "data": 0}
                        else:
                            cutted[xp][yp][layer]["data"][0] = makearr(dat, "point")

        self.data["TE"]["tlMatrix"] = cutted

    def recount_image(self):
        try:
            lev = os.path.splitext(self.data["path"])[0] + ".png"
            self.field = pg.image.load(lev)
            self.imagew, self.imageh = self.field.get_size()
            self.imagewp = self.imagew / image1size - self.ofsleft + 1
            self.imagehp = self.imageh / image1size - self.ofstop + 1
        except FileNotFoundError:
            self.field = None

    def bftileschange(self):
        try:
            x = int(input(f"({self.btiles[0]})Left: "))
            y = int(input(f"({self.btiles[1]})Top: "))
            w = int(input(f"({self.btiles[2]})Right: "))
            h = int(input(f"({self.btiles[3]})Bottom: "))
            self.data["EX2"]["extraTiles"] = [x, y, w, h]
            self.btiles = self.data["EX2"]["extraTiles"]
        except ValueError:
            print("Error: non valid answer")

    def resizeimage(self, x, y, w, h):
        if self.field is not None:
            f2 = pg.surface.Surface([(abs(x) + self.gw + self.ofsleft) * image1size, (abs(y) + self.gh + self.ofstop) * image1size])
            f2.fill(white)
            f2.blit(self.field, [x * image1size, y * image1size])
            if not self.shadowmode:
                self.field = f2.subsurface(pg.rect.Rect(0, 0, (self.gw + self.ofsleft) * image1size, (self.gh + self.ofstop) * image1size))
            else:
                sc = [
                    (len(self.data["GE"]) + self.ofsleft) * image1size,
                    (len(self.data["GE"][0]) + self.ofstop) * image1size
                ]
                self.field = pg.transform.scale(self.field, sc)
            lev = os.path.splitext(self.data["path"])[0] + ".png"
            pg.image.save(self.field, lev)

    def mswich(self):
        self.shadowmode = not self.shadowmode
