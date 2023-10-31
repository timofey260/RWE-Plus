import requests
from menus import *
from tkinter.messagebox import askyesnocancel, askyesno
import argparse
from LevelProcess import LevelProcess, ProcessManager
from lingotojson import *
from files import settings, hotkeys, path, application_path

widgets.keybol = True
manager = ProcessManager()


def launch(level):
    manager.newprocess(level)


def loadmenu():
    global surf
    run = True
    width = 1280
    height = 720
    window = pg.display.set_mode([width, height], flags=pg.RESIZABLE)
    renderer = Renderer({"path": ""}, None, None, None, False)
    surf = load(window, renderer)
    pg.display.set_icon(loadimage(path + "icon.png"))
    while run:
        doevents(window, False)
        match surf.message:
            case "new":
                launch(-1)
            case "open":
                file = surf.asksaveasfilename(defaultextension=[".txt", ".wep"])
                if file is not None and os.path.exists(file):
                    launch(file)
            case "tutorial":
                file = turntoproject(open(path2tutorial + "tutorial.txt", "r").read())
                file["path"] = "tutorial"
                renderer = Renderer(file, None, None, None, True)
                surf = TT(window, renderer)
            case "load":
                renderer = Renderer({"path": ""}, None, None, None, False)
                surf = load(window, renderer)
        surf.message = ""
        if not pg.key.get_pressed()[pg.K_LCTRL]:
            for i in surf.uc:
                if pg.key.get_pressed()[i]:
                    keypress(window)
        window.fill(pg.color.Color(settings["global"]["color"]))
        surf.blit()
        pg.display.flip()
        pg.display.update()
    pg.quit()
    exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="RWE+ console", description="Maybe a better, than official LE.\n"
                                     "Tool for making levels for rain world",
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.version = tag
    parser.add_argument("filename", type=str, nargs="?", help="Level to load")
    parser.add_argument("-n", "--new", help="Opens new file", dest="new", action="store_true")
    parser.add_argument("-v", "--version", help="Shows current version and exits", action="version")
    parser.add_argument("--render", "-r", dest="renderfiles", metavar="file", nargs="*", type=str,
                        help="Renders levels with drizzle.")
    # parser.parse_args()
    args = parser.parse_args()
    try:
        if args.new:
            launch(-1)
        elif args.renderfiles is not None:
            s = f"\"{application_path}/drizzle/Drizzle.ConsoleApp{'' if islinux else '.exe'}\""
            subprocess.run([f"{application_path}/drizzle/Drizzle.ConsoleApp{'' if islinux else '.exe'}", "render", *args.renderfiles], shell=True)
            # os.system(s)
            if not islinux:
                os.system("start " + resolvepath(path2renderedlevels))
            exit(0)
        elif args.filename is not None:
            launch(args.filename)
        else:
            loadmenu()
        while manager.run:
            manager.update()
    except FileNotFoundError:
        print("File not found!")
        raise
    except Exception as e:
        # extra save level in case of eny crashes
        f = open(application_path + "\\CrashLog.txt", "w")
        f.write(traceback.format_exc())
        f.write("This is why RWE+ crashed^^^\nSorry")
        if globalsettings["saveoncrash"] and not globalsettings["debugmode"]:
            manager.saveall(True)
            raise
        traceback.print_exc()
        ex = askyesno("Crash!!!",
                      "Oops! RWE+ seems to be crashed, Crash log saved and showed in console\nDo you want to "
                      "save All Levels you opened?")
        if ex:
            manager.saveall()
        raise