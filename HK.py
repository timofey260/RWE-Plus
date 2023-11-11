from menuclass import *


class HK(Menu):
    def __init__(self, process, openmenu="MN"):
        self.menu = "HK"
        self.m = openmenu
        self.keys = json.load(open(path + "hotkeystip.json"))
        self.scroll = 0
        self.lines = 0

        super().__init__(process, "HK")
        self.fontsize = self.labels[0].fontsize
        self.load_menu(openmenu)

    def load_menu(self, name):
        if name != self.m:
            self.m = name
            self.scroll = 0
        text = self.m + "\n"
        text2 = "\n"
        scc = self.scroll
        self.lines = 0
        for key, func in hotkeys[self.m].items():
            self.lines += 1
            if scc >= 0:
                scc -= 1
                continue
            if key == "unlock_keys":
                continue
            try:
                desc = self.keys[self.m][func]
            except KeyError:
                desc = "???"
            tx = pg.key.name(getattr(pg, key.replace("@", "").replace("+", ""))).title() + "\n"
            tx2 = desc+"\n"
            if "+" in key:
                tx = "Ctrl + " + tx
            text += tx
            text2 += tx2
        self.labels[0].set_text(text)
        self.labels[1].set_text(text2)

    def scroll_up(self):
        if self.scroll - 1 > -1:
            self.scroll -= 1
        self.load_menu(self.m)

    def scroll_down(self):
        if self.scroll + 1 < self.lines - 1:
            self.scroll += 1
        self.load_menu(self.m)

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

    def PE(self):
        self.load_menu("PE")

    def LP(self):
        self.load_menu("LP")

    def globalkeys(self):
        self.load_menu("global")

    def resize(self):
        super().resize()
        self.load_menu(self.m)

    def goback(self):
        self.sendtoowner(self.m)

    def edit(self):
        if islinux:
            os.system(f"open files/hotkeys.json")
        else:
            os.system(f"{path}hotkeys.json")