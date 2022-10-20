import os, sys
from widgets import *
import copy
from menus import *
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import *

from lingotojson import *
from files import settings, hotkeys, path, application_path

bol = True
run = True
keys = [pg.K_LCTRL, pg.K_LALT, pg.K_LSHIFT]
movekeys = [pg.K_LEFT, pg.K_UP, pg.K_DOWN, pg.K_RIGHT]
fullscreen = settings["global"]["fullscreen"]


def keypress(window, surf, file, file2, level):
    global run
    pressed = ""
    ctrl = pg.key.get_pressed()[pg.K_LCTRL]
    # shift = pg.key.get_pressed()[pg.K_LSHIFT]
    for i in hotkeys["global"].keys():
        if i[-1] == "+":
            if ctrl == 1:
                if pg.key.get_pressed()[getattr(pg, i[:-1])]:
                    pressed = hotkeys["global"][i]
        else:
            if ctrl == 0:
                if pg.key.get_pressed()[getattr(pg, i)]:
                    pressed = hotkeys["global"][i]
    for i in hotkeys[surf.menu].keys():
        if i == "unlock_keys":
            continue
        elif i[-1] == "+":
            if ctrl == 1:
                if pg.key.get_pressed()[getattr(pg, i[:-1])]:
                    pressed = hotkeys[surf.menu][i]
                    surf.send(pressed)
        else:
            if ctrl == 0:
                if pg.key.get_pressed()[getattr(pg, i)]:
                    pressed = hotkeys[surf.menu][i]
                    surf.send(pressed)
    if len(pressed) > 0 and pressed[0] == "/" and surf.menu != "LD":
        surf.message = pressed[1:]
    match pressed.lower():
        case "quit":
            asktoexit(file, file2)
        case "reload":
            surf.reload()
        case "save":
            save(file)
            file2 = copy.deepcopy(file)
        case "open":
            if surf.menu == "MN":
                launch(askopenfilename(defaultextension="txt",
                                       initialdir=os.path.dirname(os.path.abspath(__file__)) + "\LevelEditorProjects"))
        case "new":
            run = False


def asktoexit(file, file2):
    global run
    if file2 != file:
        ex = askyesnocancel("Exit from RWE+", "Do you want to save Changes?")
        if ex:
            open(asksaveasfilename(defaultextension="wep"), "w").write(json.dumps(file))
            sys.exit(0)
        elif ex is None:
            return
        else:
            sys.exit(0)
    else:
        sys.exit(0)


def launch(level):
    global bol, surf, fullscreen
    if level == -1:
        file = turntoproject(open(path + "default.txt", "r").read())
        file["level"] = ""
        file["path"] = ""
        file["dir"] = ""
    elif level == "":
        return
    elif level[-3:] == "txt":
        file = turntoproject(open(level, "r").read())
        file["level"] = os.path.basename(level)
        file["path"] = level
        file["dir"] = os.path.abspath(level)
    else:
        file = json.load(open(level, "r"))
        file["level"] = os.path.basename(level)
        file["path"] = level
        file["dir"] = os.path.abspath(level)
    items = inittolist(application_path + "\\drizzle\\Data\\Graphics\\init.txt")
    file2 = copy.deepcopy(file)
    width = settings["global"]["width"]
    height = settings["global"]["height"]
    window = pg.display.set_mode([width, height], flags=pg.RESIZABLE + (pg.FULLSCREEN * fullscreen))
    pg.display.set_icon(pg.image.load(application_path + "\\icon.png"))
    surf = MN(window, file)
    run = True
    while run:
        for event in pg.event.get():
            match event.type:
                case pg.QUIT:
                    asktoexit(file, file2)
                case pg.WINDOWRESIZED:
                    surf.resize()
                case pg.KEYDOWN:
                    # print(pg.key.name(event.key))
                    # print(event.key not in [pg.K_LCTRL, pg.K_LALT, pg.K_LSHIFT])
                    if event.key not in keys:
                        if bol:
                            bol = False
                            keypress(window, surf, file, file2, level)
                case pg.KEYUP:
                    if event.key not in keys:
                        if not bol:
                            bol = True
                case pg.MOUSEBUTTONDOWN:
                    if event.button == 4:
                        surf.send("SU")
                    elif event.button == 5:
                        surf.send("SD")
        if surf.message != "":
            match surf.message:
                case "quit":
                    asktoexit(file, file2)
                case "MN":
                    surf = MN(window, file)
                case "GE":
                    surf = GE(window, file)
                case "TE":
                    surf = TE(window, file, items)
                case "LE":
                    surf = LE(window, file)
                case "LS":
                    surf = LS(window, file, items)
                case "FE":
                    surf = FE(window, file, items)
                case "CE":
                    surf = CE(window, file)
                case "fc":
                    fullscreen = not fullscreen
                    window = pg.display.set_mode([width, height], flags=pg.RESIZABLE + (pg.FULLSCREEN * fullscreen))
                    # pg.display.toggle_fullscreen()
                    surf.resize()
                case "save":
                    save(file)
                    file2 = copy.deepcopy(file)
                case "savetxt":
                    save_txt(file)
                    file2 = copy.deepcopy(file)
            surf.message = ""

        if not pg.key.get_pressed()[pg.K_LCTRL]:
            for i in surf.uc:
                if pg.key.get_pressed()[i]:
                    keypress(window, surf, file, file2, level)

        window.fill(pg.color.Color(settings["global"]["color"]))
        surf.blit()
        pg.display.flip()
        pg.display.update()


def save_txt(file):
    savedest = asksaveasfilename(defaultextension="txt")
    if savedest != "":
        turntolingo(file, open(savedest, "w"))


def save(file):
    print(file["path"])
    if file["path"] != "":
        open(file["path"], "w").write(json.dumps(file))
    else:
        savedest = asksaveasfilename(defaultextension="wep")
        if savedest != "":
            open(savedest, "w").write(json.dumps(file))
            file["level"] = os.path.basename(savedest)
            file["path"] = savedest
            file["dir"] = os.path.abspath(savedest)


def loadmenu():
    global surf
    run = True
    width = 400
    height = 200
    window = pg.display.set_mode([width, height], flags=pg.RESIZABLE)
    surf = load(window, {"path": ""})
    while run:
        for event in pg.event.get():
            match event.type:
                case pg.QUIT:
                    exit(0)
                case pg.WINDOWRESIZED:
                    surf.resize()
        match surf.message:
            case "new":
                launch(-1)
            case "open":
                return
        keypress(window, surf, "", "", -1)
        window.fill(pg.color.Color(settings["global"]["color"]))
        surf.blit()
        pg.display.flip()
        pg.display.update()
    pg.quit()
    exit(0)


if __name__ == "__main__":
    args = sys.argv
    if len(args) == 1:
        loadmenu()
        launch(askopenfilename(defaultextension="txt",
                               initialdir=application_path + "\\LevelEditorProjects"))
    elif len(args) == 2:
        if args[1] == "-h": # there needs to be argument parser
            print(open(path + "helpmessage.txt", "r").read())
        else:
            launch(args[1])
    else:
        pass
