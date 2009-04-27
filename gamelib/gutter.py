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

from grass import GrassBlade, Lawn

class GutterWater(rabbyt.sprites.Sprite):
    def __init__(self, pos):
        img = data.textures['grassblade.png']
        rabbyt.sprites.Sprite.__init__(self, img)
        self.logicalX = pos[0]
        self.logicalY = pos[1]
        self.xy = logicalToPerspective(*pos)
        self.scale = (1.0 + (300.0-pos[1])/200.0)/2
        self.logicalZ = random.randint(-2,3)

        self.north, self.east, self.south, self.west = None,None,None,None

        self.windEffects = {'duration': 0,
                            'offset': 0,
                            'flutter': 0,
                            'countdown': 0,
                           }

    def __str__(self):
        return '<Blade %s %s %s>' % (self.logicalX, self.logicalY, id(self))

    def setLogicalXY(self, x, y):
        self.logicalX = x
        self.logicalY = y
        self.xy = logicalToPerspective(x,y)
        self.scale = (1.0 + (300.0-y)/200.0)/2

    def collides(self,x,y):
        distance = math.sqrt((x-self.x)**2 + (y-self.y)**2)
        if distance < (self.bounding_radius/2):
            return True
        return False

    def update(self, timeChange):
        newY = self.logicalY
        newX = self.logicalX
        if self.windEffects['countdown'] > 0:
            # TODO: not quite perfect math here. but approximate
            intensity = 1.0 - abs(self.windEffects['duration']/2 - (self.windEffects['duration']-self.windEffects['countdown']))
            self.windEffects['countdown'] -= timeChange
            if self.windEffects['countdown'] <= 0:
                newX = self.logicalX
            newX = self.logicalX + self.windEffects['offset']*intensity +\
                     random.randint(*self.windEffects['flutter'])
        if newX != self.logicalX:
            delta = newX-self.logicalX
            if self.north:
                self.north.pullX( delta/4 )
            if self.south:
                self.south.pullX( delta/4 )
            if newX > self.logicalX:
                if self.west:
                    self.west.pullX( delta/2 )
            else:
                if self.east:
                    self.east.pullX( delta/2 )

        self.xy = logicalToPerspective(newX, newY)
        self.y += self.logicalZ*self.scale

    def pullX(self, delta):
        self.x += delta

    def pullY(self, delta):
        self.y += delta

    def on_mouse_scroll(self, x, y, scrollx, scrolly):
        if self.collides(x,y):
            if scrolly > 0:
                print 'self collides.  self.x, self.y', self.x, self.y
                print 'info x, y, sx, sy', x, y, scrollx, scrolly
                self.logicalZ += 5
                def popNeighbor(n):
                    if n and n.logicalZ < self.logicalZ:
                        n.logicalZ += 5/2
                    
                popNeighbor(self.north)
                popNeighbor(self.east)
                popNeighbor(self.south)
                popNeighbor(self.west)

            elif scrolly < 0:
                self.logicalZ -= 5
                def pushNeighbor(n):
                    if n and n.logicalZ > self.logicalZ:
                        n.logicalZ -= 5/2
                    
                pushNeighbor(self.north)
                pushNeighbor(self.east)
                pushNeighbor(self.south)
                pushNeighbor(self.west)
                        

    def On_Wind(self):
        dur = random.random()*2 #between 0 and 2 seconds
        self.windEffects = {'duration': dur,
                            'offset': random.randint(0,5),
                            'flutter': (0,1),
                            'countdown': dur,
                           }
        
class Lawn(object):
    def __init__(self):
        self.blades = []
        for j in range(7):
            self.blades.append([])
            for i in range(20):
                self.blades[j].append(GrassBlade((i*40, (2+j)*30)))
        for j, row in enumerate(self.blades):
            for i, blade in enumerate(row):
                try:
                    blade.north = self.blades[j+1][i]
                except IndexError: pass
                try:
                    blade.east = self.blades[j][i+1]
                except IndexError: pass
                if j-1 >= 0:
                    blade.south = self.blades[j-1][i]
                if i-1 >= 0:
                    blade.west = self.blades[j][i-1]

    def __iter__(self):
        def myIter():
            for row in reversed(self.blades): #faraway rows first
                for blade in row:
                    yield blade
        return myIter()
        

    def update(self, timechange):
        for blade in self:
            blade.update(timechange)

    def draw(self):
        for blade in self:
            blade.render()

class Wind(object):
    def __init__(self):
        self.countdown = random.randint(1, 5)
        
    def update(self, timechange):
        self.countdown -= timechange
        #print self.countdown
        if self.countdown > 0:
            return

        self.countdown = random.randint(5, 30)
        events.Fire('Wind')

def main():
    global win
    clock.schedule(rabbyt.add_time)

    win = Window(width=800, height=600)
    rabbyt.set_default_attribs()

    lawn = Lawn()
    wind = Wind()

    magicEventRegister(win, events, list(lawn))

    while not win.has_exit:
        tick = clock.tick()
        win.dispatch_events()

        lawn.update(tick)
        wind.update(tick)
        events.ConsumeEventQueue()

        rabbyt.clear((1, 1, 1))

        lawn.draw()

        win.flip()

if __name__ == '__main__':
    main()

