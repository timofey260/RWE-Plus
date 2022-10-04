from lingotojson import *
from menuclass import *


class LS(menu):

    def __init__(self, surface: pg.surface.Surface, data):
        self.menu = "LS"
        self.surface = surface
        self.btiles = data["EX2"]["extraTiles"]
        self.data = data

        self.rectdata = [[0, 0], [0, 0], [0, 0]]
        self.xoffset = 0
        self.yoffset = 0

        self.size = settings["TE"]["cellsize"]

        self.message = ''

        self.ofstop = ofstop
        self.ofsleft = ofsleft

        self.gw = len(self.data["GE"])
        self.gh = len(self.data["GE"][0])
        self.tw = len(self.data["TE"]["tlMatrix"])
        self.th = len(self.data["TE"]["tlMatrix"][0])

        self.field = None

        self.recount_image()
        self.init()
        self.blit()
        self.resize()

    def blit(self):
        if self.field is not None:
            self.labels[0].set_text(self.labels[0].originaltext % (self.imagew, self.imageh, self.imagewp, self.imagehp))
        else:
            self.labels[0].set_text("Image not found! try make it in light editor!")
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

    def cuteverydata(self, x, y, w, h):
        ans = input("Are you sure?(y/n)>> ")
        if ans.lower() == "n":
            return
        self.data["GE"] = self.cutdata(x, y, w, h, self.data["GE"], [0, []])
        self.cuttiles(x, y, w, h)
        for num, effect in enumerate(self.data["FE"]["effects"]):
            self.data["FE"]["effects"][num]["mtrx"] = self.cutdata(x, y, w, h, effect["mtrx"], [0])

    def cutdata(self, x, y, w, h, array, default_instance):
        arr = array[x:len(array) - w]
        for xp, x in enumerate(arr):
            arr[xp] = x[y:len(x) - h]
        return arr

    def cuttiles(self, x, y, w, h):
        cutted = self.cutdata(x, y, w, h, self.data["TE"]["tlMatrix"], {"tp": "default", "data": 0})
        # TODO make this sh*t
        # self.data["TE"]["tlMatrix"] = cutted

    def recount_image(self):
        try:
            lev = os.path.splitext(self.data["path"])[0] + ".png"
            self.field = pg.image.load(lev)
            self.imagew, self.imageh = self.field.get_size()
            self.imagewp = self.imagew / image1size - self.ofsleft + 1
            self.imagehp = self.imageh / image1size - self.ofstop + 1
        except FileNotFoundError:
            self.field = None
