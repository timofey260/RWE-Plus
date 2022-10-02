from lingotojson import turntolingo
from menuclass import *


class MN(menu):
    def __init__(self, surface: pg.surface.Surface, data):
        self.menu = "MN"
        self.surface = surface
        self.data = data
        self.init()

    def GE(self):
        self.message = "GE"

    def TE(self):
        self.message = "TE"

    def LE(self):
        self.message = "LE"

    def save(self):
        self.message = "save"

    def saveastxt(self):
        self.message = "savetxt"

    def render(self):
        fl = application_path + "\\a.txt"
        file = open(fl, "w")
        turntolingo(self.data, file)
        os.system(application_path + "\\drizzle\\Drizzle.ConsoleApp.exe render " + fl)

    def quit(self):
        self.message = "quit"
