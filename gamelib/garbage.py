from pyglet import image
import pyglet

from util import data_file
from util import Rect
from pyglet.sprite import Sprite
from random import randint

import math
import window
import euclid

class GarbageCan:
    def __init__(self):
        self.image_opened = image.load(data_file('garbagecan-open.png'))
        self.image_closed = image.load(data_file('garbagecan-closed.png'))
        self.image_lid = image.load(data_file('garbagecan-lid.png'))

        self.opened = True
        self.lid_active = False
        self.can_active = False
        self.fallen = False

        self.can_rect = Rect(100, 100, self.image_closed)
        self.lid_rect = Rect(200, 200, self.image_lid)

        window.game_window.push_handlers(self.on_mouse_release)
        window.game_window.push_handlers(self.on_mouse_press)
        window.game_window.push_handlers(self.on_mouse_drag)

        self.sprite = Sprite(self.image_opened)

    def draw(self):
        if not self.can_active:
            if self.opened:
                if self.fallen:
                    self.sprite.draw()
                else:
                    self.image_opened.blit(*self.can_rect.bottomleft)
                
            else:
                self.image_closed.blit(*self.can_rect.bottomleft)
        if not self.lid_active and self.opened:
            self.image_lid.blit(*self.lid_rect.bottomleft)


    def on_mouse_press(self, x, y, button, modifiers):
        if button == 1:
            if self.opened and self.lid_rect.collide_point(x, y):
                self.set_lid_active()
            elif self.can_rect.collide_point(x, y):
                self.fallen = False
                self.set_can_active()

    def set_can_active(self):
        if self.opened:
            image = self.image_opened
        else:
            image = self.image_closed

        cursor = pyglet.window.ImageMouseCursor(
            image, image.width/2, image.height/2)

        window.game_window.set_mouse_cursor(cursor)
        self.can_active = True

    def set_lid_active(self):
        cursor = pyglet.window.ImageMouseCursor(
            self.image_lid,
            self.image_lid.width/2,
            self.image_lid.height/2)
        window.game_window.set_mouse_cursor(cursor)
        self.lid_active = True

    def on_mouse_release(self, x, y, button, modifiers):
        print "x=%d y=%d" % (x, y)
        if self.lid_active:
            if self.can_rect.collide_point(x, y):
                self.opened = False
            else:
                self.lid_rect.x = x
                self.lid_rect.y = y

            self.lid_active = False
            self.set_default_cursor()

        elif self.can_active:
            self.can_rect.x = x
            self.can_rect.y = y

            self.set_default_cursor()
            self.can_active = False

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.can_active:
            dist = math.sqrt(abs(dx*dx + dy*dy))
            if dist > 10:
                self.fallen = True
                self.can_active = False
                self.can_rect.x = x
                self.can_rect.y = y
                self.sprite.set_position(x, y)
                if dx > 0:
                    self.sprite.rotation = 90
                else:
                    self.sprite.rotation = -90

                if not self.opened:
                    self.opened = True
                    self.lid_rect.bottomleft = self.can_rect.bottomleft
                    self.lid_rect.x += dx * 5
                    self.lid_rect.y += dy * 5

                self.set_default_cursor()

    def set_default_cursor(self):
        cursor = window.game_window.get_system_mouse_cursor(
            window.game_window.CURSOR_DEFAULT)
        window.game_window.set_mouse_cursor(cursor)


