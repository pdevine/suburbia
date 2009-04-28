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

rabbyt.data_director = os.path.dirname(__file__)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

EDGE = 300

win = None

class RPMBubble(bubbles.ThoughtBubble):
    def __init__(self):
        super(RPMBubble, self).__init__('__')
    def On_MowerRPM(self, rpms):
        self.renderWords( str(rpms) )

class Mower(pyglet.sprite.Sprite):
    DIFFICULTY_EASY = 2
    DIFFICULTY_HARD = 10

    RPMGOAL = 1500 # how many rpms needed to start
    def __init__(self, color=(255,255,255)):
        img = data.pngs['lawnmower.png']
        self.highlighted = False
        super(Mower,self).__init__(img)
        self.xy = 720, 500

        self.difficulty = self.DIFFICULTY_EASY
        self.pullcord = None
        self.rpms = 0

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
        return '<Mower %s %s %s>' % (self.x, self.y, id(self))

    def collides(self,x,y):
        distance = math.sqrt((x-self.x)**2 + (y-self.y)**2)
        return distance < self.width*self.scale

    def update(self, timeChange):

        if self.highlighted:
            self.color = (255,20,25)
        else:
            self.color = (255,255,255)

        if self.pullcord:
            self.pullcord.update(timeChange)
            self.rpms += self.pullcord.powerAdded

        if self.rpms:
            # internal friction
            self.rpms -= self.difficulty + 10*(1/math.log(2+self.rpms))
            self.rpms = max(0, self.rpms)
            events.Fire('MowerRPM', self.rpms)
            if self.rpms >= self.RPMGOAL:
                events.Fire('MowerStart', self)
                self.stopPullCord()
                self.rpms = 0


    def draw(self):
        super(Mower, self).draw()
        if self.pullcord:
            self.pullcord.draw()

    def startPullCord(self, x, y, button):
        # give a little initial rpms so the visual cues come up
        self.rpms = 50
        self.pullcord = PullCord(x,y)

    def stopPullCord(self):
        if self.pullcord:
            self.pullcord.die()
            self.pullcord = None

    def on_mouse_press(self, x, y, button, modifiers):
        if self.collides(x,y):
            self.startPullCord(x, y, button)

    def on_mouse_release(self, x, y, button, modifiers):
        self.stopPullCord()

    def on_mouse_motion(self, x, y, dx, dy):
        if self.collides(x,y):
            self.highlighted = True
        else:
            self.highlighted = False
        

class PullCord(object):
    MAX_CORD_PARTS = 20
    def __init__(self, x, y):
        img = data.pngs['pullcord_seg.png']
        self.sprites = []
        for i in range(self.MAX_CORD_PARTS):
            s = pyglet.sprite.Sprite(img, i*10+x, y)
            s.image.anchor_x = s.width/2
            s.image.anchor_y = s.height/2
            self.sprites.append(s)
        img = data.pngs['pullcord_handle.png']
        #self.handle = pyglet.window.ImageMouseCursor(img)
        self.hand = pyglet.sprite.Sprite(img, x, y)
        self.hand.image.anchor_x = self.hand.width
        self.hand.image.anchor_y = self.hand.height/2
        #win.set_mouse_cursor(self.handle)
        win.set_mouse_visible(False)

        self.origin = x,y
        self.newPos = x,y
        self.powerAdded = 0
        self.lastDelta = 0
        self.numCordParts = 0

        win.push_handlers(self.on_mouse_drag)

    def update(self, timechange):
        self.powerAdded = 0
        delta = math.sqrt(  (self.newPos[0]-self.origin[0])**2 
                          + (self.newPos[1]-self.origin[1])**2  )
        self.powerAdded = max(0, delta - self.lastDelta)
        self.lastDelta = delta

        self.numCordParts = min(self.MAX_CORD_PARTS, int(delta/40))


    def draw(self):
        dx = self.newPos[0] - self.origin[0]
        dy = self.newPos[1] - self.origin[1]
        self.hand.rotation = math.degrees(math.atan2(dx, -dy))
        scale = 0.5 + 0.5*(-dx/600.0)
        self.hand.scale = scale
        self.hand.set_position(*self.newPos)
        self.hand.draw()
        for i in range(self.numCordParts):
            pct = float(i)/self.numCordParts
            x = self.origin[0] + (dx*pct)
            y = self.origin[1] + (dy*pct)
            self.sprites[i].x = x
            self.sprites[i].y = y
            self.sprites[i].scale = 0.4 + scale*pct
            self.sprites[i].draw()

    def die(self):
        #win.set_mouse_cursor(win.get_system_mouse_cursor(win.CURSOR_DEFAULT))
        win.set_mouse_visible(True)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.newPos = x,y


class Guage(object):
    def __init__(self, mower):
        self.x, self.y = 730, 520
        img = data.pngs['guage.png']
        self.guage = pyglet.sprite.Sprite(img, self.x, self.y)
        img = data.pngs['guage_needle.png']
        self.needle = pyglet.sprite.Sprite(img, self.x, self.y+10)
        self.needle.image.anchor_y = self.needle.height/2

        self.mower = mower
        self.pct = 0

    def update(self, timeChange):
        pass

    def draw(self):
        if self.pct == 0:
            return
        self.needle.y = self.y + self.guage.height*self.pct
        self.guage.draw()
        self.needle.draw()

    def die(self):
        self.pct = 0
        pass
        
    def On_MowerRPM(self, rpms):
        self.pct = float(rpms)/self.mower.RPMGOAL

    def On_MowerStart(self, rpms):
        self.die()


def main():
    global win
    clock.schedule(rabbyt.add_time)

    win = Window(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
    rabbyt.set_default_attribs()

    mower = Mower()
    bubbles.win = win
    bubble = RPMBubble()
    guage = Guage(mower)

    objs = [mower, guage, bubble]
    magicEventRegister(win, events, objs)

    while not win.has_exit:
        tick = clock.tick()
        win.dispatch_events()

        for obj in objs:
            obj.update(tick)
        
        events.ConsumeEventQueue()

        rabbyt.clear((1, 1, 1))

        guage.draw()
        mower.draw()
        bubble.draw()

        win.flip()

if __name__ == '__main__':
    main()

