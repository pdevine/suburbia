import pyglet
import rabbyt

from pyglet import clock
from pyglet import image

import window

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

        self.active = False

    def update(self, tick):
        pass

class Grill:
    def __init__(self):
        self.image = image.load(data_file('biggrill.png'))
        self.beef = Beef()
        self.spritzer = Spritzer()

        window.game_window.push_handlers(self.on_mouse_press)
        window.game_window.push_handlers(self.on_mouse_release)

    def update(self, tick):
        pass

    def draw(self):
        self.image.blit(120, 100)

        self.beef.draw()
        self.spritzer.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        if self.spritzer.active:
            print "spritz"
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

        rabbyt.clear((1, 1, 1))

        grill.draw()

        win.flip()

if __name__ == '__main__':
    main()

