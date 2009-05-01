import pyglet
import rabbyt

from pyglet import clock
from pyglet import image
from pyglet.gl import *

import window
import euclid

from random import randint
from util import data_file
from util import Rect

class GrillObject:
    def draw(self):
        if not self.active:
            self.image.blit(*self.rect.bottomleft)

    def handler(self, pos):
        if self.rect.collide_point(*pos):
            self.set_active()

    def set_active(self):
        cursor = pyglet.window.ImageMouseCursor(
            self.image, self.image.width/2, self.image.height/2)

        window.game_window.set_mouse_cursor(cursor)
        self.active = True

    def set_inactive(self, pos):
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.set_default_cursor()
        self.active = False

    def set_default_cursor(self):
        cursor = window.game_window.get_system_mouse_cursor(
            window.game_window.CURSOR_DEFAULT)
        window.game_window.set_mouse_cursor(cursor)


class Beef(GrillObject):
    def __init__(self):
        self.image = image.load(data_file('beef.png'))
        self.rect = Rect(120, 280, self.image)

        self.active = False

    def update(self, tick):
        pass

class Spritzer(GrillObject):
    def __init__(self):
        self.image = image.load(data_file('spritzer.png'))
        self.rect = Rect(600, 50, self.image)
        self.drop_range = (50, 100)

        self.active = False
        self.build_drop()
        self.drops = []

    def update(self, tick):
        for drop in self.drops:
            drop.update(tick)
            if drop.dead:
                self.drops.remove(drop)

    def spritz(self, pos):
        start_pos = (pos[0] - self.rect.width/2,
                     pos[1] + self.rect.height/2 - 8)
        for count in range(*self.drop_range):
            self.drops.append(WaterDrop(self.display_id, start_pos))

    def draw(self):
        GrillObject.draw(self)
        for drop in self.drops:
            drop.draw()

    def build_drop(self):
        self.display_id = glGenLists(1)
        glNewList(self.display_id, GL_COMPILE)

        glLineWidth(4)

        glBegin(GL_LINES)
        glVertex2i(0, 0)
        glVertex2i(0, 4)
        glEnd()

        glColor4f(1, 1, 1, 1)

        glEndList()

class WaterDrop:
    def __init__(self, display_id, pos):
        self.display_id = display_id
        self.lifetime_range = randint(2, 10) / 10.0
        self.color = (0, 0, 0.95, 0.7)
        self.vector = euclid.Vector2(0, 0)
        self.dead = False

        self.pos = euclid.Vector2(*pos)

        self.vector.x = -randint(100, 200)
        self.vector.y = randint(-10, 10)

    def update(self, tick):
        self.lifetime_range -= tick
        if self.lifetime_range < 0:
            self.dead = True
            return

        self.pos.x += self.vector.x * tick
        self.pos.y += self.vector.y * tick

    def draw(self):
        glPushMatrix()
        glTranslatef(self.pos.x, self.pos.y, 0)
        glColor4f(*self.color)

        glCallList(self.display_id)

#        glLineWidth(4)
#
#        glBegin(GL_LINES)
#        glVertex2i(0, 0)
#        glVertex2i(0, 4)
#        glEnd()
#
#        glColor4f(1, 1, 1, 1)

        glPopMatrix()


class Grill:
    def __init__(self):
        self.image = image.load(data_file('biggrill.png'))
        self.beef = Beef()
        self.spritzer = Spritzer()

        window.game_window.push_handlers(self.on_mouse_press)
        window.game_window.push_handlers(self.on_mouse_release)

    def update(self, tick):
        self.spritzer.update(tick)

    def draw(self):
        self.image.blit(120, 100)

        self.beef.draw()
        self.spritzer.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        if self.spritzer.active:
            print "spritz"
            self.spritzer.spritz((x, y))
            return

        self.beef.handler((x, y))
        self.spritzer.handler((x, y))

    def on_mouse_release(self, x, y, button, modifiers):
        if self.beef.active:
            self.beef.set_inactive((x, y))


def main():
    clock.schedule(rabbyt.add_time)

    win = pyglet.window.Window(width=800, height=600)
    window.set_window(win)

    rabbyt.set_default_attribs()

    grill = Grill()

    while not win.has_exit:
        tick = clock.tick()
        win.dispatch_events()

        grill.update(tick)

        rabbyt.clear((1, 1, 1))

        grill.draw()

        win.flip()

if __name__ == '__main__':
    main()

