import pyglet
import rabbyt

from pyglet import clock
from pyglet import image
from pyglet.gl import *

import window
import euclid
import events
import random

from random import randint
from util import data_file
from util import Rect

BURN_PHRASES = [
    'I hope everyone likes their steak well done',
    'Man I suck.  Maybe I should have gotten a gass grill',
]

class GrillObject:
    def __init__(self):
        self.highlighted = True
        self.active = False

        window.game_window.push_handlers(self.on_mouse_motion)
        window.game_window.push_handlers(self.on_mouse_drag)

    def draw(self):
        if self.highlighted:
            glColor4f(0.1, 0.1, 1, 1)
        else:
            glColor4f(1, 1, 1, 1)

        self.image.blit(*self.rect.bottomleft)
        glColor4f(1, 1, 1, 1)

    def handler(self, pos):
        if self.rect.collide_point(*pos):
            self.set_active()
            self.highlighted = False
            return True
        return False

    def set_active(self):
        #cursor = pyglet.window.ImageMouseCursor(
        #    self.image, self.image.width/2, self.image.height/2)

        #window.game_window.set_mouse_cursor(cursor)
        window.game_window.set_mouse_visible(False)
        self.active = True

    def set_inactive(self, pos):
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        window.game_window.set_mouse_visible(True)
        self.active = False

    def on_mouse_motion(self, x, y, dx, dy):
        if self.rect.collide_point(x, y):
            self.highlighted = True
        else:
            self.highlighted = False

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        pass

class Beef(GrillObject):
    def __init__(self):
        GrillObject.__init__(self)
        self.image = image.load(data_file('beef.png'))
        self.rect = Rect(520, 230, self.image)

        self.cooking = False

        self.reset()

        events.AddListener(self)

    def reset(self):
        self.cooking_time = 15
        self.red = 1
        self.brown_time = 3
        self.cooked = False
        self.burnt = False
        self.rect.bottomleft = (520, 230)

    def handler(self, pos):
        if self.rect.collide_point(*pos):
            self.set_active()
            self.cooking = False
            self.highlighted = False
            return True
        return False

    def set_active(self):
        GrillObject.set_active(self)
        events.Fire('BeefTaken')
        print "beef taken"

    def set_inactive(self, pos):
        GrillObject.set_inactive(self, pos)
        events.Fire('BeefDropped')
        print "beef dropped"

    def update(self, tick):
        if self.cooking:
            self.brown_time -= tick
            if self.brown_time < 0:
                self.brown_time = 3
                self.red -= 0.1

            self.cooking_time -= tick

            if self.cooking_time < 0:
                if not self.cooked:
                    self.cooked = True
                    events.Fire('BeefCooked')
                    events.Fire('NewHint',
                        'Damn that steak looks good.')
                elif self.cooking_time < -15 and not self.burnt:
                    events.Fire('BeefBurnt')
                    events.Fire('NewHint', random.choice(BURN_PHRASES))
                    self.burnt = True

    def draw(self):
        if self.highlighted:
            glColor4f(0.5, 0.1, 1, 1)
        else:
            glColor4f(self.red, self.red, self.red, 1)

        self.image.blit(*self.rect.bottomleft)

        glColor4f(1, 1, 1, 1)

    def On_Sunrise(self):
        self.reset()

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.active:
            self.rect.center = (x, y)

class Spritzer(GrillObject):
    def __init__(self):
        GrillObject.__init__(self)

        self.image = image.load(data_file('spritzer.png'))
        self.rect = Rect(600, 50, self.image)
        self.drop_range = (50, 100)

        self.build_drop()
        self.drops = []

        #events.AddListener(self)

    def set_active(self):
        GrillObject.set_active(self)
        events.Fire('SpritzerTaken')
        print "spritzer taken"

    def set_inactive(self, pos):
        GrillObject.set_inactive(self, pos)
        events.Fire('SpritzerDropped')
        print "spritzer dropped"

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

    def on_mouse_motion(self, x, y, dx, dy):
        if self.active:
            self.rect.center = (x, y)

        GrillObject.on_mouse_motion(self, x, y, dx, dy)


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

        glPopMatrix()

class RectObject:
    def draw(self):
        if not hasattr(self, 'image'):
            self.draw_rect()
        else:
            self.image.blit(*self.rect.bottomleft)

    def draw_rect(self):
        glColor4f(0, 0, 1, .5)

        glBegin(GL_POLYGON)
        glVertex2d(*self.rect.bottomleft)
        glVertex2d(*self.rect.topleft)
        glVertex2d(*self.rect.topright)
        glVertex2d(*self.rect.bottomright)
        glEnd()

        glColor4f(1, 1, 1, 1)

class Exit(RectObject):
    def __init__(self):
        self.image = image.load(data_file('back.png'))
        self.rect = Rect(700, 500, 100, 100)

class Table(RectObject):
    def __init__(self):
        self.rect = Rect(600, 0, 200, 150)

class FlareUp:
    def __init__(self):
        self.images = [
            image.load(data_file('fire0.png')),
            image.load(data_file('fire2.png')),
            image.load(data_file('fire1.png')),
        ]

        self.image = self.images[0]
        pos = (randint(140, 350), randint(270, 400))
        self.rect = Rect(pos[0], pos[1], self.image)

        self.lives = 3

        self.delay = 0.2
        self.timer = self.delay
        self.image_count = 0

    def update(self, tick):
        self.timer -= tick
        if self.timer < 0:
            self.timer = self.delay
            self.image_count += 1
            if self.image_count >= len(self.images):
                self.image_count = 0

        self.image = self.images[self.image_count]

    def draw(self):
        glColor4f(1, 1, 1, self.lives / 3.0)
        self.image.blit(*self.rect.bottomleft)
        glColor4f(1, 1, 1, 1)

class Grill:
    def __init__(self):
        self.image = image.load(data_file('biggrill.png'))
        self.beef = Beef()
        self.spritzer = Spritzer()
        self.table = Table()
        self.exit = Exit()

        self.rect = Rect(150, 300, 300, 200)

        self.flareups = []
        self.flareup_range = (10, 50)
        self.flareup_counter = randint(*self.flareup_range) / 10.0

        window.game_window.push_handlers(self.on_mouse_press)
        window.game_window.push_handlers(self.on_mouse_release)
        window.game_window.push_handlers(self.on_mouse_motion)

        #events.AddListener(self)

        self.active = False
        self.beef_hint_done = False
        self.flareup_hint_done = False

    def update(self, tick):
        self.beef.update(tick)
        if self.beef.cooking:
            self.flareup_counter -= tick
            #print self.flareup_counter
            if self.flareup_counter <= 0:
                if len(self.flareups) < 2:
                    if not self.flareup_hint_done:
                        events.Fire('NewHint',
                            'I can put out flare ups with the spritzer')
                        self.flareup_hint_done = True
                        print "flare ups hint"
                    self.flareups.append(FlareUp())
                    self.flareup_counter = randint(*self.flareup_range) / 10.0
                    print "flareup"
                    events.Fire('FlareUp')

        self.spritzer.update(tick)
        for fire in self.flareups:
            fire.update(tick)

    def draw(self):
        self.image.blit(120, 100)

        self.exit.draw()
        self.table.draw()

        #self.draw_rect()

        self.beef.draw()
        for fire in self.flareups:
            fire.draw()

        self.spritzer.draw()

    def check_flareups(self, x, y):
        for fire in self.flareups:
            #x += self.spritzer.rect.width/2
            #y += self.spritzer.rect.height/2
            rect_x = x - fire.rect.x - fire.rect.width/2
            rect_y = y + self.spritzer.rect.height/2 - fire.rect.y 

            if rect_x < 100 and abs(rect_y) < 40:
                print "hit fire"
                fire.lives -= 1
                if fire.lives <= 0:
                    self.flareups.remove(fire)
                break

    def on_mouse_press(self, x, y, button, modifiers):
        if not self.active:
            return

        if self.spritzer.active:
            if self.table.rect.collide_point(x, y):
                self.spritzer.set_inactive((x, y))
                return
            print "spritz"
            self.spritzer.spritz((x, y))
            events.Fire('Spritz')

            self.check_flareups(x, y)

            return

        if self.exit.rect.collide_point(x, y):
            self.active = False

        if self.spritzer.handler((x, y)):
            return
        if self.beef.handler((x, y)):
            return

    def on_mouse_release(self, x, y, button, modifiers):
        if self.beef.active:
            self.beef.set_inactive((x, y))
            if self.rect.collide_point(self.beef.rect.center):
                events.Fire('BeefCooking')
                self.beef.cooking = True
                print "cookin'!"

    def on_mouse_motion(self, x, y, dx, dy):
        if not self.beef_hint_done and self.active:
            events.Fire('NewHint', 'I need to put the steak on the grill.')
            self.beef_hint_done = True

    def draw_rect(self):
        glColor4f(0, 0, 1, .5)

        glBegin(GL_POLYGON)
        glVertex2d(*self.rect.bottomleft)
        glVertex2d(*self.rect.topleft)
        glVertex2d(*self.rect.topright)
        glVertex2d(*self.rect.bottomright)
        glEnd()

        glColor4f(1, 1, 1, 1)


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

