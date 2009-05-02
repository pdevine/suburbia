import os.path
import math
import rabbyt
import pyglet
import pyglet.window
from pyglet import clock
from pyglet import image
import random
import euclid
import data
import events
import bubbles
import window
import narrative

from pyglet.gl import *
from util import magicEventRegister
from util import Rect

import sky

rabbyt.data_director = os.path.dirname(__file__)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

pngNames = 'floaty01 floaty02 floaty03 floaty04'.split()

class Floater(pyglet.sprite.Sprite):
    def __init__(self, color=(255,255,255)):
        img = data.pngs[ random.choice(pngNames) ]
        x = random.randint(0,800)
        y = random.randint(400,600)
        super(Floater,self).__init__(img, x, y)
        self.velocityX = 0.1
        self.velocityY = -0.2
        self.rotateIncrement = random.random()

        self.dying = False

        self.image.anchor_x = self.image.width/2
        self.image.anchor_y = self.image.height/2

        print 'floater at', self.xy

        window.game_window.push_handlers(self.on_mouse_motion)
        events.AddListener(self)

    def getxy(self):
        return self.x, self.y
    def setxy(self, xy):
        self.x = xy[0]
        self.y = xy[1]
    xy = property(getxy, setxy)

    def __str__(self):
        return '<Floater %s %s %s>' % (self.x, self.y, id(self))

    def update(self, timeChange):
        if self.dying:
            self.opacity -= 20
            if self.opacity <= 20:
                self.die()

        #print 'updating flo'
        self.x = self.x + self.velocityX
        self.y = self.y + self.velocityY

        if (   self.x > 810 or self.x < -10
            or self.y > 610 or self.y < 400 ):
            self.dying = True

        self.rotation += self.rotateIncrement

    def die(self):
        self.opacity = 0.5
        events.Fire('FloaterDeath', self)

    def on_mouse_motion(self, x, y, dx, dy):
        addvelX = random.random() * cmp(dx,0)
        addvelY = random.random() * cmp(dy,0)
        self.velocityX += addvelX
        self.velocityY += addvelY
        


class FloaterGenerator(object):
    maxCountdown = 4
    def __init__(self):
        self.hitRequiredStage = False
        self.active = False
        self.countdown = random.randint(0, 1)
        self.count = 0
        self.floaters = []

        events.AddListener(self)

    def update(self, timechange):
        for f in self.floaters:
            f.update(timechange)

        if not self.active:
            return

        self.countdown -= timechange
        if self.countdown > 0 or self.count >= 3:
            return

        #print 'birthing floater'
        self.countdown = random.random()*self.maxCountdown
        floater = Floater()
        self.floaters.append(floater)
        events.Fire('FloaterBirth', floater)
        self.count += 1


    def On_FloaterDeath(self, floater):
        self.count -= 1
        self.floaters.remove(floater)

    def draw(self):
        for f in self.floaters:
            f.draw()

    def On_NewStage(self, stage):
        if stage == narrative.fin:
            self.hitRequiredStage = True
            self.maxCountdown = 3

    def On_Sunrise(self):
        if self.hitRequiredStage:
            self.active = True

    def On_Sunset(self):
        self.active = False


class SourcecodeGenerator(object):
    def __init__(self):
        self.srcImg = data.pngs['codesnip.png']
        self.countdown = 0
        self.hitRequiredStage = False
        self.active = False
        self.bigChunk = None
        self.x = 0
        self.y = 0

        self.regions = []

        window.game_window.push_handlers(self.on_mouse_release)
        events.AddListener(self)

    def update(self, timechange):
        if not (self.hitRequiredStage and self.active):
            return

        self.countdown = max(0, self.countdown - timechange)

    def draw(self):
        if not (self.hitRequiredStage and self.active):
            return

        if self.countdown <= 0:
            self.regions = []
            return

        x = random.randint(0,500)
        if self.countdown <= 0.02:
            self.bigChunk.blit(x, self.y)
            return

        for i, r in enumerate(self.regions):
            r.blit(x, self.y+i*5)

            x = x + random.randint(-1,3)

    def on_mouse_release(self, *args):
        x = random.randint(0,400)
        y = random.randint(10,600)
        width = random.randint(300,400)
        r1 = self.srcImg.get_region( x, y, width, 3 )
        r2 = self.srcImg.get_region( x, y+5, width, 5 )
        r3 = self.srcImg.get_region( x, y+7, width, 2 )

        y = random.randint(10,600)
        r4 = self.srcImg.get_region( x, y, width, 1 )
        r5 = self.srcImg.get_region( x, y+5, width, 2 )

        self.y = random.randint(0,600)

        self.bigChunk = self.srcImg.get_region(x,y, width, 100)

        self.regions += [r1, r2, r3, r4, r5]
        self.regions.append(r2)
        self.countdown = 0.8

    def On_Sunset(self):
        if narrative.dayCounter == 11:
            self.hitRequiredStage = True
            self.active = True


def main():
    global win
    clock.schedule(rabbyt.add_time)

    win = pyglet.window.Window(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
    window.set_window(win)

    bgPat = pyglet.image.SolidColorImagePattern((200,200,255,255))
    bg = pyglet.image.create(window.game_window.width, window.game_window.height, bgPat)

    rabbyt.set_default_attribs()
    bubbles.init()
    bubbles.win = win

    storyTeller = narrative.StoryTeller()

    fGen = FloaterGenerator()
    sGen = SourcecodeGenerator()

    events.Fire('NewStage', narrative.terror)

    scene = sky.Background(None)

    while not win.has_exit:
        tick = clock.tick()
        win.dispatch_events()

        bubbles.bubbleMaker.update(tick)
        scene.update(tick)
        fGen.update(tick)
        sGen.update(tick)
        
        events.ConsumeEventQueue()

        rabbyt.clear((1, 1, 1))
        bg.blit(0,0)

        scene.draw()
        fGen.draw()
        bubbles.bubbleMaker.draw()
        sGen.draw()

        win.flip()

if __name__ == '__main__':
    main()

