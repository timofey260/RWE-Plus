from menuclass import *

class HK(menu):
    def __init__(self, surface: pg.surface.Surface, data, openmenu="MN"):
        self.menu = "HK"
        self.m = openmenu
        self.keys = open(path + "hotkeystip.md").readlines()

        super().__init__(surface, data, "HK")
        self.init()
        self.fontsize = self.labels[0].fontsize
        self.load_menu(openmenu)

    def load_menu(self, name):
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
                ft = line.find(" - ")
                tx = line[:ft] + "\n"
                tx2 = line[ft:]
                text += tx.replace("*", "").replace("###", "")
                tx2 = tx2[tx2.rfind(" - ") + 2:]
                text2 += tx2.replace("*", "").replace("###", "")
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

    def globalkeys(self):
        self.load_menu("global")

    def resize(self):
        super().resize()
        self.load_menu(self.m)

    def goback(self):
        self.message = self.m