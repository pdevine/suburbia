from pyglet import image

from util import data_file
from util import Rect

import euclid

class GarbageCan:
    def __init__(self):
        self.image_opened = image.load(data_file('garbagecan-open.png'))
        self.image_closed = image.load(data_file('garbagecan-closed.png'))
        self.image_lid = image.load(data_file('garbagecan-lid.png'))

        self.opened = True

        width = self.image_closed.width
        height = self.image_closed.height

        self.can_rect = Rect(100, 100, width, height)

        self.lid_pos = euclid.Vector2(200, 200)

    def draw(self):
        if self.opened:
            self.image_opened.blit(*self.can_rect.center)
            self.image_lid.blit(*self.lid_pos)
        else:
            self.image.closed.blit(*self.can_rect.center)
