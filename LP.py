import widgets
from menuclass import *


class LP(menu):
    def __init__(self, surface: pg.surface.Surface, data):
        self.menu = "LP"
        self.sliders = []
        super().__init__(surface, data, "LP")
        for i in self.settings["sliders"]:
            self.sliders.append(widgets.slider(
                self.surface,
                i[0], i[1], i[2],
                i[3][0], i[3][1], self.data[i[4][0]][i[4][1]], i[3][2]))

    def blit(self):
        super().blit()
        for i in self.sliders:
            i.blit()
        self.labels[0].set_text(
            self.labels[0].originaltext % self.settings["nmd" + str(self.data["EX"]["defaultTerrain"])])
        self.labels[1].set_text(self.labels[1].originaltext % self.settings["nml" + str(self.data["EX2"]["light"])])
        for n, i in enumerate(self.sliders):
            self.data[self.settings["sliders"][n][4][0]][self.settings["sliders"][n][4][1]] = round(i.value)

    def resize(self):
        super().resize()
        for i in self.sliders:
            i.resize()

    def chparam(self, cat, name):
        self.data[cat][name] = 1 - self.data[cat][name]
        self.updatehistory([[cat, name]])

    def chinput(self, cat, name, inputdesc):
        try:
            i = self.askint(f"{inputdesc}({self.data[cat][name]})")
            self.data[cat][name] = i
        except ValueError:
            print("Invalid input!")

    def changeborder(self):
        self.chparam("EX", "defaultTerrain")

    def changelight(self):
        self.chparam("EX2", "light")
