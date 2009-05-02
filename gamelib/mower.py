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
from util import magicEventRegister
from util import logicalToPerspective
from util import Rect

import bubbles

rabbyt.data_director = os.path.dirname(__file__)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

EDGE = 300

class RPMBubble(bubbles.ThoughtBubble):
    def __init__(self):
        super(RPMBubble, self).__init__('__')
    def On_MowerRPM(self, rpms):
        self.renderWords( str(rpms) )

class Mower(pyglet.sprite.Sprite):
    hint1Done = False
    hint2Done = False
    DIFFICULTY_EASY = 2
    DIFFICULTY_HARD = 10

    RPMGOAL = 1500 # how many rpms needed to start
    def __init__(self, color=(255,255,255)):
        self.rect = Rect(300, 260, 50, 10)
        self.startableImg = data.pngs['mower.png']
        self.unstartableImg = data.pngs['mower_inactive.png']
        self.highlighted = False
        super(Mower,self).__init__(self.startableImg)
        self.xy = 10, 260

        self.startable = True
        self.difficulty = self.DIFFICULTY_EASY
        self.pullcord = None
        self.rpms = 0

        window.game_window.push_handlers(self.on_mouse_press)
        window.game_window.push_handlers(self.on_mouse_release)
        window.game_window.push_handlers(self.on_mouse_motion)
        events.AddListener(self)

    def getxy(self):
        return self.x, self.y
    def setxy(self, xy):
        self.rect.x = xy[0]
        self.rect.y = xy[1]
    xy = property(getxy, setxy)

    def __str__(self):
        return '<Mower %s %s %s>' % (self.x, self.y, id(self))

    def resetLocation(self):
        print 'resetting location'
        self.rect.x = 10
        self.rect.y = 260

    def collides(self,x,y):
        distance = math.sqrt((x-self.x)**2 + (y-self.y)**2)
        return distance < self.width*self.scale

    def update(self, timeChange):
        if self.startable:
            self.image = self.startableImg
        else:
            self.image = self.unstartableImg
        if self.highlighted:
            self.color = (255,20,25)
        else:
            self.color = (255,255,255)

        if self.pullcord:
            self.pullcord.update(timeChange)
            self.rpms += self.pullcord.powerAdded

        if self.rpms:
            # internal friction
            self.rpms -= self.difficulty + 50.0/math.log(20+self.rpms)
            self.rpms = max(0, self.rpms)
            events.Fire('MowerRPM', self.rpms)
            if self.rpms >= self.RPMGOAL:
                events.Fire('MowerStart', self)
                self.startable = False
                self.stopPullCord()
                self.rpms = 0

        self.x = self.rect.x
        self.y = self.rect.y

    def draw(self):
        super(Mower, self).draw()
        if self.pullcord:
            self.pullcord.draw()

    def draw_mow_rect(self):
        glColor4f(0, 0, 1, .5)

        glBegin(GL_POLYGON)
        glVertex2d(*self.rect.bottomleft)
        glVertex2d(*self.rect.topleft)
        glVertex2d(*self.rect.topright)
        glVertex2d(*self.rect.bottomright)
        glEnd()

        glColor4f(1, 1, 1, 1)


    def startPullCord(self, x, y, button):
        # give a little initial rpms so the visual cues come up
        self.rpms = 150
        self.pullcord = PullCord(x,y)

    def stopPullCord(self):
        if self.pullcord:
            self.pullcord.die()
            self.pullcord = None

    def on_mouse_press(self, x, y, button, modifiers):
        if self.startable and self.collides(x,y):
            self.startPullCord(x, y, button)
            if not Mower.hint2Done:
                events.Fire('NewHint',
                        'I need to jerk the cord *fast* to get this old'
                        'junker to start up')
                Mower.hint2Done = True

    def on_mouse_release(self, x, y, button, modifiers):
        self.stopPullCord()

    def on_mouse_motion(self, x, y, dx, dy):
        if self.collides(x,y):
            self.highlighted = True
            if not Mower.hint1Done:
                events.Fire('NewHint',
                            'Once a day, I can start the '
                            'lawnmower by clicking and dragging')
                Mower.hint1Done = True
        else:
            self.highlighted = False

    def On_Sunrise(self):
        self.startable = True

    def On_Sunset(self):
        self.startable = False

    def On_LawnMowed(self):
        if narrative.StoryTeller.phase == narrative.anguish:
            events.Fire('NewThought', 'Green, tidy and still.  '
                        'I just want it to stay like this forever.')
        if narrative.StoryTeller.phase == narrative.fin:
            events.Fire('NewThought', 'my perfect lawn.  '
                        'complete and whole.  My island.'
                        )
        else:
            events.Fire('NewThought', 'Even.  Uniform.  Mine.  Perfect.')
        

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
        self.hand.image.anchor_x = self.hand.width/2
        self.hand.image.anchor_y = 0
        #window.game_window.set_mouse_cursor(self.handle)
        window.game_window.set_mouse_visible(False)

        self.origin = x,y
        self.newPos = x,y
        self.powerAdded = 0
        self.lastDelta = 0
        self.numCordParts = 0

        window.game_window.push_handlers(self.on_mouse_drag)

    def update(self, timechange):
        self.powerAdded = 0
        delta = math.sqrt(  (self.newPos[0]-self.origin[0])**2 
                          + (self.newPos[1]-self.origin[1])**2  )
        self.powerAdded = max(0, delta - self.lastDelta)
        self.lastDelta = delta

        self.numCordParts = min(self.MAX_CORD_PARTS, int(delta/30))


    def draw(self):
        dx = self.newPos[0] - self.origin[0]
        dy = self.newPos[1] - self.origin[1]
        self.hand.rotation = math.degrees(math.atan2(dx, -dy))
        scale = 0.5 + 0.5*(dx/600.0)
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
        window.game_window.set_mouse_visible(True)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.newPos = x,y


class Guage(object):
    def __init__(self, mower):
        self.x, self.y = 30, 320
        img = data.pngs['guage.png']
        self.guage = pyglet.sprite.Sprite(img, self.x, self.y)
        img = data.pngs['guage_needle.png']
        self.needle = pyglet.sprite.Sprite(img, self.x, self.y+10)
        self.needle.image.anchor_y = self.needle.height/2

        self.mower = mower
        self.pct = 0

        events.AddListener(self)

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
    clock.schedule(rabbyt.add_time)

    window.game_window = Window(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
    rabbyt.set_default_attribs()

    mower = Mower()
    bubble = RPMBubble()
    guage = Guage(mower)

    objs = [mower, guage, bubble]
    magicEventRegister(window.game_window, events, objs)

    while not window.game_window.has_exit:
        tick = clock.tick()
        window.game_window.dispatch_events()

        for obj in objs:
            obj.update(tick)
        
        events.ConsumeEventQueue()

        rabbyt.clear((1, 1, 1))

        guage.draw()
        mower.draw()
        bubble.draw()

        window.game_window.flip()

if __name__ == '__main__':
    main()

