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
from util import Rect

from pyglet.gl import *

rabbyt.data_director = os.path.dirname(__file__)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

class LawnSegment:
    def __init__(self, id, display_id=-1, blades=5, rect=None):
        self.id = id
        self.display_id = display_id
        self.rect = rect
        self.blades = blades

        self.grass = []
        self.create_grass()
        self.rebuild()

    def create_grass(self):
        for count in range(self.blades):
            self.grass.append(
                Grass(randint(self.rect.left, self.rect.right),
                      randint(self.rect.bottom, self.rect.top)))

    def rebuild(self):
        self.display_id = glGenLists(1)
        glNewList(self.display_id, GL_COMPILE)

        for blade in self.grass:
            blade.draw()

        glEndList()

    def draw(self):
        glCallList(self.display_id)

    def grow(self):
        for blade in self.grass:
            blade.height += 3
            blade.width += 2

    def mow(self):
        for blade in self.grass:
            blade.height = 1
            blade.width = 1

class Mower:
    def __init__(self):
        self.rect = Rect(300, 260, 50, 10)
        self.image = image.load(data_file('mower.png'))

    def draw(self):
        self.image.blit(self.rect.x, self.rect.y)
        #self.draw_mow_rect()

    def draw_mow_rect(self):
        glColor4f(0, 0, 1, .5)

        glBegin(GL_POLYGON)
        glVertex2d(*self.rect.bottomleft)
        glVertex2d(*self.rect.topleft)
        glVertex2d(*self.rect.topright)
        glVertex2d(*self.rect.bottomright)
        glEnd()

        glColor4f(1, 1, 1, 1)


class Lawn:
    def __init__(self):
        self.street = image.load(data_file('street.png'))
        self.house = image.load(data_file('house.png'))
        self.truck = image.load(data_file('truck.png'))
        self.garbagecan = image.load(data_file('garbagecan-closed.png'))
        self.dogpiss = image.load(data_file('dogpiss.png'))

        self.mower = Mower()

        self.lawn = []
        self.current_segment = 0

        for y in range(130, 260, 10):
            for x in range(0, SCREEN_WIDTH, 40):

                # only build up to the edge of the lawn
                if x > 440 + (y - 130) / 10 * 20:
                    continue

                self.lawn.append(
                    LawnSegment(len(self.lawn), rect=Rect(x, y, 40, 10)))

        self.rebuild_time = 0.5
        self.rebuild_counter = self.rebuild_time

        # randomly update the various segments of the lawn
        self.update_list = range(0, len(self.lawn))
        random.shuffle(self.update_list)

        self.green_value = 0.3
        self.green_time = 1
        self.green_counter = self.green_time

        self.segment = len(self.lawn) - 1

        self.mow_time = 0.2
        self.mow_counter = self.mow_time
        
        self.mowing = True

        for blade in self.lawn[31].grass:
            blade.brown()
        self.lawn[31].rebuild()

    def update(self, tick):
        if self.mowing:
            self.mow_counter -= tick
            if self.mow_counter <= 0:
                self.mow()

        self.rebuild_counter -= tick
        if self.rebuild_counter <= 0:
            self.current_segment += 1
            if self.current_segment >= len(self.lawn):
                self.current_segment = 0
            self.rebuild_counter = self.rebuild_time
            self.lawn[self.update_list[self.current_segment]].grow()
            self.lawn[self.update_list[self.current_segment]].rebuild()

        self.green_counter -= tick
        if self.green_value <= 0.7 and self.green_counter <= 0:
            self.green_value += 0.005
            self.green_counter = self.green_time

    def draw(self):
        self.draw_field()

        glPushMatrix()
        for grass in self.lawn:
            grass.draw()

        glPopMatrix()
        glColor4f(1.0, 1.0, 1.0, 1.0)

        self.house.blit(170, 260)

        self.mower.draw()

        self.street.blit(0, 0)
        self.truck.blit(700, 150)
        self.garbagecan.blit(100, 100)

        glColor4f(1.0, 1.0, 1.0, 0.3)
        self.dogpiss.blit(300, 150)

        glColor4f(1.0, 1.0, 1.0, 1.0)

    def draw_field(self):
        glColor4f(0.2, self.green_value, 0.2, 1)

        glBegin(GL_POLYGON)
        glVertex2d(0, 0)
        glVertex2d(0, SCREEN_HEIGHT/2)
        glVertex2d(SCREEN_WIDTH, SCREEN_HEIGHT/2)
        glVertex2d(SCREEN_WIDTH, 0)
        glEnd()

        glColor4f(1, 1, 1, 1)

    def mow(self):
        #if self.mower.rect.x != self.lawn[self.segment].rect.x:
        self.mower.rect.center = self.lawn[self.segment].rect.center
        self.lawn[self.segment].mow()
        self.lawn[self.segment].rebuild()
        self.segment -= 1
        if self.segment < 0:
            self.segment = len(self.lawn) - 1
            self.mowing = False


class Grass:
    def __init__(self, x, y):
        self.pos = euclid.Vector2(x, y)
        self.height = 8
        self.width = 4

        self.green()

    def green(self):
        self.colors = ((0, 1.0, 0, 1), (0, 0.9, 0, 1), (0, 0.8, 0, 1))

    def brown(self):
        self.colors = ((0.6, 0.33, 0, 1),)

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

    lawn = NewLawn()

    while not win.has_exit:
        tick = clock.tick()
        win.dispatch_events()

        lawn.update(tick)

        rabbyt.clear((1, 1, 1))

        lawn.draw()

        win.flip()

if __name__ == '__main__':
    main()

