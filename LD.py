from menuclass import *


class LoadMenu(Menu):
    def __init__(self, process):
        super().__init__(process, "LD")
        self.recent = json.load(open(path + "recentProjects.json", "r"))
        self.filedata = {}
        self.selector = widgets.Selector(self, self.generate_data(), "s1")
        self.selector.callback = self.selectorset
        self.selector.callbackafterchange = False

    def selectorset(self, buttondata):
        self.owner.__init__(self.owner.manager, buttondata["path"])

    def generate_data(self) -> ItemData:
        data = ItemData()
        items = []
        for i in self.recent["files"][:20]:
            if not os.path.exists(i["path"]):
                continue
            desc = f'Path: {i["path"]}\nLast modified: {filetime(i["path"])}'
            items.append({
                "nm": i["name"],
                "color": gray,
                "description": desc,
                "path": i["path"]
            })
        data.append({"name": "Recent files", "color": gray, "items": items})
        weps = []
        txts = []
        wepcount = 0
        weppage = 1
        txtcount = 0
        txtpage = 1
        for root, dirs, files in os.walk(path2levels):
            for i, file in enumerate(files):
                fpath = os.path.join(root, file)
                if not os.path.exists(fpath):
                    continue
                desc = f'Path: {fpath}\nLast modified: {filetime(fpath)}'
                _, ext = os.path.splitext(file)
                dat = {
                    "nm": file,
                    "color": gray,
                    "description": desc,
                    "path": fpath
                }
                if ext.lower() == ".wep":
                    weps.append(dat)
                    wepcount += 1
                    if wepcount > globalsettings["recent_items_per_category"]:
                        data.append({"name": f"All .wep files p{weppage}", "color": gray, "items": weps})
                        weps = []
                        weppage += 1
                        wepcount = 0
                elif ext.lower() == ".txt":
                    txts.append(dat)
                    txtcount += 1
                    if txtcount > globalsettings["recent_items_per_category"]:
                        data.append({"name": f"All .txt files p{txtpage}", "color": gray, "items": txts})
                        txts = []
                        txtpage += 1
                        txtcount = 0
        data.append({"name": f"All .wep files p{weppage}", "color": gray, "items": weps})
        data.append({"name": f"All .txt files p{txtpage}", "color": gray, "items": txts})
        return data

    def resize(self):
        super().resize()
        if hasattr(self, "selector"):
            self.selector.resize()

    def blit(self):
        self.selector.blit()
        super().blit()
        self.selector.blittooltip()

    def tutorial(self):
        tutorial()

    def open(self):
        self.sendtoowner("open")

    def new(self):
        self.sendtoowner("new")

    def report(self):
        report()

    def github(self):
        github()

    def lt(self):
        self.selector.left()

    def rt(self):
        self.selector.right()

    @property
    def touchesanything(self):
        return super().touchesanything or self.selector.touchesanything

    @property
    def custom_info(self):
        return "Have fun!"
