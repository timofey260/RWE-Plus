import copy
import requests

import menuclass
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
surf: Menu | MenuWithField = None

tag = "2.1"
version = "version: " + tag


def keypress(window):
    global run, file, file2, redobuffer, undobuffer, surf
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
            undohistory()
        case "redo":
            redohistory()
        case "quit":
            asktoexit(file, file2)
        case "reload":
            surf.reload()
        case "save":
            surf.savef()
            file2 = copy.deepcopy(file)
        case "new":
            print("New")
            surf.savef()
            run = False
        case "open":
            surf.savef()
            file = surf.asksaveasfilename(defaultextension=[".txt", ".wep"])
            if file is not None and os.path.exists(file):
                launchload(file)
                undobuffer = []
                redobuffer = []
                surf.renderer.data = file
                surf.data = file
                surf.renderer.set_surface()
                surf.renderer.render_all(0)
                surf = MN(window, surf.renderer)
                os.system("cls")
            print("Open")


def undohistory():
    global undobuffer, redobuffer, file, surf
    if len(undobuffer) == 0:
        return
    print("undo")
    historyelem = undobuffer[-1]
    pathdict = PathDict(surf.data)
    for i in historyelem[1:]:
        pathdict[*historyelem[0], *i[0]] = i[1][1]
    surf.data = copy.deepcopy(pathdict.data)
    file = surf.data
    surf.datalast = copy.deepcopy(pathdict.data)
    redobuffer.append(copy.deepcopy(undobuffer.pop()))
    if MenuWithField in type(surf).__bases__:
        surf.renderer.data = surf.data
        surf.renderer.render_all(surf.layer)
        if hasattr(surf, "rebuttons"):
            surf.rebuttons()


def redohistory():
    global undobuffer, redobuffer, file, surf
    if len(redobuffer) == 0:
        return
    print("redo")
    historyelem = redobuffer[-1]
    pathdict = PathDict(surf.data)
    for i in historyelem[1:]:
        pathdict[*historyelem[0], *i[0]] = i[1][0]
    surf.data = copy.deepcopy(pathdict.data)
    file = surf.data
    surf.datalast = copy.deepcopy(pathdict.data)
    undobuffer.append(copy.deepcopy(redobuffer.pop()))
    if MenuWithField in type(surf).__bases__:
        surf.renderer.data = surf.data
        surf.renderer.render_all(surf.layer)
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

def launchload(level):
    global bol, surf, fullscreen, undobuffer, redobuffer, file, file2, run
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
    undobuffer = []
    redobuffer = []


def launch(level):
    global bol, surf, fullscreen, undobuffer, redobuffer, file, file2, run
    launchload(level)
    items = inittolist()
    propcolors = getcolors()
    props = getprops(items)
    file2 = copy.deepcopy(file)
    width = settings["global"]["width"]
    height = settings["global"]["height"]
    window = pg.display.set_mode([width, height], flags=pg.RESIZABLE + (pg.FULLSCREEN * fullscreen))
    # pg.display.set_icon(pg.image.load(path + "icon.png"))
    renderer = Renderer(file, items, props, propcolors)
    renderer.render_all(0)
    surf = MN(window, renderer)
    os.system("cls")
    try:
        request = requests.get("https://api.github.com/repos/timofey260/RWE-Plus/releases/latest", timeout=2)
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
                            keypress(window)
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
                    undohistory()
                case "redo":
                    redohistory()
                case "%":
                    surf = HK(window, renderer, surf.menu)
                case "quit":
                    asktoexit(file, file2)
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
                case _:
                    if surf.message in menulist:
                        surf = getattr(sys.modules[__name__], surf.message)(window, renderer)
            surf.message = ""
        if len(surf.historybuffer) > 0:
            surf.historybuffer.reverse()
            undobuffer.extend(surf.historybuffer)
            surf.historybuffer = []
            redobuffer = []
            undobuffer = undobuffer[-graphics["historylimit"]:]


        if not pg.key.get_pressed()[pg.K_LCTRL]:
            for i in surf.uc:
                if pg.key.get_pressed()[i]:
                    keypress(window)

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
    renderer = Renderer({"path": ""}, None, None, None, False)
    surf = load(window, renderer)
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
                surf.message = ""
            case "open":
                file = surf.asksaveasfilename(defaultextension=[".txt", ".wep"])
                if file is not None and os.path.exists(file):
                    launch(file)
                    surf = load(window, renderer)
                surf.message = ""
        keypress(window)
        window.fill(pg.color.Color(settings["global"]["color"]))
        surf.blit()
        pg.display.flip()
        pg.display.update()
    pg.quit()
    exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="RWE+ console", description="maybe a better, than official LE.")
    parser.version = version
    parser.add_argument("filename", type=str, nargs="?", help="level to load")
    parser.add_argument("-n", "--new", help="opens new file", dest="new", action="store_true")
    parser.add_argument("-v", "--version", help="shows current version and exits", action="version")
    parser.add_argument("--render", "-r", dest="renderfiles", metavar="file", nargs="*", type=str, help="renders levels with drizzle.")
    # parser.parse_args()
    args = parser.parse_args()
    if args.new:
        loadmenu()
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
        loadmenu()
