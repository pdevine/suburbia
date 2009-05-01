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

from pyglet.gl import *
from util import magicEventRegister
from util import logicalToPerspective

import sky

rabbyt.data_director = os.path.dirname(__file__)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

EDGE = 60
LOGICAL_X_EDGE = 800

win = None

class Leaf(pyglet.sprite.Sprite):
    hintDone = False
    def __init__(self, color=(255,255,255)):
        img = data.textures['grassblade.png']
        self.blowing = True
        self.highlighted = False
        self.sweptOffEdge = False
        self.logicalX = random.randint(20,60)
        self.logicalY = random.randint(20,260)
        self.logicalZ = random.randint(100,150)
        super(Leaf,self).__init__(img)
        self.origColor = color
        self.xy = logicalToPerspective(self.logicalX, self.logicalY)
        self.velocityX = 0.1
        self.velocityY = 0
        self.velocityZ = 0

        self.image.anchor_x = self.image.width/2
        self.image.anchor_y = 7
        self.clumpMates = []

        self.windEffects = {'duration': 0,
                            'offset': 0,
                            'flutter': 0,
                            'countdown': 0,
                           }

        #print 'created leaf at', self.logicalX, self.logicalY
        #print 'at', self.xy
        win.push_handlers(self.on_mouse_scroll)
        win.push_handlers(self.on_mouse_press)
        win.push_handlers(self.on_mouse_motion)
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
        #print 'collide distance', distance
        if distance < self.width*self.scale:
            return True
        return False

    def logicalCollides(self, x, y, z):
        distanceX = abs(x-self.logicalX)
        distanceY = abs(y-self.logicalY)
        distanceZ = abs(z-self.logicalZ)
        return all((distanceX < 40, distanceY < 40, distanceZ < 1))

    def update(self, timeChange):
        if self.sweptOffEdge:
            return self.offEdgeUpdate(timeChange)

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
                rotateAmount /= 1+ len(self.clumpMates)
            else:
                # in the air - rotate, but not so much
                rotateAmount *= 0.5

            self.rotation += rotateAmount
            self.velocityX += horizAccel

            
        # fall due to gravity
        if self.logicalZ > 0:
            self.velocityZ -= 0.01
            self.velocityZ -= len(self.clumpMates)
            self.logicalZ += self.velocityZ

            # minimal friction in the air
            self.velocityX *= 0.7
            self.velocityX = max(0.1, self.velocityX)

        # apply friction
        else:
            self.velocityX *= 0.4
            self.velocityX /= 1+ len(self.clumpMates)
            self.velocityY *= 0.8

        newX = self.logicalX + self.velocityX
        newY = self.logicalY + self.velocityY

        if newX != self.logicalX:
            delta = newX-self.logicalX
            for mate in self.clumpMates:
                mate.pullX( delta/1.4 )
        if newY != self.logicalY:
            delta = newY-self.logicalY
            for mate in self.clumpMates:
                mate.pullY( delta )

        self.scale = (1.0 + (300.0-self.logicalY)/200.0)/2
        if self.clumpMates:
            self.color = (255,240,240)
        else:
            self.color = self.origColor
        if self.highlighted:
            self.color = (25,200,25)
            #self.color = (20,255,0)

        self.setLogicalXY(newX, newY)
        self.y += self.logicalZ*self.scale

        if (self.x > SCREEN_WIDTH + 40
           or self.x < -40
           or self.y > SCREEN_HEIGHT + 40
           or self.y < -40):
            self.die()

        #print self.logicalY
        if self.logicalY < EDGE:
            self.startDying()

        if self.logicalZ == 0 and self.logicalX > LOGICAL_X_EDGE:
            self.startDying()

        self.clumpMates = [] #clear out the clumpmates in case we've moved away

        #print 'updated leaf to', self
        #print 'at', self.xy

    def startDying(self):
        events.Fire('LeafSweptOff')
        self.sweptOffEdge = True

    def offEdgeUpdate(self, timechange):
        self.opacity -= timechange*4
        if self.opacity < 0:
            self.die()

    def pullX(self, delta):
        self.x += delta

    def pullY(self, delta):
        if self.velocityY < 1:
            self.velocityY = delta/2

    def sweep(self):
        if self.logicalZ > 0:
            # can only sweep ones on the ground
            return
        self.velocityY -= 3
        self.velocityZ = random.randint(0,4)

    def On_Wind(self):
        dur = random.random()*2 #between 0 and 2 seconds
        self.blowing = True
        self.windEffects = {'duration': dur,
                            'offset': random.randint(0,5),
                            'offsetZ': random.randint(0,3),
                            'flutter': (0,1),
                            'countdown': dur,
                           }
        self.velocityZ += self.windEffects['offsetZ']


    def on_mouse_scroll(self, x, y, scrollx, scrolly):
        if self.collides(x,y):
            if scrolly < 0:
                #print 'self collides.  self.x, self.y', self.x, self.y
                #print 'info x, y, sx, sy', x, y, scrollx, scrolly
                self.sweep()

    def on_mouse_press(self, x, y, button, modifiers):
        if self.collides(x,y):
            self.sweep()

    def on_mouse_motion(self, x, y, dx, dy):
        if self.collides(x,y):
            self.highlighted = True
            if not Leaf.hintDone:
                events.Fire('NewHint', 'I can sweep these up by using the mouse wheel or the mouse buttons.')
                Leaf.hintDone = True
        else:
            self.highlighted = False
        

class LeafGroup(list):
    def update(self, timechange):
        lastLeaf = None
        for leaf in sorted(self): #go through them in sorted order
            leaf.update(timechange)
            if lastLeaf and leaf.logicalCollides(lastLeaf.logicalX, lastLeaf.logicalY, lastLeaf.logicalZ):
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
    rate = (1,6)
    def __init__(self):
        self.countdown = random.randint(0, 1)
        self.brownness = 0
        self.count = 0

        events.AddListener(self)

    def update(self, timechange):
        self.countdown -= timechange
        self.brownness += 0.1*timechange
        #red = 255
        #green = 255
        ##green = 128+(math.sin(self.brownness)+1)*128
        #blue = 128*(math.cos(self.brownness)+1)
        #color = (red, green, blue)
        color = (255,255,255)
        if self.countdown > 0 or self.count >50:
            return

        #print 'birthing leaf'
        self.countdown = random.randint(*self.rate)
        # TODO: this is debug
        self.countdown = random.random()
        leaf = Leaf(color)
        events.Fire('LeafBirth', leaf)
        self.count += 1

    def On_LeafSweptOff(self):
        self.count -= 1


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

    win = pyglet.window.Window(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
    window.set_window(win)
    rabbyt.set_default_attribs()
    bubbles.init()
    bubbles.win = win

    wind = Wind()
    leafgen = LeafGenerator()
    leaves = LeafGroup()

    bg = sky.Background()

    objs = [leafgen, leaves]
    magicEventRegister(win, events, objs)

    while not win.has_exit:
        tick = clock.tick()
        win.dispatch_events()

        bubbles.bubbleMaker.update(tick)
        bg.update(tick)
        for obj in objs:
            obj.update(tick)
        wind.update(tick)
        
        events.ConsumeEventQueue()

        rabbyt.clear((1, 1, 1))

        bg.draw()
        leaves.draw()
        bubbles.bubbleMaker.draw()

        win.flip()

if __name__ == '__main__':
    main()

