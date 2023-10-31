from menuclass import *

class load(Menu):
    def __init__(self, process):
        super().__init__(process, "LD")

    def send(self, message):
        self.message = message

    def blit(self):
        super().blit(30)

    def open(self):
        self.owner.recievemessage("open")
        # self.message = "open"

    def new(self):
        self.owner.recievemessage("new")
        # self.message = "new"

    def tutorial(self):
        self.owner.recievemessage("tutorial")
        # self.message = "tutorialRWE"

    def report(self):
        report()

    def github(self):
        github()

    @property
    def custom_info(self):
        return "Have fun!"
