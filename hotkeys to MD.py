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


def turntomd(filename, output, mod=False):
    js = json.load(open(filename, "r"))
    if mod:
        modded = open(mod, "r").readlines()
    with open(output, "w+") as file:
        file.write("Generated using hotkeys to md converter\n\n\n")
        for key, items in js.items():
            if mod:
                for line in modded: # NOQA
                    f = re.search(r"### ([a-zA-Z0-9]+)", line)
                    if f is None:
                        continue
                    if f[1] == key:
                        file.write(line)
                        break
            else:
                file.write(f"### {key}\n")
            for item, value in items.items():
                if item == "unlock_keys":
                    continue
                d = ''
                key2 = item.replace("+", "").replace("@", "")
                if mod:
                    prevcat = ""
                    for line in modded:
                        cat = re.search(r"### ([a-zA-Z0-9]+)", line)
                        if cat is not None:
                            prevcat = cat[1]
                        if prevcat != key:
                            continue
                        print(prevcat, key)
                        f = re.search(r"- ([a-zA-Z0-9-/_]+) -", line)
                        if f is None:
                            continue
                        if f[1] == value:
                            desc = re.search(r"- [a-zA-Z0-9-/_]+ - ([a-zA-Z0-9+-/_,. ]+)", line)
                            if desc is None:
                                continue
                            d = desc[1]
                            break
                if item.find("+") != -1:
                    file.write(f"* **ctrl + {k.name(getattr(pg, key2)).title()}** - {value} - {d}\n")
                else:
                    file.write(f"* **{k.name(getattr(pg, key2)).title()}** - {value} - {d}\n")
    print("Done!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", type=str, help="file to be parsed")
    parser.add_argument("-o", "--output", default=application_path + ex,
                        metavar="file", dest="output", type=str, help="output file")
    parser.add_argument("-m", "--merge", type=str, metavar="file", dest="mod", default=None, help="merges two files to one")
    args = parser.parse_args()
    if args.filename is not None:
        turntomd(args.filename, args.output, args.mod)
