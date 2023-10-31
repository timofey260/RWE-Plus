from menus import *
from menuclass import Menu, MenuWithField
from tkinter.messagebox import askyesnocancel, askyesno
import time
import requests


class ProcessManager:
    def __init__(self):
        self.run = True
        self.processes: list[LevelProcess] = []
        self.currentproccess = 0
        self.keys = [pg.K_LCTRL, pg.K_LALT, pg.K_LSHIFT]
        self.movekeys = [pg.K_LEFT, pg.K_UP, pg.K_DOWN, pg.K_RIGHT]
        self.fullscreen = settings["global"]["fullscreen"]
        loadi = loadimage(f"{path}load.png")
        self.window = pg.display.set_mode(loadi.get_size(), flags=pg.NOFRAME)
        pg.display.set_icon(loadimage(path + "icon.png"))
        self.window.blit(loadi, [0, 0])
        pg.display.flip()
        pg.display.update()
        self.items = inittolist(self.window)
        self.propcolors = getcolors()
        self.props = getprops(self.items, self.window)
        self.width = settings["global"]["width"]
        self.height = settings["global"]["height"]
        self.window = pg.display.set_mode([self.width, self.height], flags=pg.RESIZABLE | (pg.FULLSCREEN * self.fullscreen))

        os.system("cls")
        try:
            request = requests.get("https://api.github.com/repos/timofey260/RWE-Plus/releases/latest", timeout=2)
            if request.status_code == 200:
                gittag = request.json()["tag_name"]
                if tag != gittag:
                    print("A new version of RWE+ is available!")
                    print(f"Current Version: {tag}, latest: {gittag}")
                    print("https://github.com/timofey260/RWE-Plus/releases/latest\n"
                          f"Make sure you don't erase your RWE+ projects in {path2levels} and copy them somewhere!!!")
        except requests.exceptions.ConnectionError:
            print("Cannot find new RWE+ versions")
        except requests.exceptions.ReadTimeout:
            print("Cannot find new RWE+ versions")

    def update(self):
        if len(self.processes) > 0:
            self.processes[self.currentproccess].update()

    def newprocess(self, level):
        if (level != -1 and os.path.exists(level)) or level == -1:
            self.processes.append(LevelProcess(self, level))

    def closeprocess(self, process):
        self.processes.remove(process)

    def openlevel(self, level):
        self.newprocess(level)
        print("Open")

    def saveall(self, crashsave=False):
        for i in self.processes:
            i.menu.savef(crashsave)


class LevelProcess:
    def __init__(self, manager: ProcessManager, file: str|int, demo=False):
        print("Switched to new process")
        self.manager = manager
        self.surface = manager.window
        self.launchload(file)
        self.file2 = deepcopy(self.file)
        self.renderer = Renderer(self.file, manager.items, manager.props, manager.propcolors)
        self.renderer.render_all(0)
        self.undobuffer = []
        self.redobuffer = []
        self.savetimer = time.time()
        self.menu: Menu | MenuWithField = None

    def closeprocess(self):
        self.manager.closeprocess(self)

    def asktoexit(self):
        if self.file2 != self.file:
            ex = askyesnocancel("Exit from RWE+", "Do you want to save Changes?")
            if ex:
                surf.savef()
                self.closeprocess()
            elif ex is None:
                return
            else:
                self.closeprocess()
        else:
            self.closeprocess()

    def launchload(self, level):
        if level == -1:
            self.file = turntoproject(open(path + "default.txt", "r").read())
            self.file["level"] = ""
            self.file["path"] = ""
            self.file["dir"] = ""
        elif level == "":
            return
        elif level[-3:] == "txt":
            self.file = turntoproject(open(level, "r").read())
            self.file["level"] = os.path.basename(level)
            self.file["path"] = level
            self.file["dir"] = os.path.abspath(level)
        else:
            self.file = RWELevel(json.load(open(level, "r")))
            self.file["level"] = os.path.basename(level)
            self.file["path"] = level
            self.file["dir"] = os.path.abspath(level)
        self.undobuffer = []
        self.redobuffer = []

    def recievemessage(self, message):
        pass

    def undohistory(self):
        if len(self.undobuffer) == 0:
            return
        print("Undo")
        lastsize = [surf.levelwidth, surf.levelheight]
        historyelem = self.undobuffer[-1]
        '''
        Undo element data:
        [
            [path in level data],
            *[ history step
                [path to level data],
                what changed(after),
                from what changed(before)
            ], and other history steps...
        ]
        '''
        elem = historyelem[1:]
        elem.reverse()
        print("elem: ", historyelem)
        for i in elem:
            print(i)
            if len(i[0]) > 0:  # actions, used to minimize memory cost and improve performance
                match i[0][0]:
                    case ".insert":  # insert on redo, pop on undo
                        surf.data[*historyelem[0], *i[0][1:]].pop(i[1])
                        continue
                    case ".append":  # append on redo, pop on undo
                        surf.data[*historyelem[0], *i[0][1:]].pop(-1)
                        continue
                    case ".pop":  # pop on redo, insert on undo
                        surf.data[*historyelem[0], *i[0][1:]].insert(i[1], i[2])
                        continue
                    case ".move":  # pop and insert on redo, pop and insert on undo
                        surf.data[*historyelem[0], *i[0][1:]].insert(i[1],
                                                                     surf.data[*historyelem[0], *i[0][1:]].pop(i[2]))
                        continue
            surf.data[*historyelem[0], *i[0]] = i[1][1]
        self.redobuffer.append(deepcopy(self.undobuffer.pop()))
        if [surf.levelwidth, surf.levelheight] != lastsize:
            surf.renderer.set_surface([image1size * surf.levelwidth, image1size * surf.levelheight])
        surf.onundo()
        if MenuWithField in type(surf).__bases__:
            surf.renderer.render_all(surf.layer)
            surf.rfa()
            if hasattr(surf, "rebuttons"):
                surf.rebuttons()

    def redohistory(self):
        if len(self.redobuffer) == 0:
            return
        print("Redo")
        lastsize = [surf.levelwidth, surf.levelheight]
        historyelem = self.redobuffer[-1]

        elem = historyelem[1:]
        elem.reverse()
        for i in elem:
            print(i)
            if len(i[0]) > 0:  # actions, used to minimize memory cost and improve performance
                match i[0][0]:
                    case ".insert":  # insert on redo, pop on undo
                        surf.data[*historyelem[0], *i[0][1:]].insert(i[1], i[2])
                        continue
                    case ".append":  # append on redo, pop on undo
                        surf.data[*historyelem[0], *i[0][1:]].append(i[1])
                        continue
                    case ".pop":  # pop on redo, insert on undo
                        surf.data[*historyelem[0], *i[0][1:]].pop(i[1])
                        continue
                    case ".move":  # pop and insert on redo, pop and insert on undo
                        surf.data[*historyelem[0], *i[0][1:]].insert(i[2],
                                                                     surf.data[*historyelem[0], *i[0][1:]].pop(i[1]))
                        continue
            surf.data[*historyelem[0], *i[0]] = i[1][0]

        self.undobuffer.append(deepcopy(self.redobuffer.pop()))
        if [surf.levelwidth, surf.levelheight] != lastsize:
            surf.renderer.set_surface([image1size * surf.levelwidth, image1size * surf.levelheight])
        surf.onredo()
        if MenuWithField in type(surf).__bases__:
            surf.renderer.render_all(surf.layer)
            surf.rfa()
            if hasattr(surf, "rebuttons"):
                surf.rebuttons()

    def keypress(self):
        pressed = ""
        ctrl = pg.key.get_pressed()[pg.K_LCTRL]
        # shift = pg.key.get_pressed()[pg.K_LSHIFT]
        for i in hotkeys["global"].keys():
            key = i.replace("@", "").replace("+", "")
            if i == "unlock_keys":
                continue
            if int(i.find("+") != -1) - int(ctrl) == 0:
                if pg.key.get_pressed()[getattr(pg, key)]:
                    pressed = hotkeys["global"][i]
        for i in hotkeys[surf.menu].keys():
            key = i.replace("@", "").replace("+", "")
            if i == "unlock_keys":
                continue
            if int(i.find("+") != -1) - int(ctrl) == 0:
                if pg.key.get_pressed()[getattr(pg, key)]:
                    pressed = hotkeys[surf.menu][i]
                    surf.send(pressed)
        if len(pressed) > 0 and pressed[0] == "/" and surf.menu != "LD":
            surf.message = pressed[1:]
        match pressed.lower():
            case "undo":
                self.undohistory()
            case "redo":
                self.redohistory()
            case "quit":
                self.asktoexit()
            case "reload":
                surf.reload()
            case "save":
                surf.savef()
                self.file2 = deepcopy(self.file)
            case "new":
                print("New")
                surf.savef()
                run = False
            case "open":
                self.manager.openlevel(surf.asksaveasfilename(defaultextension=[".txt", ".wep"]))

    def launch(self, level):
        self.manager.newprocess(level)

    def doevents(self, dropfile=True):
        global surf, render
        for event in pg.event.get():
            match event.type:
                case pg.DROPFILE:
                    if dropfile:
                        self.manager.openlevel(event.file)
                    else:
                        if event.file is not None and os.path.exists(event.file):
                            self.launch(event.file)
                case pg.QUIT:
                    self.asktoexit()
                case pg.WINDOWRESIZED:
                    surf.resize()
                case pg.KEYDOWN:
                    if event.key not in self.manager.keys:
                        if widgets.keybol:
                            widgets.keybol = False
                            self.keypress()
                case pg.KEYUP:
                    if event.key not in self.manager.keys:
                        if not widgets.keybol:
                            widgets.keybol = True
                case pg.MOUSEBUTTONDOWN:
                    if event.button == 4:
                        surf.send("SU")
                    elif event.button == 5:
                        surf.send("SD")

    def update(self):
        self.doevents()
        if self.menu.message != "":
            match self.menu.message:
                case "undo":
                    self.undohistory()
                case "redo":
                    self.redohistory()
                case "%":
                    self.menu = HK(self.surface, self.renderer, self.menu.menu)
                case "quit":
                    self.asktoexit()
                case "fc":
                    self.manager.fullscreen = not self.manager.fullscreen
                    window = pg.display.set_mode([self.manager.width, self.manager.height], flags=pg.RESIZABLE | (pg.FULLSCREEN * self.manager.fullscreen))
                    # pg.display.toggle_fullscreen()
                    self.menu.resize()
                case "save":
                    self.menu.savef()
                    self.file2 = deepcopy(self.file)
                case "saveas":
                    self.menu.saveasf()
                    self.file2 = deepcopy(self.file)
                case "savetxt":
                    self.menu.savef_txt()
                    self.file2 = deepcopy(self.file)
                case _:
                    if self.menu.message in menulist:
                        surf = getattr(sys.modules[__name__], self.menu.message)(self)
                    else:
                        self.menu.send(self.menu.message)
            surf.message = ""
        if len(surf.historybuffer) > 0:
            surf.historybuffer.reverse()
            undobuffer.extend(surf.historybuffer)
            surf.historybuffer = []
            redobuffer = []
            undobuffer = undobuffer[-globalsettings["historylimit"]:]

        if not pg.key.get_pressed()[pg.K_LCTRL]:
            for i in surf.uc:
                if pg.key.get_pressed()[i]:
                    keypress(window)
        if settings[surf.menu].get("menucolor") is not None:
            window.fill(pg.color.Color(settings[surf.menu]["menucolor"]))
        else:
            window.fill(pg.color.Color(settings["global"]["color"]))
        surf.blit()
        if 1 < globalsettings["autosavedelay"] < time.time() - savetimer:
            print("Autosaving...")
            surf.savef()
            savetimer = time.time()
        pg.display.flip()
        pg.display.update()