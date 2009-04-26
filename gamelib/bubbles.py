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

import grass
from grass import GrassBlade, Lawn

class ThoughtBubble(object):
    bubble_width = 640
    bubble_bottom = 200
    bubble_left = 76
    def __init__(self, words):
        self.dying = False
        self.opacity = 220
        self.textOpacity = 1.0
        self.xPadding = 20
        self.yPadding = 20
        self.topimg = data.pngs['bubble_top']
        self.botimg = data.pngs['bubble_bottom']
        self.renderWords(words)

        win.push_handlers(self.on_mouse_press)

    def renderWords(self, words):
        myFont = data.fonts['default']
        self.text = pyglet.font.Text(myFont, words,
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

    def update(self, timechange):
        if self.dying:
            self.opacity -= 10
            if self.opacity <= 0:
                self.opacity = 0
                events.Fire('BubbleDeath', self)
                self.die()

    def die(self):
        self.dying = False

    def on_mouse_press(self, x, y, button, modifiers):
        self.dying = True
        
            

def main():
    global win
    clock.schedule(rabbyt.add_time)

    win = Window(width=800, height=600)
    grass.win = win
    rabbyt.set_default_attribs()
    bgPat = pyglet.image.SolidColorImagePattern((0,0,0,255))
    bg = pyglet.image.create(win.width, win.height, bgPat)

    lawn = Lawn()
    bub = ThoughtBubble('Click to make this disappear. asdf asdf .qwer p30n fpin pp) ) *HNPO *H#NN ! #RFL')

    magicEventRegister(win, events, [bub])

    while not win.has_exit:
        tick = clock.tick()
        win.dispatch_events()

        lawn.update(tick)
        bub.update(tick)
        events.ConsumeEventQueue()

        rabbyt.clear((1, 1, 1))
        bg.blit(0,0)

        lawn.draw()
        bub.draw()

        win.flip()

if __name__ == '__main__':
    main()

