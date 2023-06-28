from menuclass import *


class HK(Menu):
    def __init__(self, surface: pg.surface.Surface, renderer, openmenu="MN"):
        self.menu = "HK"
        self.m = openmenu
        self.keys = json.load(open(path + "hotkeystip.json"))
        self.scroll = 0

        super().__init__(surface, renderer, "HK")
        self.fontsize = self.labels[0].fontsize
        self.load_menu(openmenu)

    def load_menu(self, name):
        if name != self.m:
            self.m = name
            self.scroll = 0
        text = self.m + "\n"
        text2 = "\n"
        for key, func in hotkeys[self.m].items():
            if key == "unlock_keys":
                continue
            desc = self.keys[self.m][func]
            tx = pg.key.name(getattr(pg, key.replace("@", "").replace("+", ""))).title() + "\n"
            tx2 = desc+"\n"
            if "+" in key:
                tx = "Ctrl + " + tx
            text += tx
            text2 += tx2

        self.labels[0].set_text(text)
        self.labels[1].set_text(text2)

    def send(self, message):
        super().send(message)
        match message:
            case "SD":
                if self.scroll + 1 <= self.labels[1].text.count("\n"):
                    self.scroll += 1
                self.load_menu(self.m)
            case "SU":
                if self.scroll - 1 > -1:
                    self.scroll -= 1
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
        self.message = self.m

    def edit(self):
        if islinux:
            os.system(f"open files/hotkeys.json")
        else:
            os.system(f"{path}hotkeys.json")