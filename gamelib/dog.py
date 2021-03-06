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
import window
import narrative

from pyglet.gl import *
from util import logicalToPerspective

import bubbles
import mower

rabbyt.data_director = os.path.dirname(__file__)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

LAWN_X = 40
LAWN_WIDTH = 400
LAWN_Y = 170
LAWN_HEIGHT = 120

STARTPOS = (830,300)

class Dog(pyglet.sprite.Sprite):
    hintDone = False
    def __init__(self, color=(255,255,255)):
        img = data.pngs['dog.png']
        self.highlighted = False
        super(Dog, self).__init__(img)
        self.image.anchor_x = self.width/2
        self.image.anchor_y = self.height/2
        self.xy = STARTPOS

        self.active = False
        self.active = True #DEBUG
        self.searching = False
        self.runningAway = False
        self.pooing = False
        self.pooDelay = 3 #seconds it takes to drop a dookie
        self.searchDelay = 3 #seconds to rest before i can search again
        self.shooPower = 0
        self.pooPower = 0
        self.pooCountdown = 0
        self.searchCountdown = 0

        window.game_window.push_handlers(self.on_mouse_press)
        window.game_window.push_handlers(self.on_mouse_release)
        window.game_window.push_handlers(self.on_mouse_motion)
        events.AddListener(self)

    def draw(self):
        if not self.active:
            return
        # XXX - fix bug with the color becoming corrupt on some machines
        pyglet.sprite.Sprite.draw(self)
        glColor4f(1, 1, 1, 1)

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
        if not self.active:
            return

        if self.highlighted:
            self.color = (255,20,25)
        else:
            self.color = (255,255,255)

        if self.searchCountdown > 0:
            self.searchCountdown = max(self.searchCountdown-timeChange,
                                       0)

        def moveTowardsTarget(x,y):
            # TODO: smarter move algorithm needed
            dx = x - self.x
            dy = y - self.y

            self.velocityX = 4*cmp(dx,0)
            self.velocityY = 4*cmp(dy,0)

            if abs(self.velocityX) > abs(dx):
                self.velocityX = 1 * cmp(self.velocityX,0)

            if abs(self.velocityY) > abs(dy):
                self.velocityY = 1 * cmp(self.velocityY,0)
                

            self.x += self.velocityX
            self.y += self.velocityY

        if self.runningAway:
            moveTowardsTarget(*STARTPOS)
            if self.distanceTo(*STARTPOS) < 5:
                self.runningAway = False
                #print 'reached resting place'
                self.searching = False

        elif self.searching:
            moveTowardsTarget(*self.pooTarget)

            if self.distanceTo(*self.pooTarget) < 5:
                self.poo()
                self.searching = False

        elif self.pooing:
            self.pooCountdown -= timeChange
            if self.pooCountdown <= 0:
                # TODO this is a hack
                pos = self.x-12, self.y-30
                events.Fire('DogPoo', pos)
                self.runaway()
                self.pooing = False


    def shoo(self, x, y, button):
        # give a little initial rpms so the visual cues come up
        events.Fire('Shoo', x, y, self)
        if self.searching:
            self.shooPower += 10
            if self.shooPower > 20:
                self.runaway()

    def poo(self):
        self.searching = False
        self.pooing = True
        self.pooCountdown = self.pooDelay

    def search(self):
        events.Fire('DogActive', self)
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
        self.searchCountdown = self.searchDelay

    def on_mouse_press(self, x, y, button, modifiers):
        if self.collides(x,y):
            self.shoo(x, y, button)

    def on_mouse_release(self, x, y, button, modifiers):
        pass

    def on_mouse_motion(self, x, y, dx, dy):
        if self.collides(x,y):
            self.highlighted = True
            if not Dog.hintDone:
                events.Fire('NewHint', 'I can yell at the dog by clicking on her')
                Dog.hintDone = True
        else:
            self.highlighted = False

    def On_MowerRPM(self, rpms):
        #print 'dog got MowerRPM', rpms
        if self.searching:
            return
        if rpms > mower.Mower.RPMGOAL*0.1 and not (self.searchCountdown or self.pooing or self.runningAway):
            self.search()

    def On_MowerStart(self, mower):
        #print 'dog got MowerStart'
        if self.searching:
            self.runaway()

    def On_NewStage(self, stage):
        if stage == narrative.foreshadowing:
            self.active = True

            

class PooSmearAnim(object):
    def __init__(self, pos, poomaster):
        img = data.pngs['poonugget_left.png']
        self.left = pyglet.sprite.Sprite(img, *pos)
        img = data.pngs['poonugget_mid.png']
        self.mid = pyglet.sprite.Sprite(img, *pos)
        img = data.pngs['poonugget_right.png']
        self.right = pyglet.sprite.Sprite(img, *pos)
        self.countdown = 0.5
        self.poomaster = poomaster

    def update(self, timechange):
        self.countdown -= timechange
        if self.countdown <= 0:
            self.poomaster.deadAnims.append(self)
        for s in [self.left, self.mid, self.right]:
            s.opacity -= 10
            s.scale -= 0.1

        self.left.x -= 8
        self.left.y -= 1
        self.mid.x -= 4
        self.mid.y -= 4
        self.right.x -= 1
        self.right.y -= 8

    def draw(self):
        for s in [self.left, self.mid, self.right]:
            s.draw()
        
class PooMaster(object):
    def __init__(self):
        events.AddListener(self)
        self.pooSprites = []
        self.smearAnims = []
        self.deadAnims = []

    def On_DogPoo(self, pos):
        #print 'putting poo at', pos
        img = data.pngs['dookie.png']
        s = pyglet.sprite.Sprite(img, *pos)
        self.pooSprites.append(s)

    def On_DogPooSmear(self, pos):
        for p in self.pooSprites:
            if (p.x, p.y) == pos:
                self.pooSprites.remove(p)
                self.smearAnims.append( PooSmearAnim(pos, self) )

    def update(self, timechange):
        for anim in self.smearAnims:
            anim.update(timechange)
        for anim in self.deadAnims:
            self.smearAnims.remove(anim)
        self.deadAnims = []

    def draw(self):
        for s in self.pooSprites:
            s.draw()
        for s in self.smearAnims:
            s.draw()


def main():
    clock.schedule(rabbyt.add_time)

    window.game_window = Window(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
    rabbyt.set_default_attribs()

    bgPat = pyglet.image.SolidColorImagePattern((200,200,200,255))
    bg = pyglet.image.create(window.game_window.width, window.game_window.height, bgPat)

    dog = Dog()
    mowr = mower.Mower()
    guage = mower.Guage(mowr)
    bubbles.init()
    pooMaster = PooMaster()

    events.Fire('NewStage', narrative.foreshadowing)

    objs = [dog, mowr, guage]

    while not window.game_window.has_exit:
        tick = clock.tick()
        window.game_window.dispatch_events()

        bubbles.bubbleMaker.update(tick)
        for obj in objs:
            obj.update(tick)
        
        events.ConsumeEventQueue()

        rabbyt.clear((1, 1, 1))

        bg.blit(0,0)
        mowr.draw()
        guage.draw()
        pooMaster.draw()
        dog.draw()
        bubbles.bubbleMaker.draw()

        window.game_window.flip()

if __name__ == '__main__':
    main()

