import os.path
import rabbyt
import pyglet
from pyglet.window import Window
from pyglet import clock
from pyglet import image
import random
import euclid
import data

from pyglet.gl import *

rabbyt.data_director = os.path.dirname(__file__)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

class Rain:
    def __init__(self):
        self.quad = gluNewQuadric()
        self.rain = []

        self.delay_time = 0.1
        self.counter = self.delay_time

        self.addDrops()

    def addDrops(self, amount=10):
        for count in range(amount):
            self.rain.append(RainDrop(self.quad))

    def update(self, tick):
        self.counter -= tick
        if self.counter <= 0:
            self.addDrops()
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
        self.color = (0, 0, 0.95, 1)
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
        glColor4f(*self.color)
        glPushMatrix()

        glTranslatef(self.x, self.y, 0)

        gluQuadricDrawStyle(self.quad, GLU_FILL)
        gluDisk(self.quad, 0, 2, 50, 1)

        glPopMatrix()


class GrassBlade(pyglet.sprite.Sprite):
    def __init__(self, pos):
        img = data.pngs['grassblade.png']
        pyglet.sprite.Sprite.__init__(self, img, *pos)
        self.logicalX = pos[0]
        self.logicalY = pos[1]

    def update(self, timeChange=None):
        return
        self.x = self.logicalX + window.bgOffset[0]
        self.y = self.logicalY + window.bgOffset[1]
        self.logicalX += randint(-2, 2)
        self.logicalY += 1
        self.opacity -= 2
        self.scale += 0.01
        if self.opacity < 80:
            events.Fire('SpriteRemove', self)

def logicalToPerspective(x,y):
    vanishingLineX = 400.0
    vanishingLineY = 300.0

    oldDeltaX = vanishingLineX-x
    oldDeltaY = vanishingLineY-y

    # 0 means its right on it, 1.0 means it's really far away
    farnessFromLineY = (oldDeltaY/vanishingLineY)
    farnessFromLineX = (oldDeltaX/vanishingLineX)

    newDeltaX = (farnessFromLineY)*oldDeltaX
    newDeltaY = (farnessFromLineY)*oldDeltaY

    newX = x - (newDeltaX - oldDeltaX)
    newY = y - (newDeltaY - oldDeltaY)
    print x,y, 'translated to', newX, newY
    return newX, newY

class Lawn(object):
    def __init__(self):
        self.blades = []
        for i in range(20):
            for j in range(8):
                logicalPosition = i*40, j*30
                pos = logicalToPerspective(*logicalPosition)
                #pos = logicalPosition
                self.blades.append( GrassBlade(pos) )

    def update(self, timechange):
        [b.update(timechange) for b in self.blades]
    def draw(self):
        [b.draw() for b in self.blades]

def main():
    clock.schedule(rabbyt.add_time)

    win = Window(width=800, height=600)
    rabbyt.set_default_attribs()

    rain = Rain()
    lawn = Lawn()

    while not win.has_exit:
        tick = clock.tick()
        win.dispatch_events()

        rain.update(tick)
        lawn.update(tick)

        rabbyt.clear((1, 1, 1))

        rain.draw()
        lawn.draw()

        win.flip()

if __name__ == '__main__':
    main()

