import os.path
import math
import rabbyt
import pyglet
import pyglet.window
from pyglet.window import Window
from pyglet import clock
from pyglet import image
import random
import euclid
import data
import events

from pyglet.gl import *
from util import magicEventRegister
from util import logicalToPerspective

import bubbles
import mower

rabbyt.data_director = os.path.dirname(__file__)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

LAWN_X = 40
LAWN_WIDTH = 400
LAWN_Y = 20
LAWN_HEIGHT = 300

win = None

class Dog(pyglet.sprite.Sprite):
    def __init__(self, color=(255,255,255)):
        img = data.pngs['dog.png']
        self.highlighted = False
        super(Dog, self).__init__(img)
        self.image.anchor_x = self.width/2
        self.image.anchor_y = self.height/2
        self.xy = 620, 300

        self.active = False
        self.runningAway = False
        self.searching = False
        self.pooing = False
        self.pooDelay = 3 #seconds it takes to drop a dookie
        self.activateDelay = 3 #seconds to rest before i can activate again
        self.shooPower = 0
        self.pooPower = 0
        self.pooCountdown = 0
        self.activateCountdown = 0

        win.push_handlers(self.on_mouse_press)
        win.push_handlers(self.on_mouse_release)
        win.push_handlers(self.on_mouse_motion)
        events.AddListener(self)

    def getxy(self):
        return self.x, self.y
    def setxy(self, xy):
        self.x = xy[0]
        self.y = xy[1]
    xy = property(getxy, setxy)

    def __str__(self):
        return '<Dog %s %s %s>' % (self.x, self.y, id(self))
    
    def distanceTo(self, x, y):
        return math.sqrt((x-self.x)**2 + (y-self.y)**2)

    def collides(self,x,y):
        return self.distanceTo(x,y) < self.width*0.5*self.scale

    def update(self, timeChange):
        if self.highlighted:
            self.color = (255,20,25)
        else:
            self.color = (255,255,255)

        if not self.active:
            if self.activateCountdown > 0:
                self.activateCountdown = max(self.activateCountdown-timeChange,
                                             0)
            return

        def moveTowardsTarget(x,y):
            # TODO: smarter move algorithm needed
            dx = x - self.x
            dy = y - self.y

            self.velocityX = 4*cmp(dx,0)
            self.velocityY = 4*cmp(dy,0)

            self.x += self.velocityX
            self.y += self.velocityY

        if self.runningAway:
            moveTowardsTarget(700,500)
            if self.distanceTo(700,500) < 5:
                print 'reached resting place'
                self.active = False

        elif self.searching:
            moveTowardsTarget(*self.pooTarget)

            if self.distanceTo(*self.pooTarget) < 5:
                print 'reached poo target'
                self.poo()
                self.searching = False

        elif self.pooing:
            self.pooCountdown -= timeChange
            if self.pooCountdown <= 0:
                print 'did my business'
                events.Fire('DogPoo', self.xy)
                self.runaway()
                self.pooing = False


    def shoo(self, x, y, button):
        # give a little initial rpms so the visual cues come up
        events.Fire('Shoo', x, y, self)
        self.shooPower += 10
        if self.shooPower > 20:
            self.runaway()

    def poo(self):
        self.searching = False
        self.pooing = True
        self.pooCountdown = self.pooDelay

    def activate(self):
        print 'ACTIVATING'
        events.Fire('DogActive', self)
        self.active = True
        self.searching = True
        self.runningAway = False
        self.pooing = False
        self.pooTarget = (random.randint(LAWN_X, LAWN_X+LAWN_WIDTH),
                          random.randint(LAWN_Y, LAWN_Y+LAWN_HEIGHT))

    def runaway(self):
        events.Fire('DogRunAway', self)
        self.searching = False
        self.runningAway = True
        self.shooPower = 0
        self.activateCountdown = self.activateDelay

    def on_mouse_press(self, x, y, button, modifiers):
        if self.collides(x,y):
            self.shoo(x, y, button)

    def on_mouse_release(self, x, y, button, modifiers):
        pass

    def on_mouse_motion(self, x, y, dx, dy):
        if self.collides(x,y):
            self.highlighted = True
        else:
            self.highlighted = False

    def On_MowerRPM(self, rpms):
        print 'dog got MowerRPM', rpms
        if self.active:
            return
        if rpms > mower.Mower.RPMGOAL*0.1 and not self.activateCountdown:
            self.activate()

    def On_MowerStart(self, mower):
        print 'dog got MowerStart'
        if self.active:
            self.runaway()
            
        
class PooMaster(object):
    def __init__(self):
        events.AddListener(self)
        self.pooSprites = []

    def On_DogPoo(self, pos):
        print 'putting poo at', pos
        img = data.pngs['poo.png']
        s = pyglet.sprite.Sprite(img, *pos)
        self.pooSprites.append(s)

    def draw(self):
        for s in self.pooSprites:
            s.draw()


def main():
    global win
    clock.schedule(rabbyt.add_time)

    win = Window(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
    rabbyt.set_default_attribs()
    mower.win = win

    dog = Dog()
    mowr = mower.Mower()
    guage = mower.Guage(mowr)
    bubbles.win = win
    pooMaster = PooMaster()

    objs = [dog, mowr, guage]
    magicEventRegister(win, events, objs)

    while not win.has_exit:
        tick = clock.tick()
        win.dispatch_events()

        for obj in objs:
            obj.update(tick)
        
        events.ConsumeEventQueue()

        rabbyt.clear((1, 1, 1))

        mowr.draw()
        guage.draw()
        pooMaster.draw()
        dog.draw()

        win.flip()

if __name__ == '__main__':
    main()

