import os.path
import math
import random
import rabbyt
import pyglet
import pyglet.window
from pyglet import clock
from pyglet import image
import random
import euclid
import data
import events
import window

from pyglet.gl import *
from util import magicEventRegister

rabbyt.data_director = os.path.dirname(__file__)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

bubbleMaker = None

DOGYELLS = [
'Get off!',
'Gah!  out!',
'Take off!']

def init():
    global bubbleMaker
    bubbleMaker = BubbleMaker()
    #print 'just made a bubble maker'


class Bubble(object):
    xPadding = 20
    yPadding = 20
    textOpacity = 1.0

    def renderWords(self, words):
        self.text = pyglet.font.Text(self.myFont, words,
                                     color=(0,255,0,self.textOpacity))
        self.text.width = self.width - self.xPadding*2
        self.text.halign = 'center'
        self.text.valign = 'bottom'
        self.text.y = self.get_text_y()
        self.text.x = self.x + self.xPadding

    def die(self):
        self.dying = False
        events.Fire('BubbleDeath', self)


class ThoughtBubble(Bubble):
    myFont = data.fonts['default']
    bubble_width = 640
    bubble_bottom = 200
    bubble_left = 76
    fadeRate = 10

    def __init__(self, words):
        self.dying = False
        self.birthing = True
        self.opacity = 0
        self.maxOpacity = 220
        img = data.pngs['bubble_bottom']
        self.botSprite = pyglet.sprite.Sprite(img, 0, self.bubble_bottom)

        self.renderWords(words)

        img = data.pngs['bubble_top']
        top_y = self.y + self.botSprite.height + self.text.height + self.yPadding*2
        self.topSprite = pyglet.sprite.Sprite(img, 0, top_y)

        pat = pyglet.image.SolidColorImagePattern((255,255,255,255))
        img = pyglet.image.create(self.bubble_width,
                                  self.text.height + self.yPadding*2,
                                  pat)
        self.bgSprite = pyglet.sprite.Sprite(img, self.x,
                                             self.y + self.botSprite.height)


        self.bubbleDrops = []
        self.startBubbleDrops()

        window.game_window.push_handlers(self.on_mouse_press)
        window.game_window.push_handlers(self.on_mouse_scroll)

    def get_x(self):
        return self.bubble_left
    x = property(get_x)

    def get_y(self):
        return self.bubble_bottom
    y = property(get_y)

    def get_width(self):
        return self.bubble_width
    width = property(get_width)

    def get_text_y(self):
        return self.y + self.botSprite.height + self.yPadding

    def startBubbleDrops(self):
        bdrop = BubbleDrop(self.x + self.width*0.6, self.y - 30, 1.0)
        self.bubbleDrops.append(bdrop)
        bdrop = BubbleDrop(self.x + self.width*0.5, self.y - 40, 0.5)
        self.bubbleDrops.append(bdrop)

    def draw(self):
        self.botSprite.opacity = self.opacity
        self.botSprite.draw()

        self.bgSprite.opacity = self.opacity
        self.bgSprite.draw()

        self.topSprite.opacity = self.opacity
        self.topSprite.draw()

        self.text.draw()

        for bdrop in self.bubbleDrops:
            bdrop.draw()

    def update(self, timechange):
        for bdrop in self.bubbleDrops:
            bdrop.update(timechange)
        if self.dying:
            self.opacity -= self.fadeRate
            for bdrop in self.bubbleDrops:
                bdrop.scale = bdrop.scale*0.95
            if self.opacity <= 0:
                self.opacity = 0
                self.die()
        elif self.birthing:
            self.opacity += 10
            if self.opacity >= self.maxOpacity:
                self.opacity = self.maxOpacity
                self.birthing = False
                
    def die(self):
        super(ThoughtBubble, self).die()
        self.bubbleDrops = []

    def on_mouse_press(self, x, y, button, modifiers):
        if not self.birthing:
            self.dying = True

    def on_mouse_scroll(self, *args):
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

        img = data.pngs['bubble_hint_bottom']
        self.botSprite = pyglet.sprite.Sprite(img, 0, self.y)

        self.renderWords(words)

        img = data.pngs['bubble_hint_top']
        top_y = self.y + self.botSprite.height + self.text.height + self.yPadding*2
        self.topSprite = pyglet.sprite.Sprite(img, 0, top_y)

        pat = pyglet.image.SolidColorImagePattern((255,255,255,255))
        img = pyglet.image.create(self.bubble_width,
                                  self.text.height + self.yPadding*2,
                                  pat)
        self.bgSprite = pyglet.sprite.Sprite(img, self.x,
                                             self.y + self.botSprite.height)

        self.bubbleDrops = []
        self.startBubbleDrops()

        window.game_window.push_handlers(self.on_mouse_press)
        window.game_window.push_handlers(self.on_mouse_scroll)


# -----------------------------------------------------------------------------
class YellBubble(Bubble, pyglet.sprite.Sprite):
    fadeRate = 40
    myFont = data.fonts['hint']

    def __init__(self, words):
        self.dying = False
        self.birthing = True
        img = data.pngs['bubble_yell.png']
        rand_x = random.randint(0,10)
        rand_y = random.randint(0,10)
        super(YellBubble, self).__init__(img, 40+rand_x, 10+rand_y)
        self.renderWords(words)
        self.opacity = 0
        self.maxOpacity = 255

    def get_text_y(self):
        return self.y + 80

    def update(self, timechange):
        if self.dying:
            self.opacity -= self.fadeRate
            if self.opacity <= 0:
                self.opacity = 0
                self.die()
        elif self.birthing:
            self.opacity += 60
            if self.opacity >= self.maxOpacity:
                self.opacity = self.maxOpacity
                self.birthing = False

    def draw(self):
        super(YellBubble, self).draw()
        self.text.draw()
                
    def die(self):
        super(YellBubble, self).die()


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
        self.yellCounter = {}

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

    def On_Shoo(self, x, y, dog):
        #print 'got shoo'
        yellbub = YellBubble(random.choice(DOGYELLS))
        self.yellCounter[yellbub] = 1.0

    def On_BubbleDeath(self, bub):
        if bub in self.tBubbles:
            self.tBubbles.remove(bub)
        if bub in self.hBubbles:
            self.hBubbles.remove(bub)
        if bub in self.yellCounter:
            del self.yellCounter[bub]
        
    def update(self, timeChange):
        for bub in self.tBubbles + self.hBubbles:
            bub.update(timeChange)
        for yellbub in self.yellCounter:
            yellbub.update(timeChange)
            self.yellCounter[yellbub] -= timeChange
            if self.yellCounter[yellbub] <= 0.0:
                yellbub.dying = True

    def draw(self):
        for bub in self.tBubbles + self.hBubbles + self.yellCounter.keys():
            bub.draw()
    

def main():
    clock.schedule(rabbyt.add_time)

    window.game_window.set_window(Window(width=800, height=600))
    rabbyt.set_default_attribs()
    bgPat = pyglet.image.SolidColorImagePattern((0,0,0,255))
    bg = pyglet.image.create(window.game_window.width, window.game_window.height, bgPat)

    bub = ThoughtBubble('Click to make this disappear.'
                        ' This is a thought bubble.'
                        ' asdf asdf .qwer p30n fpin pp) ) *HNPO *H#NN ! #RFL')

    bub2 = HintBubble('This is a hint bubble.')

    maker = BubbleMaker()

    magicEventRegister(window.game_window, events, [bub])

    counter = 0

    objects = [bub, bub2, maker]
    events.Fire('Shoo', 1,2,None)

    while not window.game_window.has_exit:
        tick = clock.tick()
        window.game_window.dispatch_events()

        counter += tick
        if counter > 8:
            counter = -10
            events.Fire('NewThought', 'new thought')
            events.Fire('Shoo', 3,4,None)
            
        for obj in objects:
            obj.update(tick)

        events.ConsumeEventQueue()

        rabbyt.clear((1, 1, 1))
        bg.blit(0,0)

        for obj in objects:
            obj.draw()

        window.game_window.flip()

if __name__ == '__main__':
    main()

