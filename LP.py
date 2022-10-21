from menuclass import *


class LP(menu):
    def __init__(self, surface: pg.surface.Surface, data):
        super().__init__(surface, data, "LP")

    def blit(self):
        super().blit()
        self.labels[0].set_text(
            self.labels[0].originaltext % settings[self.menu]["nmd" + str(self.data["EX"]["defaultTerrain"])])
        self.labels[1].set_text(self.labels[1].originaltext % settings[self.menu]["nml" + str(self.data["EX2"]["light"])])
        self.labels[2].set_text(
            self.labels[2].originaltext % settings[self.menu]["nmw" + str(self.data["EX"]["waterDrips"])])

    def chparam(self, cat, name):
        self.data[cat][name] = 1 - self.data[cat][name]

    def chinput(self, cat, name, inputdesc):
        try:
            i = int(input(inputdesc + f"({self.data[cat][name]})"))
            self.data[cat][name] = i
        except ValueError:
            print("Invalid input!")

    def changeborder(self):
        self.chparam("EX", "defaultTerrain")

    def changelight(self):
        self.chparam("EX2", "light")

    def changewd(self):
        self.chparam("EX", "waterDrips")
