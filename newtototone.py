#!python
# -*- mode: python; Encoding: utf-8; coding: utf-8 -*-
# Last updated: <2019/02/10 02:52:35 +0900>
"""
NEWTOTOTONE (Pyxel version)

Windows10 x64 + Python 3.7.1 32bit
"""

import pyxel
import random


scrw, scrh = 160, 120
score = 0
infos = []


class Player:
    def __init__(self):
        self.init()

    def init(self):
        self.alive = True
        self.x = pyxel.width / 2
        self.y = pyxel.height - 8 - 8
        self.flip = 0
        self.t = 0

    def update(self):
        if self.alive:
            # move player
            spd = 1
            if pyxel.btn(pyxel.KEY_LEFT):
                self.x -= spd
                self.flip = 0
            elif pyxel.btn(pyxel.KEY_RIGHT):
                self.x += spd
                self.flip = 1
            if self.x <= 8:
                self.x = 8
            if self.x >= pyxel.width - 8:
                self.x = pyxel.width - 8
        self.t += 1

    def draw(self):
        id = 6
        if self.alive:
            id += (self.t % 40) // 20 * 2
        else:
            id = 10
            self.flip = self.t % 20 // 10
        x, y = self.x - 8, self.y - 8
        u, v = id * 8, 0
        w, h = 16, 16
        if self.flip:
            w = -16
        imgn, colkey = 0, 10
        pyxel.blt(x, y, imgn, u, v, w, h, colkey)


class Item:
    def __init__(self, x, y, kind):
        self.alive = True
        self.x, self.y = x, y
        self.dx, self.dy = 0, 0
        self.kind = kind
        self.hit = False
        self.sprid = 2 + (self.kind) * 2

    def update(self):
        if self.alive:
            self.x += self.dx
            self.y += self.dy
            self.dy += 0.25 * 9.8 / 60.0

            if self.y - 8 > pyxel.height:
                self.y = -16
                self.dy = 0
                self.alive = False
            elif self.hit:
                if self.kind == 0:
                    global score
                    score += 10
                    born_info(self.x, self.y, 10)
                    pyxel.play(0, 0, loop=False)
                self.alive = False

    def draw(self):
        if self.alive:
            x, y = self.x - 8, self.y - 8
            u, v = self.sprid * 8, 0
            w, h = 16, 16
            imgn, colkey = 0, 10
            pyxel.blt(x, y, imgn, u, v, w, h, colkey)


class Info:
    def __init__(self, x, y, str):
        self.alive = True
        self.x, self.y = x, y
        self.str = str
        self.timer = 0

    def update(self):
        self.y -= 0.5
        self.timer += 1
        if self.timer > 30:
            self.alive = False

    def draw(self):
        pyxel.text(self.x + 1, self.y + 1, self.str, 0)
        pyxel.text(self.x, self.y, self.str, 7)


def born_info(_x, _y, _score):
    global infos
    infos.append(Info(_x, _y - 16, "+%d" % _score))


def update_sprites(objs):
    for o in objs:
        o.update()


def remove_sprites(objs):
    if len(objs) > 0:
        elen = len(objs)
        for i in reversed(range(elen)):
            if not objs[i].alive:
                objs.pop(i)


def draw_sprites(objs):
    for o in objs:
        o.draw()


def hitcheck(p, objs):
    for spr in objs:
        dx = abs(spr.x - p.x)
        dy = abs(spr.y - p.y)
        if spr.kind == 0:
            if dx <= 8.0 and dy <= 8.0:
                spr.hit = True
        elif spr.kind == 1:
            if (dx * dx + dy * dy) < (8 * 8):
                spr.hit = True
                p.alive = False


def print_center(s, y):
    x = (pyxel.width - (len(s) * 4)) // 2
    pyxel.text(x + 1, y + 1, s, 0)
    pyxel.text(x, y, s, 7)


def draw_bg():
    x, y = 0, 0
    tm = 0
    u, v, w, h = 0, 0, 20, 15
    pyxel.bltm(x, y, tm, u, v, w, h)


class App:

    def __init__(self):
        global score
        global infos

        pyxel.init(scrw, scrh, caption="NEWTOTOTONE", fps=60)
        pyxel.load("assets/newtototone.pyxel")

        self.player = Player()
        score = 0
        self.hiscore = 0
        self.gmstep = 0
        self.brate = 0
        self.t = 0
        self.brate = 100
        self.items = []
        infos = []

        pyxel.run(self.update, self.draw)

    def update(self):
        global score
        global infos

        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        if self.gmstep == 0:
            # title
            if pyxel.btnp(pyxel.KEY_UP):
                score = 0
                self.gmstep = 1
                self.brate = 100
                self.t = 0
                random.seed(0)

                # start BGM
                pyxel.playm(0, loop=True)

        elif self.gmstep == 1:
            # game main
            hitcheck(self.player, self.items)
            self.player.update()

            # born item
            if self.t % 60 == 0:
                self.brate -= 3
                if self.brate <= 1:
                    self.brate = 100
            if self.t % 10 == 0:
                x = random.randint(8, pyxel.width - 8 - 1)
                b = max(20, self.brate)
                k = 1 if random.randint(0, 100) > b else 0
                self.items.append(Item(x, -16, k))

            update_sprites(self.items)
            update_sprites(infos)

            remove_sprites(self.items)
            remove_sprites(infos)

            if score > self.hiscore:
                self.hiscore = score

            if not self.player.alive:
                self.gmstep = 2
                self.t = 0

                # stop BGM
                pyxel.stop()

                # play dead SE
                pyxel.play(0, 1, loop=False)

        elif self.gmstep == 2:
            # game over
            self.player.update()
            if self.t >= 60 + 30:
                self.player.init()
                self.gmstep = 0
                self.items = []
                infos = []

        self.t += 1

    def draw(self):
        global score
        global infos

        pyxel.cls(0)
        draw_bg()
        self.player.draw()
        draw_sprites(self.items)
        draw_sprites(infos)

        s = "SCORE: %d  HI-SCORE: %d" % (score, self.hiscore)
        pyxel.text(1, 1, s, 7)

        if self.gmstep == 0:
            print_center("NEWTOTOTONE", 40)
            print_center("MOVE: LEFT,RIGHT KEY", 74)
            print_center("PUSH UP KEY TO START", 84)
        elif self.gmstep == 2:
            print_center("GAME OVER", pyxel.height / 2 - 6)


App()
