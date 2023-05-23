import copy
import json
import pygame as pg
import pygame.key as k
import argparse
import os, sys
import re

if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(__file__)

ex = r"\\hotkeys.md"


def mdtojson(filename, desc, output):
    js = json.load(open(filename, "r"))
    modded = json.load(open(desc, "r"))
    newdict = {}
    for menu, items in js.items():
        print(menu, items)
        newdict[menu] = {}
        for key, func in items.items():
            if key == "unlock_keys":
                continue
            if modded[menu].get(func):
                newdict[menu][func] = modded[menu][func]
            else:
                newdict[menu][func] = ""
    open(output, "w").write(json.dumps(newdict, indent=4))


def turntomd(filename, desc, output):
    js = json.load(open(filename, "r"))
    modded = json.load(open(desc, "r"))
    with open(output, "w+") as file:
        file.write("Generated using hotkeys to md converter\n\n\n")
        for menu, items in js.items():
            file.write("###" + menu + "\n")
            for key, func in items.items():
                if key == "unlock_keys":
                    continue
                description = modded[menu][func]
                key2 = key.replace("+", "").replace("@", "")
                if key.find("+") != -1:
                    file.write(f"* **ctrl + {k.name(getattr(pg, key2)).title()}** - {func} - {description}\n")
                else:
                    file.write(f"* **{k.name(getattr(pg, key2)).title()}** - {func} - {description}\n")
    print("Done!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", type=str, help="file to be parsed")
    parser.add_argument("-o", "--output", default=application_path + ex,
                        metavar="file", dest="output", type=str, help="output file")
    parser.add_argument("-t", "--tomd", type=str, metavar="file", dest="md", default=None,
                        help="combines hotkeys and descriptions file into one markdown text")
    parser.add_argument("-m", "--merge", type=str, metavar="file", dest="merge", default=None,
                        help="combines hotkeys and descriptions file into one descriptions file")
    args = parser.parse_args()
    if args.merge is not None:
        mdtojson(args.filename, args.merge, args.output)
    elif args.md is not None:
        turntomd(args.filename, args.md, args.output)
