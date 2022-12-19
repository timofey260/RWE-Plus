from menuclass import *

class HK(menu):
    def __init__(self, surface: pg.surface.Surface, data):
        self.menu = "HK"
        self.m = "MN"
        self.keys = open(path + "hotkeystip.md").readlines()

        super().__init__(surface, data, "HK")
        self.init()
        self.fontsize = self.labels[0].fontsize
        self.load_menu("MN")

    def load_menu(self, name):
        try:
            a = getattr(self, "fontsize")
        except AttributeError:
            return
        self.m = name
        sw = False
        text = ""
        text2 = ""
        count = 0
        for line in self.keys:
            if "###" in line:
                if sw:
                    break
                if name in line:
                    sw = True
            if sw:
                if widgets.mts(text, blue, self.fontsize).get_height() > self.surface.get_height():
                    text2 += line.replace("*", "").replace("###", "") + "\n"
                    count += 1
                else:
                    text += line.replace("*", "").replace("###", "") + "\n"
                    count += 1

        self.labels[0].set_text(text)
        self.labels[1].set_text(text2)

    def MN(self):
        self.load_menu("MN")

    def GE(self):
        self.load_menu("GE")

    def HK(self):
        self.load_menu("HK")

    def TE(self):
        self.load_menu("TE")

    def LE(self):
        self.load_menu("LE")

    def CE(self):
        self.load_menu("CE")

    def FE(self):
        self.load_menu("FE")

    def EE(self):
        self.load_menu("EE")

    def PE(self):
        self.load_menu("PE")

    def LS(self):
        self.load_menu("LS")

    def LP(self):
        self.load_menu("LP")

    def resize(self):
        super().resize()
        self.load_menu(self.m)