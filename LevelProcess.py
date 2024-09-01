from menus import *
from menuclass import Menu, MenuWithField
import time
import requests
from tkinter import filedialog


class ProcessManager:
    def __init__(self):
        global godres
        self.run = True
        self.processes: list[LevelProcess] = []
        self.currentproccess = 0
        self.keys = [pg.K_LCTRL, pg.K_LALT, pg.K_LSHIFT]
        self.movekeys = [pg.K_LEFT, pg.K_UP, pg.K_DOWN, pg.K_RIGHT]
        self.fullscreen = settings["global"]["fullscreen"]
        loadi = loadimage(os.path.join(path, "load.png"))
        self.window = pg.display.set_mode(loadi.get_size(), flags=pg.NOFRAME)
        self.window.blit(loadi, [0, 0])

        pg.display.set_icon(loadimage(os.path.join(path, "icon.png")))
        pg.display.flip()
        pg.display.update()
        self.tiles = inittolist(self.window)
        self.propcolors = getcolors()
        self.props = getprops(self.tiles, self.window)
        self.effects = solveeffects(e)
        self.width = settings["global"]["width"]
        self.height = settings["global"]["height"]
        pg.quit()
        pg.font.init()
        self.window = pg.display.set_mode([self.width, self.height],
                                          flags=pg.RESIZABLE | (pg.FULLSCREEN * self.fullscreen))
        self.notifications: list[widgets.Notification] = []

        self.selectprocess = False
        self.processbuttons: list[widgets.Button] = []
        self.processscroll = 0
        godres = pg.transform.scale(god, pg.display.get_window_size())

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
        self.notify("Everything loaded successfully!")

    def gotoselectprocess(self):
        self.selectprocess = True
        self.processbuttons = []
        widgets.resetpresses()
        for indx, process in enumerate(self.processes):
            process: LevelProcess
            x = indx % 3 * 33
            y = (indx // 3 - self.processscroll) * 33
            self.processbuttons.append(widgets.Button(self.window, pg.Rect([x, y, 33, 33]), gray, process.file["level"],
                                                      tooltip=process.file["path"],
                                                      icon=process.renderer.surf_geo,
                                                      onpress=self.gotoprocess))
            self.processbuttons[-1].buttondata = indx
        for i in self.processbuttons:
            i.resize()

    def gotoprocess(self, button: widgets.Button):
        self.selectprocess = False
        self.currentproccess = button.buttondata
        self.processbuttons = []

    def processesmenuupdate(self):
        self.window.fill(color)
        for i in self.processbuttons:
            i.blitshadow()
        for i in self.processbuttons:
            i.blit()
        for i in self.processbuttons:
            if i.blittooltip():
                break
        for event in pg.event.get():
            match event.type:
                case pg.KEYDOWN:
                    if event.key in [pg.K_RETURN, pg.K_ESCAPE]:
                        self.selectprocess = False
                        self.processbuttons = []
                        return
                case pg.MOUSEBUTTONDOWN:
                    if event.button == 4:
                        self.processscroll = max(self.processscroll - 1, 0)
                        self.gotoselectprocess()
                    elif event.button == 5:
                        self.processscroll = min(self.processscroll + 1, len(self.processbuttons) // 3)
                        self.gotoselectprocess()

        if not pg.mouse.get_pressed(3)[0] and not widgets.enablebuttons:
            widgets.enablebuttons = True

    def update(self):
        if len(self.processes) <= 0:
            exit()
        if self.selectprocess:
            self.processesmenuupdate()
        else:
            self.mainprocessupdate()

        if len(self.notifications) > 0:
            self.notifications[0].blit()
            if self.notifications[0].delete:
                self.notifications.pop(0)
        pg.display.flip()
        pg.display.update()

    def mainprocessupdate(self):
        try:
            self.currentproccess = widgets.restrict(self.currentproccess, 0, len(self.processes) - 1)
            self.mainprocess.update()
        except Exception as e:
            # extra save level in case of eny crashes
            f = open(os.path.join(application_path, "CrashLog.txt"), "w")
            f.write(traceback.format_exc())
            f.write("This is why RWE+ crashed^^^\nSorry")
            saved = False
            if globalsettings["saveoncrash"] and not debugmode:
                self.saveall(True)
                saved = True
            traceback.print_exc()

            if not saved:
                ex = self.mainprocess.menu.askstr("Oops! RWE+ seems to be crashed!"
                              " Do you want to save level you opened?(y/n)")
                if ex.lower() == "y":
                    try:
                        self.mainprocess.menu.savef()
                    except:
                        print("Cannot save!!! sorry")
                        self.closeprocess(self.mainprocess)
                        raise e
            try:
                self.mainprocess.update()
            except:
                self.saveall(True)
                raise

    def newprocess(self, level):
        if level != -1 and os.path.exists(level):
            self.processes.append(LevelProcess(self, level))
            self.currentproccess = len(self.processes) - 1
        else:
            self.processes.append(LevelProcess(self, level, True))
            self.currentproccess = len(self.processes) - 1
        self.printprocesses()
        self.mainprocess.menu.recaption()
        self.notify("Created new Process!")

    def closeprocess(self, process):
        self.processes.remove(process)
        self.currentproccess = widgets.restrict(self.currentproccess, 0, len(self.processes) - 1)
        if len(self.processes) > 0:
            self.mainprocess.menu.recaption()

    def openlevel(self, level):
        self.newprocess(level)
        self.notify("Opened level new Process!")

    def saveall(self, crashsave=False):
        for i in self.processes:
            i.menu.savef(crashsave=crashsave)

    def openfullscreen(self):
        self.fullscreen = not self.fullscreen
        self.window = pg.display.set_mode([self.width, self.height],
                                          flags=pg.RESIZABLE | (pg.FULLSCREEN * self.fullscreen))

    def printprocesses(self):
        print(", ".join([str(i) for i in self.processes]))

    @property
    def mainprocess(self):
        return self.processes[self.currentproccess]

    def notify(self, *args):
        print(*args)
        self.notifications.append(widgets.Notification(self.window, ''.join(args)))

    def swichprocess(self):
        widgets.keybol = True
        self.gotoselectprocess()
        pg.display.set_caption("RWE+ | Process select")
        self.notify("Opened process select")


class LevelProcess:
    def __init__(self, manager: ProcessManager, file: str | int, demo=False):
        print("Switched to new process")
        self.manager = manager
        try:
            self.launchload(file)
        except FileNotFoundError:
            self.manager.notify(f"File {file} not found! Action stopped")
            return
        self.demo = demo
        self.surface = manager.window
        self.file2 = deepcopy(self.file)
        self.undobuffer = []
        self.redobuffer = []
        self.savetimer = time.time()
        self.renderer = Renderer(self)
        self.renderer.render_all(0)
        if demo:
            self.menu: Menu | MenuWithField = LoadMenu(self)
        else:
            self.menu: Menu | MenuWithField = MN(self)

    def __str__(self):
        if self.file["level"] == "":
            return f'(Unnamed with {self.menu.menu})'
        else:
            return f'({self.file["level"]} with {self.menu.menu})'

    def closeprocess(self):
        self.manager.closeprocess(self)

    def asktoexit(self):
        if self.file2 != self.file and not self.demo:
            try:
                ex = self.menu.askstr("Save before closing? y/n", defaulttext="y", savelevel=False)
                #ex = askyesnocancel("Exit from RWE+", "Do you want to save Changes?")
            except:
                print("why")
            if ex.lower() == "y":
                self.menu.savef()
                self.closeprocess()
            elif ex is None:
                return
            else:
                self.closeprocess()
        else:
            self.closeprocess()

    def launchload(self, level):
        if level == -1:
            self.file = turntoproject(open(os.path.join(path, "default.txt"), "r").read())
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
            self.addrecent(level)
        else:
            self.file = RWELevel(json.load(open(level, "r")))
            self.file["level"] = os.path.basename(level)
            self.file["path"] = level
            self.file["dir"] = os.path.abspath(level)
            self.addrecent(level)
        self.undobuffer = []
        self.redobuffer = []

    def addrecent(self, file):
        datadir = appdirs.user_data_dir("RWE+", "timofey26", roaming=True)
        recentfile = os.path.join(datadir, "recentProjects.json")
        if not os.path.exists(recentfile):
            os.makedirs(datadir, exist_ok=True)
            open(recentfile, "w").write("{ \"files\": [] }")
        data = json.load(open(recentfile, "r"))
        filename = os.path.basename(file)
        for i, item in enumerate(data["files"]):
            if item["path"] == file:
                data["files"].pop(i)
        data["files"].insert(0, {"path": file, "name": filename})
        json.dump(data, open(recentfile, "w"), indent=4)

    def recievemessage(self, message):
        match message:
            case "undo":
                self.undohistory()
            case "redo":
                self.redohistory()
            case "%":
                self.menu = HK(self, self.menu.menu)
            case "quit":
                self.asktoexit()
            case "fc":
                self.manager.openfullscreen()
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
            case "newProcess":
                self.manager.newprocess(-1)
            case "swichprocess":
                self.manager.swichprocess()
            case "rerender_all":
                self.renderer.render_all(self.menu.layer)
                self.menu.rfa()
            case "RELOAD":
                self.menu.reload()
            case "new":
                self.__init__(self.manager, -1)
            case "openNewProcess":
                if globalsettings["rwefilebrowser"] or islinux:
                    file = self.menu.asksaveasfilename(defaultextension=[".txt", ".wep"])
                else:
                    file = filedialog.askopenfilename(initialdir=path2levels,
                                                      defaultextension=".wep",
                                                      filetypes=[("Leditor unrendered level", ".txt"),
                                                                 ("World Editor Project", ".wep")])
                if file is not None and os.path.exists(file):
                    self.manager.newprocess(file)
            case "open":
                if globalsettings["rwefilebrowser"] or islinux:
                    file = self.menu.asksaveasfilename(defaultextension=[".txt", ".wep"])
                else:
                    file = filedialog.askopenfilename(initialdir=path2levels,
                                                      defaultextension=".wep",
                                                      filetypes=[("Leditor unrendered level", ".txt"),
                                                                 ("World Editor Project", ".wep")])
                if file and os.path.exists(file):
                    self.__init__(self.manager, file)
            case "load":
                self.menu = LoadMenu(self)
            case _:
                if message in menulist and self.menu.menu != "LD":
                    self.menu = getattr(sys.modules[__name__], message)(self)
                else:
                    self.menu.send(message)

    def undohistory(self):
        if len(self.undobuffer) == 0:
            return
        lastsize = [self.menu.levelwidth, self.menu.levelheight]
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
        def checkmatrixforchanges(old, new):
            area = [[True for _ in range(self.menu.levelheight)] for _ in range(self.menu.levelwidth)]
            changes = False
            for xp in range(len(area)):
                for yp in range(len(area[0])):
                    if old[xp][yp] != new[xp][yp]:
                        changes = True
                        area[xp][yp] = False
            return changes, area

        elem = historyelem[1:]
        elem.reverse()
        # print("elem: ", historyelem)
        lastdata = deepcopy(self.menu.data)
        for i in elem:
            # print(i)
            if len(i[0]) > 0:  # actions, used to minimize memory cost and improve performance
                match i[0][0]:
                    case ".insert":  # insert on redo, pop on undo
                        self.menu.data[*historyelem[0], *i[0][1:]].pop(i[1])
                        continue
                    case ".append":  # append on redo, pop on undo
                        self.menu.data[*historyelem[0], *i[0][1:]].pop(-1)
                        continue
                    case ".pop":  # pop on redo, insert on undo
                        self.menu.data[*historyelem[0], *i[0][1:]].insert(i[1], i[2])
                        continue
                    case ".move":  # pop and insert on redo, pop and insert on undo
                        self.menu.data[*historyelem[0], *i[0][1:]].insert(i[1],
                                                                          self.menu.data[
                                                                              *historyelem[0], *i[0][1:]].pop(i[2]))
                        continue
            self.menu.data[*historyelem[0], *i[0]] = i[1][1]
        self.redobuffer.append(deepcopy(self.undobuffer.pop()))
        rerendered = True
        if [self.menu.levelwidth, self.menu.levelheight] != lastsize:
            self.renderer.set_surface([image1size * self.menu.levelwidth, image1size * self.menu.levelheight])
            self.renderer.render_all(self.menu.layer)
            rerendered = False
        self.menu.onundo()
        if rerendered:
            checkgeo, geoarea = checkmatrixforchanges(lastdata["GE"], self.menu.data["GE"])
            check, area = checkmatrixforchanges(lastdata["TE", "tlMatrix"], self.menu.data["TE", "tlMatrix"])
            if checkgeo:
                self.renderer.geo_render_area(geoarea, self.menu.layer)
                for xp, x in enumerate(geoarea):
                    for yp, y in enumerate(x):
                        area[xp][yp] = area[xp][yp] and y

            if checkgeo or check:
                self.renderer.tiles_render_area(area, self.menu.layer)
            if lastdata["PR"] != self.menu.data["PR"]:
                self.renderer.props_full_render(self.menu.layer)
            if lastdata["FE"] != self.menu.data["FE"]:
                self.renderer.rerendereffect()

            if MenuWithField in type(self.menu).__bases__:
                # self.menu.renderer.render_all(self.menu.layer)
                self.menu.rfa()
            self.manager.notify("Done undo")

    def redohistory(self):
        if len(self.redobuffer) == 0:
            return
        lastsize = [self.menu.levelwidth, self.menu.levelheight]
        historyelem = self.redobuffer[-1]

        def checkmatrixforchanges(old, new):
            area = [[True for _ in range(self.menu.levelheight)] for _ in range(self.menu.levelwidth)]
            changes = False
            for xp in range(len(area)):
                for yp in range(len(area[0])):
                    if old[xp][yp] != new[xp][yp]:
                        changes = True
                        area[xp][yp] = False
            return changes, area

        elem = historyelem[1:]
        elem.reverse()
        lastdata = deepcopy(self.menu.data)
        for i in elem:
            # print(i)
            if len(i[0]) > 0:  # actions, used to minimize memory cost and improve performance
                match i[0][0]:
                    case ".insert":  # insert on redo, pop on undo
                        self.menu.data[*historyelem[0], *i[0][1:]].insert(i[1], i[2])
                        continue
                    case ".append":  # append on redo, pop on undo
                        self.menu.data[*historyelem[0], *i[0][1:]].append(i[1])
                        continue
                    case ".pop":  # pop on redo, insert on undo
                        self.menu.data[*historyelem[0], *i[0][1:]].pop(i[1])
                        continue
                    case ".move":  # pop and insert on redo, pop and insert on undo
                        self.menu.data[*historyelem[0], *i[0][1:]].insert(i[2],
                                                                          self.menu.data[
                                                                              *historyelem[0], *i[0][1:]].pop(i[1]))
                        continue
            self.menu.data[*historyelem[0], *i[0]] = i[1][0]

        self.undobuffer.append(deepcopy(self.redobuffer.pop()))
        rerendered = True
        if [self.menu.levelwidth, self.menu.levelheight] != lastsize:
            self.renderer.set_surface([image1size * self.menu.levelwidth, image1size * self.menu.levelheight])
            self.renderer.render_all(self.menu.layer)
            rerendered = False
        self.menu.onundo()
        if rerendered:
            checkgeo, geoarea = checkmatrixforchanges(lastdata["GE"], self.menu.data["GE"])
            check, area = checkmatrixforchanges(lastdata["TE", "tlMatrix"], self.menu.data["TE", "tlMatrix"])
            if checkgeo:
                self.renderer.geo_render_area(geoarea, self.menu.layer)
                for xp, x in enumerate(geoarea):
                    for yp, y in enumerate(x):
                        area[xp][yp] = area[xp][yp] and y

            if checkgeo or check:
                self.renderer.tiles_render_area(area, self.menu.layer)
            if lastdata["PR"] != self.menu.data["PR"]:
                self.renderer.props_full_render(self.menu.layer)
            if lastdata["FE"] != self.menu.data["FE"]:
                self.renderer.rerendereffect()

        if MenuWithField in type(self.menu).__bases__:
            # self.menu.renderer.render_all(self.menu.layer)
            self.menu.rfa()
        self.manager.notify("Done redo")

    def keypress(self):
        pressed = ""
        ctrl = pg.key.get_pressed()[pg.K_LCTRL]
        shift = pg.key.get_pressed()[pg.K_LSHIFT]
        for i in hotkeys["global"].keys():
            if i == "unlock_keys":
                continue
            key = i.replace("@", "").replace("+", "").replace("-", "")
            if int(i.find("+") != -1) - int(ctrl) == 0 and int(i.find("-") != -1) - int(shift) == 0:
                if pg.key.get_pressed()[getattr(pg, key)]:
                    pressed = hotkeys["global"][i]
        for i in hotkeys[self.menu.menu].keys():
            if i == "unlock_keys":
                continue
            key = i.replace("@", "").replace("+", "").replace("-", "")
            if int(i.find("+") != -1) - int(ctrl) == 0 and int(i.find("-") != -1) - int(shift) == 0:
                if pg.key.get_pressed()[getattr(pg, key)]:
                    pressed = hotkeys[self.menu.menu][i]
                    self.menu.send(pressed)
        if len(pressed) > 0 and pressed[0] == "/":
            self.recievemessage(pressed[1:])
            return

    def launch(self, level):
        self.manager.newprocess(level)

    def doevents(self, dropfile=True):
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
                    global godres
                    godres = pg.transform.scale(god, pg.display.get_window_size())
                    self.menu.resize()
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
                        self.menu.scroll_up()
                    elif event.button == 5:
                        self.menu.scroll_down()

    def update(self):
        self.doevents()
        if globalsettings["godmode"]:
            self.surface.blit(godres, [0, 0])
        else:
            self.menu.blitbefore()
        if not pg.key.get_pressed()[pg.K_LCTRL]:
            for i in self.menu.uc:
                if pg.key.get_pressed()[i]:
                    self.keypress()
        self.menu.blit()
        if 1 < globalsettings["autosavedelay"] < time.time() - self.savetimer and not self.demo:
            print("Autosaving...")
            self.menu.savef()
            self.savetimer = time.time()
            self.manager.notify("Autosaved!")
