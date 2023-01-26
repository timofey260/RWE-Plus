import math
from pygame import Vector2, Rect
import lingotojson
import pygame as pg

data = lingotojson.turntoproject(open("LevelEditorProjects\\HI_C15.txt", "r").read())

def Diag(point1, point2):
    RectHeight = abs(point1.x - point2.x)
    RectWidth = abs(point1.y - point2.y)
    diagonal = math.sqrt((RectHeight * RectHeight) + (RectWidth * RectWidth))
    return diagonal

def DiagWI(point1, point2, dig):
    RectHeight = abs(point1.x - point2.x)
    RectWidth = abs(point1.y - point2.y)
    return (RectHeight * RectHeight) + (RectWidth * RectWidth) < dig*dig


def MoveToPoint(pointA, pointB, theMovement):
    pointB = pointB - pointA
    diag = Diag(Vector2(0, 0), pointB)
    if diag > 0:
        dirVec = pointB / diag
    else:
        dirVec = Vector2(0, 1)
    return dirVec * theMovement

def lerp(a, b, t):
    return (1 - t) * a + t * b

def restrict(a, minimum, maximum):
    return max(min(a, maximum), minimum)


class RopeModel:
    def __init__(self, data, pA, pB, prop, lengthFac, lr, rel):
        self.data = data
        self.posA: Vector2 = pA
        self.posB: Vector2 = pB
        self.segmentLength: int = prop["segmentLength"]
        self.grav = prop["grav"]
        self.stiff = prop["stiff"]
        self.release = rel
        self.segments = []
        self.friction = prop["friction"]
        self.airFric = prop["airFric"]
        self.layer = lr
        self.segRad = prop["segRad"]
        self.rigid = prop["rigid"]
        self.edgeDirection = prop["edgeDirection"]
        self.selfPush = prop["selfPush"]
        self.sourcePush = prop["sourcePush"]

        numberOfSegments = int(max((Diag(pA, pB) / self.segmentLength) * lengthFac, 3))
        step = Diag(pA, pB) / numberOfSegments
        for i in range(numberOfSegments):
            self.segments.append({"pos": pA + MoveToPoint(pA, pB, (i - 0.5) * step),
                                  "lastPos": pA + MoveToPoint(pA, pB, (i - 0.5) * step),
                                  "vel": Vector2(0, 0)
                                  })

    def modelRopeUpdate(self):
        if self.edgeDirection > 0:
            dir = MoveToPoint(self.posA, self.posB, 1)
            if self.release > -1:
                for A in range(int(len(self.segments) / 2)):
                    fac = pow(1 - ((A-1)/(len(self.segments)/2)), 2)
                    self.segments[A]["vel"] += dir * fac * self.edgeDirection
                idealFirstPos = self.posA + dir * self.segmentLength
                self.segments[0]["pos"] = Vector2(
                    lerp(self.segments[0]["pos"].x, idealFirstPos.x, self.edgeDirection),
                    lerp(self.segments[0]["pos"].y, idealFirstPos.y, self.edgeDirection))
            if self.release < 1:
                for A1 in range(int(len(self.segments) / 2)):
                    fac = pow(1 - ((A1 - 1) / (len(self.segments) / 2)), 2)
                    A = len(self.segments) - A1 - 1
                    self.segments[A]["vel"] += dir * fac * self.edgeDirection
                idealFirstPos = self.posB + dir * self.segmentLength
                self.segments[len(self.segments) - 1]["pos"] = Vector2(
                    lerp(self.segments[-1]["pos"].x, idealFirstPos.x, self.edgeDirection),
                    lerp(self.segments[-1]["pos"].y, idealFirstPos.y, self.edgeDirection))
        if self.release > -1:
            self.segments[0]["pos"] = self.posA.copy()
            self.segments[0]["vel"] = Vector2(0, 0)
        if self.release < 1:
            self.segments[-1]["pos"] = self.posB.copy()
            self.segments[-1]["vel"] = Vector2(0, 0)
        for i in range(len(self.segments)):
            self.segments[i]["lastPos"] = self.segments[i]["pos"]
            self.segments[i]["pos"] += self.segments[i]["vel"]
            self.segments[i]["vel"] *= self.airFric
            self.segments[i]["vel"].y = self.segments[i]["vel"].y + self.grav

        for i in range(1, len(self.segments)):
            self.ConnectRopePoints(i, i-1)
            if self.rigid > 0:
                self.ApplyRigidity(i)
        for i in range(len(self.segments), 0):
            self.ConnectRopePoints(i, i+1)
            if self.rigid > 0:
                self.ApplyRigidity(i)

        if self.selfPush > 0:
            for A in range(len(self.segments)):
                for B in range(len(self.segments)):
                    if A != B and DiagWI(self.segments[A]["pos"], self.segments[B]["pos"], self.selfPush):
                        dir = MoveToPoint(self.segments[A]["pos"], self.segments[B]["pos"], 1)
                        dist = Diag(self.segments[A]["pos"], self.segments[B]["pos"])
                        mov = dir * (dist-self.selfPush)

                        self.segments[A]['pos'] += mov * 0.5
                        self.segments[A]['vel'] += mov * 0.5
                        self.segments[B]['pos'] -= mov * 0.5
                        self.segments[B]['vel'] -= mov * 0.5
        if self.sourcePush > 0:
            for A in range(len(self.segments)):
                self.segments[A]["vel"] += MoveToPoint(self.posA, self.segments[A]["pos"], self.sourcePush) * restrict(((A - 1) / (len(self.segments) - 1)) - 0.7, 0, 1)
                self.segments[A]["vel"] += MoveToPoint(self.posB, self.segments[A]["pos"], self.sourcePush) * restrict((1 - ((A - 1) / (len(self.segments) - 1))) - 0.7, 0, 1)

        for i in range(int(self.release > -1), len(self.segments) - int(self.release < 1)):
            self.PushRopePointOutOfTerrain(i)


    def ApplyRigidity(self, A):
        for B2 in [-2, 2, -3, 3, -4, 4]:
            B = A + B2
            if 0 < B < len(self.segments):
                dir = MoveToPoint(self.segments[A]["pos"], self.segments[B]["pos"], 1)
                self.segments[A]["vel"] -= (dir * self.rigid * self.segmentLength) / (Diag(self.segments[A]["pos"], self.segments[B]["pos"]) + 0.1 + abs(B2))
                self.segments[B]["vel"] += (dir * self.rigid * self.segmentLength) / (Diag(self.segments[A]["pos"], self.segments[B]["pos"]) + 0.1 + abs(B2))

    def ConnectRopePoints(self, A, B):
        dir = MoveToPoint(self.segments[A]["pos"], self.segments[B]["pos"], 1)
        dist = Diag(self.segments[A]["pos"], self.segments[B]["pos"])
        if self.stiff == 1 or dist > self.segmentLength:
            mov = dir * (dist - self.segmentLength)

            self.segments[A]['pos'] += mov * 0.5
            self.segments[A]['vel'] += mov * 0.5
            self.segments[B]['pos'] -= mov * 0.5
            self.segments[B]['vel'] -= mov * 0.5

    def PushRopePointOutOfTerrain(self, A):
        p = {
            "Loc": self.segments[A]["pos"],
            "LastLoc": self.segments[A]["lastPos"],
            "Frc": self.segments[A]["vel"],
            "SizePnt": Vector2(self.segRad, self.segRad)
        }
        p = self.sharedCheckVCollision(p, self.friction, self.layer)

        self.segments[A]["pos"] = p["Loc"]
        self.segments[A]["vel"] = p["Frc"]

        gridPos = self.giveGridPos(self.segments[A]["pos"])
        for dir in [Vector2(0, 0), Vector2(-1, 0), Vector2(-1, -1), Vector2(0, -1), Vector2(1, -1), Vector2(1, 0), Vector2(1, 1), Vector2(0, 1), Vector2(-1, 1)]:
            midPos = self.giveMiddleOfTile(gridPos + dir)
            terrainPos = Vector2(restrict(self.segments[A]["pos"].x, midPos.x - 10, midPos.x + 10),
                                    restrict(self.segments[A]["pos"].y, midPos.y - 10, midPos.y + 10))
            terrainPos = ((terrainPos * 10) + midPos) / 11

            dir = MoveToPoint(self.segments[A]["pos"], terrainPos, 1)
            dist = Diag(self.segments[A]["pos"], terrainPos)
            if dist < self.segRad:
                mov = dir * (dist - self.segRad)
                self.segments[A]["pos"] += mov
                self.segments[A]["vel"] += mov

    def giveMiddleOfTile(self, pos):
        return Vector2((pos.x * 20) - 10, (pos.y * 20) - 10)
    def sharedCheckVCollision(self, p, friction, layer):
        bounce = 0

        if p["Frc"].y > 0:
            lastGridPos = self.giveGridPos(p["LastLoc"])
            feetPos = self.giveGridPos(p["Loc"] + Vector2(0, p["SizePnt"].y + 0.01))
            lastFeetPos = self.giveGridPos(p["LastLoc"] + Vector2(0, p["SizePnt"].y))
            leftPos = self.giveGridPos(p["Loc"] + Vector2(-p["SizePnt"].x + 1, p["SizePnt"].y + 0.01))
            rightPos = self.giveGridPos(p["Loc"] + Vector2(p["SizePnt"].x - 1, p["SizePnt"].y + 0.01))
            for q in range(int(lastFeetPos.y), int(feetPos.y)):
                for c in range(int(leftPos.x), int(rightPos.x)):
                    if self.afaMvLvlEdit(Vector2(c, q), layer) == 1 and self.afaMvLvlEdit(Vector2(c, q-1), layer) != 1:
                        if lastGridPos.y >= q and self.afaMvLvlEdit(lastGridPos, layer) == 1:
                            pass
                        else:
                            p["Loc"].y = ((q-1) * 20) - p["SizePnt"].y
                            p["Frc"].x *= friction
                            p["Frc"].y = -p["Frc"].y * bounce
                            return p
        else:
            lastGridPos = self.giveGridPos(p["LastLoc"])
            headPos = self.giveGridPos(p["Loc"] - Vector2(0, p["SizePnt"].y + 0.01))
            lastHeadPos = self.giveGridPos(p["LastLoc"] - Vector2(0, p["SizePnt"].y))
            leftPos = self.giveGridPos(p["Loc"] + Vector2(-p["SizePnt"].x + 1, p["SizePnt"].y + 0.01))
            rightPos = self.giveGridPos(p["Loc"] + Vector2(p["SizePnt"].x - 1, p["SizePnt"].y + 0.01))
            for d in range(int(lastHeadPos.y), int(headPos.y)):
                q = (lastHeadPos.y) - (d - headPos.y)
                for c in range(int(leftPos.x), int(rightPos.x)):
                    if self.afaMvLvlEdit(Vector2(c, q), layer) == 1 and self.afaMvLvlEdit(Vector2(c, q+1), layer) != 1:
                        if lastGridPos.y <= q and self.afaMvLvlEdit(lastGridPos, layer) != 1:
                            pass
                        else:
                            p["Loc"].y = (q * 20) + p["SizePnt"].y
                            p["Frc"].x *= friction
                            p["Frc"].y = -p["Frc"].y * bounce
                            return p
        return p

    def giveGridPos(self, pos: Vector2):
        return Vector2(int(pos.x / 20 + 0.4999), int(pos.y / 20 + 0.4999))

    def afaMvLvlEdit(self, pos: Vector2, layer):
        if Rect(1, 1, len(self.data["GE"]), len(self.data["GE"])).collidepoint(pos):
            return 0
            return self.data["GE"][round(pos.x)][round(pos.y)][layer][1]
        return 1

def demo():
    rope = RopeModel(data, Vector2(60, 200), Vector2(60 + 9 * 16, 200),
                     {"nm": "Wire", "tp": "rope", "depth": 4, "tags": [], "notes": [], "segmentLength": 10,
                      "collisionDepth": 2, "segRad": 4.5, "grav": 0.5, "friction": 0.5, "airFric": 0.9, "stiff": 1,
                      "previewColor": [255, 0, 0], "previewEvery": 4, "edgeDirection": 5, "rigid": 1.6, "selfPush": 0,
                      "sourcePush": 0}, 1, 1, 0)
    timer = pg.time.Clock()
    run = True
    width = 1280
    height = 720
    window = pg.display.set_mode([width, height], flags=pg.RESIZABLE)
    while run:
        window.fill([0, 0, 0])
        for event in pg.event.get():
            match event.type:
                case pg.QUIT:
                    exit(0)
        if any(pg.key.get_pressed()):
            rope.modelRopeUpdate()
        for segment in rope.segments:
            pg.draw.circle(window, [255, 0, 0], segment["pos"], 3)
        pg.draw.line(window, [0, 255, 0], rope.posA, rope.posB)
        pg.display.flip()
        pg.display.update()
        timer.tick(20)
    pg.quit()
    exit(0)

demo()
