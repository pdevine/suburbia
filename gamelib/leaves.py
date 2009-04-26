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

rabbyt.data_director = os.path.dirname(__file__)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

win = None


class Leaf(pyglet.sprite.Sprite):
    def __init__(self):
        img = data.textures['grassblade.png']
        super(Leaf,self).__init__(img)
        self.blowing = True
        self.logicalX = 0
        self.logicalY = random.randint(1,200)
        self.xy = logicalToPerspective(self.logicalX, self.logicalY)
        self.logicalZ = random.randint(100,150)
        self.velocityX = 0.1
        self.velocityZ = 0

        self.image.anchor_x = self.image.width/2
        self.image.anchor_y = 7
        self.clumpMates = []

        self.windEffects = {'duration': 0,
                            'offset': 0,
                            'flutter': 0,
                            'countdown': 0,
                           }

        print 'created leaf at', self.logicalX, self.logicalY
        print 'at', self.xy
        #win.push_handlers(self.on_
        events.AddListener(self)

    def getxy(self):
        return self.x, self.y
    def setxy(self, xy):
        self.x = xy[0]
        self.y = xy[1]
    xy = property(getxy, setxy)


    def __str__(self):
        return '<Leaf %s %s %s>' % (self.logicalX, self.logicalY, id(self))

    def __cmp__(self, other):
        return cmp(self.logicalX, other.logicalX)

    def die(self):
        events.Fire('LeafDeath', self)

    def setLogicalXY(self, x, y):
        self.logicalX = x
        self.logicalY = y
        self.xy = logicalToPerspective(x,y)

    def collides(self,x,y):
        distance = math.sqrt((x-self.x)**2 + (y-self.y)**2)
        if distance < 10:
            return True
        return False

    def update(self, timeChange):
        newY = self.logicalY
        newX = self.logicalX
        if self.windEffects['countdown'] > 0:
            self.windEffects['countdown'] -= timeChange

            horizAccel= 0
            # TODO: not quite perfect math here. but approximate
            intensity = 1.0 - abs(self.windEffects['duration']/2 - (self.windEffects['duration']-self.windEffects['countdown']))

            horizAccel = self.windEffects['offset']*intensity
            rotateAmount = self.windEffects['offset']*intensity

            if self.logicalZ <= 0:
                # on ground - friction means blow around less
                horizAccel *= 0.7
                # on ground - rotate more
                self.logicalZ = 0
                self.velocityZ = 0
            else:
                # in the air - rotate, but not so much
                rotateAmount *= 0.5

            self.rotation += rotateAmount
            self.velocityX += horizAccel

            
        # fall due to gravity
        if self.logicalZ > 0:
            self.velocityZ -= 0.01
            self.logicalZ += self.velocityZ

            # minimal friction in the air
            self.velocityX *= 0.6
            self.velocityX = max(0.1, self.velocityX)

        # apply friction
        else:
            self.velocityX *= 0.4

        newX = self.logicalX + self.velocityX

        if newX != self.logicalX:
            delta = newX-self.logicalX
            for mate in self.clumpMates:
                mate.pullX( delta/2 )

        self.scale = (1.0 + (300.0-self.logicalY)/200.0)/2
        self.setLogicalXY(newX, newY)
        self.clumpMates = [] #clear out the clumpmates in case we've moved away
        self.y += self.logicalZ*self.scale

        if (self.x > SCREEN_WIDTH + 40
           or self.x < -40
           or self.y > SCREEN_HEIGHT
           or self.y < -40):
            self.die()

        #print 'updated leaf to', self
        #print 'at', self.xy


    def pullX(self, delta):
        self.x += delta

    def pullY(self, delta):
        self.y += delta

    def On_Wind(self):
        print 'blowing', self
        dur = random.random()*2 #between 0 and 2 seconds
        self.blowing = True
        self.windEffects = {'duration': dur,
                            'offset': random.randint(0,5),
                            'offsetZ': random.randint(0,3),
                            'flutter': (0,1),
                            'countdown': dur,
                           }
        self.velocityZ += self.windEffects['offsetZ']
        
class LeafGroup(list):
    def update(self, timechange):
        lastLeaf = None
        for leaf in sorted(self): #go through them in sorted order
            leaf.update(timechange)
            if lastLeaf and leaf.collides(*lastLeaf.xy):
                leaf.clumpMates.append(lastLeaf)
                lastLeaf.clumpMates.append(leaf)

            lastLeaf = leaf

    def __hash__(self):
        # wow.  big hack.
        return id(self)

    def draw(self):
        for leaf in sorted(self):
            leaf.draw()
            
    def On_LeafBirth(self, leaf):
        self.append(leaf)

    def On_LeafDeath(self, leaf):
        self.remove(leaf)

class LeafGenerator(object):
    def __init__(self):
        self.countdown = random.randint(0, 1)

    def update(self, timechange):
        self.countdown -= timechange
        #print self.countdown
        if self.countdown > 0:
            return

        print 'birthing leaf'
        self.countdown = random.randint(4, 6)
        leaf = Leaf()
        events.Fire('LeafBirth', leaf)

class Wind(object):
    def __init__(self):
        self.countdown = random.randint(1, 5)
        
    def update(self, timechange):
        self.countdown -= timechange
        #print self.countdown
        if self.countdown > 0:
            return

        self.countdown = random.randint(3, 5)
        events.Fire('Wind')

def main():
    global win
    clock.schedule(rabbyt.add_time)

    win = Window(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
    rabbyt.set_default_attribs()

    wind = Wind()
    leafgen = LeafGenerator()
    leaves = LeafGroup()

    objs = [leafgen, leaves]
    magicEventRegister(win, events, objs)

    while not win.has_exit:
        tick = clock.tick()
        win.dispatch_events()

        for obj in objs:
            obj.update(tick)
        wind.update(tick)
        
        events.ConsumeEventQueue()

        rabbyt.clear((1, 1, 1))

        leaves.draw()

        win.flip()

if __name__ == '__main__':
    main()
