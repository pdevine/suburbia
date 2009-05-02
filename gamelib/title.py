import pyglet
import data
from util import data_file
from pyglet.gl import *

class Title:
    def __init__(self):
        self.image = pyglet.image.load(data_file('title.png'))

        self.active = True
        self.count = 4
        self.alpha = 1

    def update(self, tick):
        if self.active:
            self.count -= tick
            if self.count < 0:
                self.alpha -= tick
                if self.alpha < 0:
                    self.active = False
                    print "title off"

    def draw(self):
        if self.active:
            glColor4f(1, 1, 1, self.alpha)
            self.image.blit(100, 450)
            glColor4f(1, 1, 1, 1)
