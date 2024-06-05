import multiprocessing

if __name__ == "__main__":
    import argparse
    from LevelProcess import *

    widgets.keybol = True
    open(application_path / "loadLog.txt", "w")
    multiprocessing.freeze_support()
    manager = ProcessManager()
    parser = argparse.ArgumentParser(prog="RWE+ console", description="Maybe a better, than official LE.\n"
                                                                      "Tool for making levels for rain world",
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.version = tag
    parser.add_argument("filename", type=str, nargs="?", help="Level to load")
    parser.add_argument("-n", "--new", help="Opens new file", dest="new", action="store_true")
    parser.add_argument("-v", "--version", help="Shows current version and exits", action="version")
    parser.add_argument("--render", "-r", dest="renderfiles", metavar="file", nargs="*", type=str,
                        help="Renders levels with drizzle.")
    # this code is as clean as main should be
    args = parser.parse_args()
    try:
        if args.new:
            manager.newprocess(-1)
        elif args.renderfiles is not None:
            s = f"\"{application_path}/drizzle/Drizzle.ConsoleApp{'' if islinux else '.exe'}\""
            subprocess.run([f"{application_path}/drizzle/Drizzle.ConsoleApp{'' if islinux else '.exe'}", "render",
                            *args.renderfiles], shell=True)
            if not islinux:
                os.system("start " + resolvepath(path2renderedlevels))
            exit(0)
        elif args.filename is not None:
            manager.newprocess(args.filename)
        else:
            manager.newprocess(-1)
    except FileNotFoundError:
        print("File not found!")
        raise

    while manager.run:
        manager.update()
