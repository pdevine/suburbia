import os.path
import rabbyt

from pyglet.window import Window
from pyglet import clock
from pyglet import image

import colorsys
from random import randint
import euclid

from util import data_file

from pyglet.gl import *

rabbyt.data_director = os.path.dirname(__file__)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# WEATHER STATES
#  few clouds
#  partially cloudy
#  cloudy
#  overcast
#
#  raining
#  hailing
#  windy

CURRENT_CLOUD_COVERAGE = 'few'

CLOUD_COVERAGE = {
    'clear': (0, 0),
    'few': (1, 3),
    'partial': (4, 7),
    'cloudy': (8, 12),
    'overcast': (20, 30)
}

# Wind speed is pixels per second
WIND_SPEED = -10

class Background:
    def __init__(self):
        self.color = (0.78, 0.78, 1.0)
        self.hsv_color = [240/360.0, 60/100.0, 0]

        self.weather = 'cloudy'

        self.sun = Sun()
        self.rain = Rain()
        self.clouds = Clouds(self.hsv_color)
        self.earth = Earth()

    def update(self, tick):
        elements = [self.sun, self.rain, self.clouds]

        for element in elements:
            if element:
                element.update(tick)

        if self.sun and self.sun.pos.x < 100:
            self.hsv_color[2] = min(self.sun.pos.x+50, 100)/100.0
        elif self.sun and self.sun.pos.x > SCREEN_WIDTH - 200:
            self.hsv_color[2] = \
                min(SCREEN_WIDTH - self.sun.pos.x+20, 100)/100.0
        else:
            self.hsv_color[2] = 1

        self.color = colorsys.hsv_to_rgb(*self.hsv_color)

    def draw(self):
#        elements = [self.earth, self.sun, self.rain]
#        for element in elements:
#            if element:
#                element.draw()

        self.sun.draw()

        self.clouds.draw()

        self.earth.draw()
        self.rain.draw()

class Earth:
    def __init__(self):
        self.image = image.load(data_file('underground-sm.png'))

    def update(self, tick):
        pass

    def draw_field(self):
        glColor4f(0.298, 0.27, 0.2, 1)

        glBegin(GL_POLYGON)
        glVertex2d(0, 0)
        glVertex2d(0, SCREEN_HEIGHT/2)
        glVertex2d(SCREEN_WIDTH, SCREEN_HEIGHT/2)
        glVertex2d(SCREEN_WIDTH, 0)
        glEnd()

        glColor4f(1, 1, 1, 1)

    def draw(self):
        self.draw_field()
        self.image.blit(0, 0)

class Clouds:
    def __init__(self, bg_color):
        self.current_weather = 'overcast'
        self.total_clouds = randint(*CLOUD_COVERAGE[self.current_weather])
        self.bg_color = bg_color

        self.clouds = []
        for count in range(self.total_clouds):
            self.add_cloud()

        self.delay_time = 0.5
        self.counter = self.delay_time

    def add_cloud(self):
        self.clouds.append(Cloud(self.bg_color))

    def remove_cloud(self):
        self.clouds.remove(self.clouds[randint(0, len(self.clouds)-1)])

    def update(self, tick):
        self.counter -= tick

        if self.current_weather != CURRENT_CLOUD_COVERAGE:
            self.current_weather = CURRENT_CLOUD_COVERAGE
            self.total_clouds = randint(*CLOUD_COVERAGE[self.current_weather])

        if self.counter <= 0:
            if len(self.clouds) < self.total_clouds:
                self.add_cloud()
            elif len(self.clouds) > self.total_clouds:
                self.remove_cloud()

            self.counter = self.delay_time

        for cloud in self.clouds:
            cloud.update(tick)

            if cloud.dead:
                self.clouds.remove(cloud)

    def draw(self):
        for cloud in self.clouds:
            cloud.draw()

class Cloud:
    def __init__(self, color):
        self.image = image.load(data_file('cloud.png'))
        self.pos = euclid.Vector2(randint(0, SCREEN_WIDTH),
                                  SCREEN_HEIGHT - randint(40, 100))
        self.color = color
        self.hsv_color = [0.666, 1, 1]

        self.dead = False

    def update(self, tick):
        self.hsv_color[1] = 1 - self.color[2]

        self.pos.x += WIND_SPEED * tick

        if WIND_SPEED > 0 and self.pos.x > SCREEN_WIDTH:
            self.dead = True
        elif WIND_SPEED < 0 and self.pos.x < 0 - self.image.width:
            self.dead = True

    def draw(self):
        glColor3f(*colorsys.hsv_to_rgb(*self.hsv_color))
        self.image.blit(self.pos.x, self.pos.y)
        glColor4f(1.0, 1.0, 1.0, 1.0)

class Sun:
    def __init__(self):
        #self.image = rabbyt.Sprite(data_file('sun.png'))
        #self.image.xy = (-100, SCREEN_HEIGHT - 100)
        self.image = image.load(data_file('sun.png'))
        self.pos = euclid.Vector2(-100, SCREEN_HEIGHT - 100)
        self.vector = euclid.Vector2(0, 0)
        self.vector.x = 50

    def update(self, tick):
        if self.pos.x < SCREEN_WIDTH / 2:
            self.vector.y = 5
        else:
            self.vector.y = -5

        self.pos.x += self.vector.x * tick
        self.pos.y += self.vector.y * tick

    def draw(self):
        glColor4f(1.0, 1.0, 1.0, 1.0)

        #self.image.render()
        self.image.blit(self.pos.x, self.pos.y)


class Rain:
    def __init__(self):
        self.quad = gluNewQuadric()
        self.rain = []

        self.delay_time = 0.1
        self.counter = self.delay_time

        self.add_drops()

    def add_drops(self, amount=10):
        for count in range(amount):
            self.rain.append(RainDrop(self.quad))

    def update(self, tick):
        self.counter -= tick
        if self.counter <= 0:
            self.add_drops()
            self.counter = self.delay_time

        for drop in self.rain:
            drop.update(tick)

            if drop.dead:
                self.rain.remove(drop)

    def draw(self):
        for drop in self.rain:
            drop.draw()

class RainDrop:
    def __init__(self, quad):
        self.quad = quad
        self.color = (0, 0, 0.95, 0.5)
        self.vector = euclid.Vector2(0, 0)
        self.dead = False

        self.vector.y = -SCREEN_HEIGHT

        self.x = randint(0, SCREEN_WIDTH)
        self.y = SCREEN_HEIGHT + 1

    def update(self, tick):
        self.x += self.vector.x * tick
        self.y += self.vector.y * tick

        if self.y < 180:
            self.dead = True

    def draw(self):
        glPushMatrix()

        glColor4f(*self.color)

        glLineWidth(4)

        glBegin(GL_LINES)
        glVertex2i(int(self.x), int(self.y))
        glVertex2i(int(self.x), int(self.y-3))
        glEnd()

        glColor4f(1.0, 1.0, 1.0, 1.0)

        glPopMatrix()


def main():
    clock.schedule(rabbyt.add_time)

    win = Window(width=800, height=600)
    rabbyt.set_default_attribs()

    bg = Background()

    while not win.has_exit:
        tick = clock.tick()
        win.dispatch_events()

        bg.update(tick)

        rabbyt.clear((bg.color))

        bg.draw()

        win.flip()

if __name__ == '__main__':
    main()

