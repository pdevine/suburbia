import os.path
import rabbyt

from pyglet.window import Window
from pyglet import clock
from pyglet import image

import colorsys
from random import randint
import random
import euclid
import math

from util import data_file

from pyglet.gl import *

rabbyt.data_director = os.path.dirname(__file__)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

class Lawn:
    def __init__(self):
        pass
        self.lawn = []

        for count in range(0, 900):
            self.lawn.append(Grass(randint(5, SCREEN_WIDTH-5),
                                   randint(180, SCREEN_HEIGHT/2)))

        self.lawnCache = None
        self.build_lawn()

    def update(self, tick):
        pass

    def draw(self):
        glPushMatrix()

        glCallList(self.lawnCache)

        glPopMatrix()
        glColor4f(1.0, 1.0, 1.0, 1.0)

    def build_lawn(self):
        self.lawnCache = glGenLists(1)
        glNewList(self.lawnCache, GL_COMPILE)

        for grass in self.lawn:
            grass.draw()

        glEndList()

class Grass:
    def __init__(self, x, y):
        self.color = (0, 1.0, 0, 1)
        self.pos = euclid.Vector2(x, y)

    def update(self, tick):
        pass

    def draw(self):
        glColor4f(*self.color)

        glLineWidth(2)

        glBegin(GL_LINES)
        glVertex2i(int(self.pos.x), int(self.pos.y))
        glVertex2i(int(self.pos.x), int(self.pos.y+6))

        glVertex2i(int(self.pos.x), int(self.pos.y))
        glVertex2i(int(self.pos.x-3), int(self.pos.y+7))

        glVertex2i(int(self.pos.x), int(self.pos.y))
        glVertex2i(int(self.pos.x+5), int(self.pos.y+9))
        glEnd()


def main():
    clock.schedule(rabbyt.add_time)

    win = Window(width=800, height=600)
    rabbyt.set_default_attribs()

    lawn = Lawn()

    while not win.has_exit:
        tick = clock.tick()
        win.dispatch_events()

        #lawn.update(tick)

        rabbyt.clear((1, 1, 1))

        lawn.draw()

        win.flip()

if __name__ == '__main__':
    main()

