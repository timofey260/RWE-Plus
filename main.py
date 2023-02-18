import copy
import requests
from menus import *
from tkinter.messagebox import askyesnocancel
import argparse
from path_dict import PathDict
from lingotojson import *
from files import settings, hotkeys, path, application_path

bol = True
run = True
keys = [pg.K_LCTRL, pg.K_LALT, pg.K_LSHIFT]
movekeys = [pg.K_LEFT, pg.K_UP, pg.K_DOWN, pg.K_RIGHT]
fullscreen = settings["global"]["fullscreen"]
file = ""
file2 = ""
undobuffer = []
redobuffer = []

tag = "2.0"
version = "version: " + tag

a = [[69], [[[[1, []], [0, []], [0, []]], [[1, []], [0, []], [0, []]], [[1, []], [1, []], [0, []]], [[1, []], [1, []], [0, []]], [[1, []], [1, []], [0, []]], [[0, []], [1, []], [0, []]], [[1, []], [1, []], [0, []]], [[1, []], [1, []], [1, []]], [[1, []], [1, []], [1, []]], [[1, []], [0, []], [1, []]], [[1, []], [0, []], [1, []]], [[0, []], [0, []], [1, []]], [[0, []], [0, []], [1, []]], [[0, []], [1, []], [1, []]], [[0, []], [1, []], [1, []]], [[0, []], [1, []], [1, []]], [[0, []], [1, []], [1, []]], [[1, []], [1, []], [1, []]], [[0, []], [0, []], [1, []]], [[0, []], [0, []], [1, []]], [[1, []], [1, []], [1, []]], [[1, []], [1, []], [1, []]], [[1, []], [1, []], [1, []]], [[1, []], [1, []], [1, []]], [[1, []], [1, []], [1, []]], [[1, []], [1, []], [1, []]], [[1, []], [1, []], [1, []]], [[0, []], [1, []], [1, []]], [[0, []], [0, []], [1, []]], [[0, []], [1, []], [1, []]], [[1, []], [1, []], [1, []]], [[1, []], [1, []], [1, []]], [[1, []], [1, []], [1, []]], [[1, []], [0, []], [1, []]], [[1, []], [0, []], [0, []]], [[1, []], [0, []], [0, []]], [[1, []], [0, []], [0, []]], [[1, []], [0, []], [0, []]], [[1, []], [0, []], [0, []]], [[1, []], [0, []], [0, []]], [[1, []], [0, []], [0, []]], [[1, []], [0, []], [0, []]], [[1, []], [0, []], [0, []]]],
            [[[1, []], [0, []], [0, []]], [[1, []], [0, []], [0, []]], [[1, []], [1, []], [0, []]], [[1, []], [1, []], [0, []]], [[1, []], [1, []], [0, []]], [[0, []], [1, []], [0, []]], [[1, []], [1, []], [0, []]], [[1, []], [1, []], [1, []]], [[1, []], [1, []], [1, []]], [[1, []], [0, []], [1, []]], [[0, []], [0, []], [1, []]], [[0, []], [0, []], [1, []]], [[0, []], [0, []], [1, []]], [[0, []], [1, []], [1, []]], [[0, []], [1, []], [1, []]], [[0, []], [1, []], [1, []]], [[0, []], [1, []], [1, []]], [[0, []], [1, []], [1, []]], [[0, []], [0, []], [1, []]], [[0, []], [0, []], [1, []]], [[1, []], [1, []], [1, []]], [[1, []], [1, []], [1, []]], [[1, []], [1, []], [1, []]], [[1, []], [1, []], [1, []]], [[1, []], [1, []], [1, []]], [[1, []], [1, []], [1, []]], [[1, []], [1, []], [1, []]], [[0, []], [1, []], [1, []]], [[0, []], [0, []], [1, []]], [[0, []], [1, []], [1, []]], [[1, []], [1, []], [1, []]], [[1, []], [1, []], [1, []]], [[1, []], [1, []], [1, []]], [[1, []], [0, []], [1, []]], [[1, []], [0, []], [0, []]], [[1, []], [0, []], [0, []]], [[1, []], [0, []], [0, []]], [[1, []], [0, []], [0, []]], [[1, []], [0, []], [0, []]], [[1, []], [0, []], [0, []]], [[1, []], [0, []], [0, []]], [[1, []], [0, []], [0, []]], [[1, []], [0, []], [0, []]]]]]


def keypress(window, surf):
    global run, file, file2, redobuffer, undobuffer
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
            undohistory(surf)
        case "redo":
            redohistory(surf)
        case "quit":
            asktoexit(file, file2)
        case "reload":
            surf.reload()
        case "save":
            surf.savef()
            file2 = copy.deepcopy(file)
        case "new":
            run = False

def undohistory(surf: menu | menu_with_field):
    global undobuffer, redobuffer, file
    if len(undobuffer) == 0:
        return
    print("undo")
    historyelem = undobuffer[-1]
    pathdict = PathDict(surf.data)
    for i in historyelem[1:]:
        pathdict[*historyelem[0], *i[0]] = i[1][1]
    file = copy.deepcopy(pathdict.data)
    surf.datalast = copy.deepcopy(pathdict.data)
    redobuffer.append(copy.deepcopy(undobuffer.pop()))
    if menu_with_field in type(surf).__bases__:
        surf.rfa()
        if hasattr(surf, "rebuttons"):
            surf.rebuttons()

def redohistory(surf: menu | menu_with_field):
    global undobuffer, redobuffer, file
    if len(redobuffer) == 0:
        return
    historyelem = redobuffer[-1]
    pathdict = PathDict(surf.data)
    for i in historyelem[1:]:
        pathdict[*historyelem[0], *i[0]] = i[1][0]
    file = copy.deepcopy(pathdict.data)
    surf.datalast = copy.deepcopy(pathdict.data)
    undobuffer.append(copy.deepcopy(redobuffer.pop()))
    if menu_with_field in type(surf).__bases__:
        surf.rfa()
        if hasattr(surf, "rebuttons"):
            surf.rebuttons()


def asktoexit(file, file2):
    global run, surf
    if file2 != file:
        ex = askyesnocancel("Exit from RWE+", "Do you want to save Changes?")
        if ex:
            surf.savef()
            sys.exit(0)
        elif ex is None:
            return
        else:
            sys.exit(0)
    else:
        sys.exit(0)


def launch(level):
    global bol, surf, fullscreen, undobuffer, redobuffer, file, file2
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
    undobuffer = []
    redobuffer = []
    width = settings["global"]["width"]
    height = settings["global"]["height"]
    window = pg.display.set_mode([width, height], flags=pg.RESIZABLE + (pg.FULLSCREEN * fullscreen))
    pg.display.set_icon(pg.image.load(path + "icon.png"))
    surf = MN(window, file, items, props, propcolors)
    surf.savef()
    os.system("cls")
    try:
        request = requests.get("https://api.github.com/repos/timofey260/RWE-Plus/releases/latest")
        if request.status_code == 200:
            gittag = request.json()["tag_name"]
            if tag != gittag:
                print("A new version of RWE+ is available!")
                print(f"Current Version: {tag}, latest: {gittag}")
                print("https://github.com/timofey260/RWE-Plus/releases/latest")
    except requests.exceptions.ConnectionError:
        print("Cannot find new RWE+ versions")
    run = True
    while run:
        for event in pg.event.get():
            match event.type:
                case pg.QUIT:
                    asktoexit(file, file2)
                case pg.WINDOWRESIZED:
                    surf.resize()
                case pg.KEYDOWN:
                    if event.key not in keys:
                        if bol:
                            bol = False
                            keypress(window, surf)
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
                case "undo":
                    undohistory(surf)
                case "redo":
                    redohistory(surf)
                case "%":
                    surf = HK(window, file, surf.menu)
                case "quit":
                    asktoexit(file, file2)
                case "MN":
                    surf = MN(window, file, items, props, propcolors)
                case "GE":
                    surf = GE(window, file, items, props, propcolors)
                case "TE":
                    surf = TE(window, file, items, props, propcolors)
                case "LE":
                    surf = LE(window, file, items, props, propcolors)
                case "LS":
                    surf = LS(window, file, items)
                case "FE":
                    surf = FE(window, file, items, props, propcolors)
                case "CE":
                    surf = CE(window, file, items, props, propcolors)
                case "LP":
                    surf = LP(window, file)
                case "EE":
                    surf = EE(window, file, items, props, propcolors)
                case "PE":
                    surf = PE(window, file, items, props, propcolors)
                case "HK":
                    surf = HK(window, file)
                case "fc":
                    fullscreen = not fullscreen
                    window = pg.display.set_mode([width, height], flags=pg.RESIZABLE + (pg.FULLSCREEN * fullscreen))
                    # pg.display.toggle_fullscreen()
                    surf.resize()
                case "save":
                    surf.savef()
                    file2 = copy.deepcopy(file)
                case "saveas":
                    surf.saveasf()
                    file2 = copy.deepcopy(file)
                case "savetxt":
                    surf.savef_txt()
                    file2 = copy.deepcopy(file)
            surf.message = ""
        if len(surf.historybuffer) > 0:
            surf.historybuffer.reverse()
            for actionindx in surf.historybuffer:
                undobuffer.append(actionindx)
            surf.historybuffer = []
            redobuffer = []
            undobuffer = undobuffer[-graphics["historylimit"]:]


        if not pg.key.get_pressed()[pg.K_LCTRL]:
            for i in surf.uc:
                if pg.key.get_pressed()[i]:
                    keypress(window, surf)

        if settings[surf.menu].get("menucolor") is not None:
            window.fill(pg.color.Color(settings[surf.menu]["menucolor"]))
        else:
            window.fill(pg.color.Color(settings["global"]["color"]))
        surf.blit()
        pg.display.flip()
        pg.display.update()


def loadmenu():
    global surf
    run = True
    width = 1280
    height = 720
    window = pg.display.set_mode([width, height], flags=pg.RESIZABLE)
    surf = load(window, {"path": ""})
    pg.display.set_icon(pg.image.load(path + "icon.png"))
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
                file = surf.asksaveasfilename(defaultextension=[".txt", ".wep"])
                print(file)
                if os.path.exists(file):
                    launch(file)
        keypress(window, surf)
        window.fill(pg.color.Color(settings["global"]["color"]))
        surf.blit()
        pg.display.flip()
        pg.display.update()
    pg.quit()
    exit(0)


def new():
    loadmenu()


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
