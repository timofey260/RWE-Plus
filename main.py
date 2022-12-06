import os, sys
from widgets import *
import copy
from menus import *
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import *
import argparse

from lingotojson import *
from files import settings, hotkeys, path, application_path

bol = True
run = True
keys = [pg.K_LCTRL, pg.K_LALT, pg.K_LSHIFT]
movekeys = [pg.K_LEFT, pg.K_UP, pg.K_DOWN, pg.K_RIGHT]
fullscreen = settings["global"]["fullscreen"]

version = "v1.6 alpha"


def keypress(window, surf, file, file2, level):
    global run
    pressed = ""
    ctrl = pg.key.get_pressed()[pg.K_LCTRL]
    # shift = pg.key.get_pressed()[pg.K_LSHIFT]
    for i in hotkeys["global"].keys():
        key = i.replace("@", "").replace("+", "")
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
    items = inittolist()
    propcolors = getcolors()
    props = getprops(items)
    file2 = copy.deepcopy(file)
    width = settings["global"]["width"]
    height = settings["global"]["height"]
    window = pg.display.set_mode([width, height], flags=pg.RESIZABLE + (pg.FULLSCREEN * fullscreen))
    pg.display.set_icon(pg.image.load(application_path + "\\files\\icon.png"))
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
                case "LP":
                    surf = LP(window, file)
                case "EE":
                    surf = EE(window, file)
                case "PE":
                    surf = PE(window, file, props, propcolors)
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

        if settings[surf.menu].get("menucolor") is not None:
            window.fill(pg.color.Color(settings[surf.menu]["menucolor"]))
        else:
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
        open(os.path.splitext(file["path"])[0] + ".wep", "w").write(json.dumps(file))
        file["path"] = os.path.splitext(file["path"])[0] + ".wep"
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


def new():
    loadmenu()
    launch(askopenfilename(defaultextension="txt",
                           initialdir=application_path + "\\LevelEditorProjects"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="RWE+ console", description="maybe a better, than official LE.")
    parser.version = version
    parser.add_argument("filename", type=str, nargs="?", help="level to load")
    parser.add_argument("-n", "--new", help="opens new file", dest="new", action="store_true")
    parser.add_argument("-v", "--version", help="shows current version and exits", action="version")
    parser.add_argument("--render", "-r", dest="renderfiles", metavar="file", nargs="*", type=str, help="renders levels with drizzle.")
    parser.parse_args()
    args = parser.parse_args()

    if args.new:
        new()
    if args.renderfiles is not None:
        s = application_path + "\\drizzle\\Drizzle.ConsoleApp.exe render "
        for i in args.renderfiles:
            s += i + " "
        os.system(s)
        os.system("explorer " + path2renderedlevels)
        exit(0)
    if args.filename is not None:
        try:
            launch(args.filename)
        except FileNotFoundError:
            print("File not found!")
    else:
        new()
