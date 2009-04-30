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

rabbyt.data_director = os.path.dirname(__file__)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

win = None

bubbleMaker = None

def init():
    global bubbleMaker
    bubbleMaker = BubbleMaker()

class ThoughtBubble(object):
    bubble_width = 640
    bubble_bottom = 200
    bubble_left = 76
    myFont = data.fonts['default']
    fadeRate = 10

    def __init__(self, words):
        self.dying = False
        self.birthing = True
        self.opacity = 0
        self.maxOpacity = 220
        self.textOpacity = 1.0
        self.xPadding = 20
        self.yPadding = 20
        self.topimg = data.pngs['bubble_top']
        self.botimg = data.pngs['bubble_bottom']
        self.renderWords(words)
        self.bubbleDrops = []
        self.startBubbleDrops()

        win.push_handlers(self.on_mouse_press)

    def get_x(self):
        return self.bubble_left
    x = property(get_x)

    def get_y(self):
        return self.bubble_bottom
    y = property(get_y)

    def get_width(self):
        return self.bubble_width
    width = property(get_width)

    def startBubbleDrops(self):
        bdrop = BubbleDrop(self.x + self.width*0.6, self.y - 30, 1.0)
        self.bubbleDrops.append(bdrop)
        bdrop = BubbleDrop(self.x + self.width*0.5, self.y - 40, 0.5)
        self.bubbleDrops.append(bdrop)

    def renderWords(self, words):
        self.text = pyglet.font.Text(self.myFont, words,
                                     color=(0,255,0,self.textOpacity))
        self.text.width = self.bubble_width - self.xPadding*2
        self.text.halign = 'center'
        self.text.valign = 'bottom'
        self.text.y = self.bubble_bottom + self.botimg.height + self.yPadding
        self.text.x = self.bubble_left + self.xPadding

    def draw(self):
        pat = pyglet.image.SolidColorImagePattern((255,255,255,self.opacity))
        bgimg = pyglet.image.create(self.bubble_width,
                                    self.text.height + self.yPadding*2,
                                    pat)
        s = pyglet.sprite.Sprite(self.botimg, 0, self.bubble_bottom)
        s.opacity = self.opacity
        s.draw()
        bgimg.blit(self.bubble_left,  self.bubble_bottom + self.botimg.height)
        s = pyglet.sprite.Sprite(self.topimg, 0,
                                 self.bubble_bottom + self.botimg.height + bgimg.height)
        s.opacity = self.opacity
        s.draw()
        self.text.draw()

        for bdrop in self.bubbleDrops:
            bdrop.draw()

    def update(self, timechange):
        for bdrop in self.bubbleDrops:
            bdrop.update(timechange)
        if self.dying:
            self.opacity -= self.fadeRate
            for bdrop in self.bubbleDrops:
                bdrop.scale = bdrop.scale*0.9
            if self.opacity <= 0:
                self.opacity = 0
                events.Fire('BubbleDeath', self)
                self.die()
        elif self.birthing:
            self.opacity += 10
            if self.opacity >= self.maxOpacity:
                self.opacity = self.maxOpacity
                self.birthing = False
                
    def die(self):
        self.dying = False
        self.bubbleDrops = []

    def on_mouse_press(self, x, y, button, modifiers):
        if not self.birthing:
            self.dying = True
        
            
class HintBubble(ThoughtBubble):
    bubble_width = 333
    bubble_bottom = 460
    bubble_left = 29
    myFont = data.fonts['hint']
    fadeRate = 2

    def __init__(self, words):
        self.dying = False
        self.birthing = True
        self.opacity = 0
        self.maxOpacity = 220
        self.textOpacity = 1.0
        self.xPadding = 20
        self.yPadding = 20
        self.topimg = data.pngs['bubble_hint_top']
        self.botimg = data.pngs['bubble_hint_bottom']
        self.renderWords(words)
        self.bubbleDrops = []
        self.startBubbleDrops()

        win.push_handlers(self.on_mouse_press)


class BubbleDrop(pyglet.sprite.Sprite):
    def __init__(self, x, y, scale):
        img = data.pngs['bubble_drop_motion']
        super(BubbleDrop, self).__init__(img, 0, y)
        self.image.anchor_x = self.width/2
        self.image.anchor_y = self.height/2
        self.scale = scale
        self.dest = x,y
        self.velocityX = 0
        self.velocityY = 0
        self.opacity = 200
        
    def die(self):
        pass

    def distanceTo(self, x, y):
        return math.sqrt((x-self.x)**2 + (y-self.y)**2)

    def reachDest(self):
        self.image = data.pngs['bubble_drop']
        self.velocityX = 0

    def update(self, timeChange):
        if (self.x, self.y) == self.dest:
            return
        dx = self.distanceTo(*self.dest)
        if dx < 5:
            self.reachDest()
            self.x = self.dest[0]
            return
        else:
            self.velocityX = 5 * math.log(dx)

        self.x += self.velocityX

        

class BubbleMaker(object):
    def __init__(self):
        self.tBubbles = []
        self.hBubbles = []

        events.AddListener(self)

    def On_NewThought(self, msg):
        bubble = ThoughtBubble(msg)
        for bub in self.tBubbles:
            bub.dying = True
        self.tBubbles.append(bubble)

    def On_NewHint(self, msg):
        bubble = HintBubble(msg)
        for bub in self.hBubbles:
            bub.dying = True
        self.hBubbles.append(bubble)

    def On_BubbleDeath(self, bub):
        if bub in self.tBubbles:
            self.tBubbles.remove(bub)
        if bub in self.hBubbles:
            self.hBubbles.remove(bub)
        
    def update(self, timeChange):
        for bub in self.tBubbles + self.hBubbles:
            bub.update(timeChange)

    def draw(self):
        for bub in self.tBubbles + self.hBubbles:
            bub.draw()
    

def main():
    global win
    clock.schedule(rabbyt.add_time)

    win = Window(width=800, height=600)
    rabbyt.set_default_attribs()
    bgPat = pyglet.image.SolidColorImagePattern((0,0,0,255))
    bg = pyglet.image.create(win.width, win.height, bgPat)

    bub = ThoughtBubble('Click to make this disappear.'
                        ' This is a thought bubble.'
                        ' asdf asdf .qwer p30n fpin pp) ) *HNPO *H#NN ! #RFL')

    bub2 = HintBubble('This is a hint bubble.')

    maker = BubbleMaker()

    magicEventRegister(win, events, [bub])

    counter = 0

    objects = [bub, bub2, maker]

    while not win.has_exit:
        tick = clock.tick()
        win.dispatch_events()

        counter += tick
        if counter > 8:
            counter = -10
            events.Fire('NewThought', 'new thought')
            

        for obj in objects:
            obj.update(tick)

        events.ConsumeEventQueue()

        rabbyt.clear((1, 1, 1))
        bg.blit(0,0)

        for obj in objects:
            obj.draw()

        win.flip()

if __name__ == '__main__':
    main()

