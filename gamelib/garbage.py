from pyglet import image
import pyglet

from util import data_file
from util import Rect
from pyglet.sprite import Sprite
from random import randint
from pyglet.gl import *

import math
import window
import euclid
import events


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
import leaves
import window
import narrative


class GarbageCan:
    def __init__(self):
        self.image_opened = image.load(data_file('garbagecan-open.png'))
        self.image_closed = image.load(data_file('garbagecan-closed.png'))
        self.image_lid = image.load(data_file('garbagecan-lid.png'))

        self.opened = True
        self.lid_active = False
        self.can_active = False
        self.fallen = False
        self.can_highlighted = False
        self.lid_highlighted = True

        self.can_rect = Rect(0, 0, self.image_closed)
        self.can_rect.center = (80, 60)

        self.can_sprite = Sprite(self.image_opened)
        self.can_sprite.set_position(100 - self.image_opened.width / 2,
                                     100 - self.image_opened.height / 2)

        self.lid_rect = Rect(20, 40, self.image_lid)

        window.game_window.push_handlers(self.on_mouse_release)
        window.game_window.push_handlers(self.on_mouse_press)
        window.game_window.push_handlers(self.on_mouse_drag)
        window.game_window.push_handlers(self.on_mouse_motion)

        events.AddListener(self)

    def update(self, timechange):
        pass
    def draw(self):
        if not self.can_active:
            if self.can_highlighted:
                self.can_sprite.color = (255, 20, 25)
            else:
                self.can_sprite.color = (255, 255, 255)
        else:
            self.can_sprite.color = (255, 255, 255)

        self.can_sprite.draw()

        glColor4f(1, 1, 1, 1)

        if not self.lid_active:
            if self.lid_highlighted:
                glColor4f(1, 0.1, 0.1, 1)
            else:
                glColor4f(1, 1, 1, 1)
        
        if self.opened:
            self.image_lid.blit(*self.lid_rect.bottomleft)

        glColor4f(1, 1, 1, 1)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == 1:
            if self.opened and self.lid_rect.collide_point(x, y):
                self.set_lid_active()
            elif self.can_rect.collide_point(x, y):
                self.fallen = False
                self.set_can_active()
                self.can_sprite.rotation = 0

                if self.opened:
                    self.can_sprite.image = self.image_opened
                else:
                    self.can_sprite.image = self.image_closed

    def set_can_active(self):
        window.game_window.set_mouse_visible(False)
        self.can_active = True
        events.Fire('CanTaken')

    def set_lid_active(self):
        window.game_window.set_mouse_visible(False)
        self.lid_active = True
        events.Fire('LidTaken')

    def on_mouse_release(self, x, y, button, modifiers):
        window.game_window.set_mouse_visible(True)
        #print "x=%d y=%d" % (x, y)
        if self.lid_active:
            if self.can_rect.collide_point(x, y):
                self.can_sprite.image = self.image_closed
                self.opened = False
                events.Fire('LidClosed')
            else:
                self.lid_rect.x = x
                self.lid_rect.y = y
                events.Fire('LidDropped')

            self.lid_active = False

        elif self.can_active:
            self.can_sprite.rotation = 0
            self.can_rect.center = (x, y)
            self.can_sprite.set_position(x-self.image_opened.width/2,
                                         y-self.image_opened.height/2)

            self.can_active = False
            events.Fire('CanDropped')

    def on_mouse_motion(self, x, y, dx, dy):
        if self.can_rect.collide_point(x, y):
            self.can_highlighted = True
        else:
            self.can_highlighted = False

        if self.lid_rect.collide_point(x, y):
            self.lid_highlighted = True
        else:
            self.lid_highlighted = False

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.can_active:
            self.can_rect.x = x
            self.can_rect.y = y
            self.can_sprite.set_position(x, y)

            dist = math.sqrt(abs(dx*dx + dy*dy))
            self.can_sprite.rotation = dx / 10.0 * 45

            if dist > 10:
                self.fallen = True
                self.can_active = False
                if dx > 0:
                    self.can_sprite.rotation = 90
                else:
                    self.can_sprite.rotation = -90

                events.Fire('CanTipped')

                if not self.opened:
                    self.opened = True
                    self.can_sprite.image = self.image_opened
                    self.lid_rect.bottomleft = self.can_rect.bottomleft
                    self.lid_rect.x += dx * 5
                    self.lid_rect.y += dy * 5

        elif self.lid_active:
            self.lid_rect.center = (x, y)


def main():
    global win
    clock.schedule(rabbyt.add_time)

    win = pyglet.window.Window(width=leaves.SCREEN_WIDTH, height=leaves.SCREEN_HEIGHT)
    window.set_window(win)
    rabbyt.set_default_attribs()

    garbage = GarbageCan()

    leafs = leaves.LeafGroup()
    leafs += [leaves.Leaf(), leaves.Leaf(), leaves.Leaf() ]
    for i in range(len(leafs)):
        leafs[i].logicalX = 260 + i*80
        leafs[i].logicalY = 100 + i*60
        leafs[i].logicalZ = 10

    while not win.has_exit:
        tick = clock.tick()
        win.dispatch_events()

        leafs.update(tick)
        garbage.update(tick)
        
        events.ConsumeEventQueue()

        rabbyt.clear((1, 1, 1))

        leafs.draw()
        garbage.draw()

        win.flip()

if __name__ == '__main__':
    main()

