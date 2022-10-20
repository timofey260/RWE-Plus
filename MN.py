from lingotojson import turntolingo
from menuclass import *


class MN(menu):
    def __init__(self, surface: pg.surface.Surface, data):
        super().__init__(surface, data, "MN")

    def GE(self):
        self.message = "GE"

    def TE(self):
        self.message = "TE"

    def LE(self):
        self.message = "LE"

    def LS(self):
        self.message = "LS"

    def FE(self):
        self.message = "FE"

    def CE(self):
        self.message = "CE"

    def save(self):
        self.message = "save"

    def saveastxt(self):
        self.message = "savetxt"

    def render(self):
        fl = os.path.splitext(self.data["path"])[0] + ".txt"
        file = open(fl, "w")
        turntolingo(self.data, file)
        os.system(application_path + "\\drizzle\\Drizzle.ConsoleApp.exe render " + fl)

    def quit(self):
        self.message = "quit"
