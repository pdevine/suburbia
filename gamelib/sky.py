import os.path
import rabbyt

from pyglet.window import Window
from pyglet import clock
from pyglet import image

import random
import euclid

from util import data_file

from pyglet.gl import *

rabbyt.data_director = os.path.dirname(__file__)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

class Background:
    def __init__(self):
        self.color = (0.78, 0.78, 1.0)

        self.sun = Sun()
        self.rain = Rain()
        self.earth = image.load(data_file('small-earth.png'))

    def update(self, tick):
        elements = [self.sun, self.rain]

        for element in elements:
            if element:
                element.update(tick)

    def draw(self):
#        elements = [self.earth, self.sun, self.rain]
#        for element in elements:
#            if element:
#                element.draw()

        self.sun.draw()
        self.earth.blit(0, 0)
        self.rain.draw()

class Sun:
    def __init__(self):
        #self.image = rabbyt.Sprite(data_file('sun.png'))
        #self.image.xy = (-100, SCREEN_HEIGHT - 100)
        self.image = image.load(data_file('sun.png'))
        self.pos = euclid.Vector2(-100, SCREEN_HEIGHT - 100)
        self.vector = euclid.Vector2(0, 0)
        self.vector.x = 50

    def update(self, tick):
        if self.pos.x < SCREEN_WIDTH / 2:
            self.vector.y = 5
        else:
            self.vector.y = -5

        self.pos.x += self.vector.x * tick
        self.pos.y += self.vector.y * tick

    def draw(self):
        glColor4f(1.0, 1.0, 1.0, 1.0)

        #self.image.render()
        self.image.blit(self.pos.x, self.pos.y)


class Rain:
    def __init__(self):
        self.quad = gluNewQuadric()
        self.rain = []

        self.delay_time = 0.1
        self.counter = self.delay_time

        self.add_drops()

    def add_drops(self, amount=10):
        for count in range(amount):
            self.rain.append(RainDrop(self.quad))

    def update(self, tick):
        self.counter -= tick
        if self.counter <= 0:
            self.add_drops()
            self.counter = self.delay_time

        for drop in self.rain:
            drop.update(tick)

            if drop.dead:
                self.rain.remove(drop)

    def draw(self):
        for drop in self.rain:
            drop.draw()

class RainDrop:
    def __init__(self, quad):
        self.quad = quad
        self.color = (0, 0, 0.95, 0.5)
        self.vector = euclid.Vector2(0, 0)
        self.dead = False

        self.vector.y = -SCREEN_HEIGHT

        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = SCREEN_HEIGHT + 1

    def update(self, tick):
        self.x += self.vector.x * tick
        self.y += self.vector.y * tick

        if self.y < 0:
            self.dead = True

    def draw(self):
        glPushMatrix()

        glColor4f(*self.color)

        glLineWidth(3)

        glBegin(GL_LINES)
        glVertex2i(int(self.x), int(self.y))
        glVertex2i(int(self.x), int(self.y-3))
        glEnd()

        glColor4f(1.0, 1.0, 1.0, 1.0)

        glPopMatrix()


def main():
    clock.schedule(rabbyt.add_time)

    win = Window(width=800, height=600)
    rabbyt.set_default_attribs()

    bg = Background()

    while not win.has_exit:
        tick = clock.tick()
        win.dispatch_events()

        bg.update(tick)

        rabbyt.clear((bg.color))

        bg.draw()

        win.flip()

if __name__ == '__main__':
    main()

