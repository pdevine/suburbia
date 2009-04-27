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
        self.underground = image.load(data_file('underground-sm.png'))
        self.street = image.load(data_file('street.png'))
        self.lawn_segments = 200
        self.lawn = []
        self.lawn_cache = []
        self.lawn_positions = {}

        self.green_value = 0.3
        self.green_time = 1
        self.green_counter = self.green_time

        self.grow_turn = 0

        for lawn_count in range(0, self.lawn_segments):
            self.lawn.append([])
            self.lawn_cache.append([])
            for count in range(0, 20):
                while True:
                    blade = Grass(randint(5, SCREEN_WIDTH-5),
                                  randint(130, SCREEN_HEIGHT/2))
                    if not self.lawn_positions.get((blade.pos.x, blade.pos.y)):
                        self.lawn[lawn_count].append(blade)
                        break

            self.build_lawn(lawn_count, fresh_grass=True)

        self.rebuild_time = 0.75
        self.counter = 0


    def update(self, tick):
        self.counter -= tick
        if self.counter <= 0:
            self.counter = self.rebuild_time

            #print "grow"

            self.grow_turn += 1
            if self.grow_turn >= self.lawn_segments:
                self.grow_turn = 0

            self.build_lawn(self.grow_turn)

        self.green_counter -= tick
        if self.green_value <= 0.7 and self.green_counter <= 0:
            print "green"
            self.green_value += 0.01
            self.green_counter = self.green_time

    def draw_field(self):
        glColor4f(0.2, self.green_value, 0.2, 1)

        glBegin(GL_POLYGON)
        glVertex2d(0, 0)
        glVertex2d(0, SCREEN_HEIGHT/2)
        glVertex2d(SCREEN_WIDTH, SCREEN_HEIGHT/2)
        glVertex2d(SCREEN_WIDTH, 0)
        glEnd()

        glColor4f(1, 1, 1, 1)

    def draw(self):
        self.draw_field()
        self.underground.blit(0, 0)

        glPushMatrix()

        for lawn in self.lawn_cache:
            glCallList(lawn)

        glPopMatrix()
        glColor4f(1.0, 1.0, 1.0, 1.0)
        self.street.blit(0, 0)

    def build_lawn(self, grow_turn, fresh_grass=False):
        self.lawn_cache[grow_turn] = glGenLists(1)
        glNewList(self.lawn_cache[grow_turn], GL_COMPILE)

        for grass in self.lawn[grow_turn]:
            if not fresh_grass:
                grass.height += 4
                grass.width += 2
            grass.draw()

        glEndList()

class Grass:
    def __init__(self, x, y):
        self.pos = euclid.Vector2(x, y)
        self.height = 1
        self.width = 1
        self.colors = ((0, 1.0, 0, 1), (0, 0.9, 0, 1), (0, 0.8, 0, 1))

    def update(self, tick):
        pass

    def draw(self):
        color = random.choice(self.colors)
        glColor4f(*color)

        glLineWidth(1)

        glBegin(GL_LINES)
        glVertex2i(int(self.pos.x), int(self.pos.y))
        glVertex2i(int(self.pos.x), int(self.pos.y+randint(1, self.height)))

        glVertex2i(int(self.pos.x), int(self.pos.y))
        glVertex2i(int(self.pos.x - randint(1, self.width)),
                   int(self.pos.y + randint(1, self.height)))

        glVertex2i(int(self.pos.x), int(self.pos.y))
        glVertex2i(int(self.pos.x + randint(1, self.width)),
                   int(self.pos.y + randint(1, self.height)))
        glEnd()


def main():
    clock.schedule(rabbyt.add_time)

    win = Window(width=800, height=600)
    rabbyt.set_default_attribs()

    lawn = Lawn()

    while not win.has_exit:
        tick = clock.tick()
        win.dispatch_events()

        lawn.update(tick)

        rabbyt.clear((1, 1, 1))

        lawn.draw()

        win.flip()

if __name__ == '__main__':
    main()

