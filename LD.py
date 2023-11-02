from menuclass import *


class load(Menu):
    def __init__(self, process):
        super().__init__(process, "LD")

    def send(self, message):
        self.sendtoowner(message)

    def blit(self):
        super().blit(30)

    def open(self):
        self.sendtoowner("open")

    def new(self):
        self.sendtoowner("new")

    def tutorial(self):
        self.sendtoowner("tutorial")

    def report(self):
        report()

    def github(self):
        github()

    @property
    def custom_info(self):
        return "Have fun!"
