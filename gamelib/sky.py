import os.path
import rabbyt

from pyglet.window import Window
from pyglet import clock
from pyglet import image

import events
import colorsys
from random import randint
import random
import euclid
import math

from grass import Lawn
from grass import MiniGrill
from grill import Grill

from garbage import GarbageCan

from util import data_file

from pyglet.gl import *

rabbyt.data_director = os.path.dirname(__file__)

fps_display = None

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

CURRENT_CLOUD_COVERAGE = 'overcast'

CLOUD_COVERAGE = {
    'clear': (0, 0),
    'few': (1, 2),
    'partial': (3, 4),
    'cloudy': (5, 9),
    'overcast': (10, 12)
}

# Wind speed is pixels per second
WIND_SPEED = -30

class Background:
    def __init__(self):
        self.over = False
        self.color = (0.78, 0.78, 1.0)
        self.hsv_color = [240/360.0, 60/100.0, 0]

        self.weather = 'cloudy'

        self.sun = Sun()
        self.moon = Moon()
        self.rain = Rain()
        self.lawn = Lawn()
        self.mini_grill = MiniGrill()
        self.big_grill = Grill()

        self.clouds = Clouds(self.hsv_color)
        self.garbage_can = GarbageCan()

        self.weather_time = 20
        self.counter = self.weather_time

        events.AddListener(self)

    def update(self, tick):
        if self.over:
            return self.update_dead(tick)

        # save the grill state in the big grill so it's easier to
        # turn off
        if self.mini_grill.active:
            self.big_grill.active = True
            self.mini_grill.active = False

        if self.big_grill.active:
            return self.big_grill.update(tick)
            
        global CURRENT_CLOUD_COVERAGE

        self.counter -= tick

        if self.counter <= 0:
            CURRENT_CLOUD_COVERAGE = random.choice(CLOUD_COVERAGE.keys())
            if 'cloudy' in CURRENT_CLOUD_COVERAGE or \
               'overcast' in CURRENT_CLOUD_COVERAGE:
                self.rain.active = random.choice([True, False])
            else:
                self.rain.active = False

            print "It's now %s" % CURRENT_CLOUD_COVERAGE
            if self.rain.active:
                print "It's raining"
            else:
                print "It's not raining"

            self.counter = self.weather_time

        elements = [self.sun, self.moon, self.rain, self.clouds, self.lawn]

        for element in elements:
            if element:
                element.update(tick)

        if self.sun.deg < 180 and self.sun.deg > 150:
            self.hsv_color[2] = (180 - self.sun.deg) / 30
        elif self.sun.deg < 30 and self.sun.deg > 0:
            self.hsv_color[2] = self.sun.deg / 30

        self.color = colorsys.hsv_to_rgb(*self.hsv_color)

    def draw(self):
        if self.big_grill.active:
            self.big_grill.draw()
            return

        elements = [self.sun, self.moon, self.clouds, self.lawn,
                    self.mini_grill, self.rain, self.garbage_can]

        for element in elements:
            if element:
                element.draw()

    def update_dead(self, tick):
        return

    def On_NarrativeOver(self):
        self.over = True

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
        self.clouds.append(Cloud(self.bg_color, len(self.clouds)))

    def remove_cloud(self):
        self.clouds[randint(0, len(self.clouds)-1)].state = 'dying'

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

            if cloud.state == 'dead':
                self.clouds.remove(cloud)

    def draw(self):
        for cloud in self.clouds:
            cloud.draw()

class Cloud:
    def __init__(self, color, cloud_position):
        self.image = image.load(data_file('cloud.png'))

        cloud_min, cloud_max = CLOUD_COVERAGE[CURRENT_CLOUD_COVERAGE]

        pos_min = int((cloud_position - 1) / float(cloud_max) * SCREEN_WIDTH)
        pos_max = int(cloud_position / float(cloud_max) * SCREEN_WIDTH)

        self.pos = euclid.Vector2(randint(pos_min, pos_max), 
                                  SCREEN_HEIGHT - randint(40, 100))
        self.color = color
        self.hsv_color = [0.666, 1, 1]

        self.alpha = 0

        self.state = 'spawning'

    def update(self, tick):
        self.hsv_color[1] = 1 - self.color[2]

        if self.state == 'spawning':
            self.alpha += 0.8 * tick
            if self.alpha >= 1.0:
                self.alpha = 1
                self.state = 'alive'
        elif self.state == 'dying':
            self.alpha -= 0.8 * tick
            if self.alpha <= 0:
                self.state = 'dead'

        self.pos.x += WIND_SPEED * tick

        if WIND_SPEED > 0 and self.pos.x > SCREEN_WIDTH:
            self.state = 'dead'
        elif WIND_SPEED < 0 and self.pos.x < 0 - self.image.width:
            self.state = 'dead'

    def draw(self):
        glColor4f(*colorsys.hsv_to_rgb(*self.hsv_color) + (self.alpha,))
        self.image.blit(self.pos.x, self.pos.y)
        glColor4f(1.0, 1.0, 1.0, 1.0)

class OrbitingObject:
    def __init__(self):
        self.pos = euclid.Vector2(0, 0)
        self.center_pos = euclid.Vector2(SCREEN_WIDTH/2 - 45,
                                         SCREEN_HEIGHT/2-50)

        self.current_weather = None
        self.alpha = 1.0

    def update(self, tick):
        if CURRENT_CLOUD_COVERAGE == 'overcast' and self.alpha > 0:
            self.alpha = min(self.alpha - 0.3 * tick , 0.0)
        elif CURRENT_CLOUD_COVERAGE != 'overcast' and self.alpha < 1:
            self.alpha = min(self.alpha + 0.3 * tick, 1.0)
                
        degBefore = self.deg
        self.deg -= 10 * tick
        if self.deg < 0:
            self.set()
            self.deg = 360 + self.deg
        elif self.deg < 180 and self.deg + 10 * tick > 180:
            self.rise()

        self.rad = math.radians(self.deg)

        self.pos.x = self.center_pos.x + math.cos(self.rad) * 480
        self.pos.y = self.center_pos.y + math.sin(self.rad) * 250

    def draw(self):
        glColor4f(1.0, 1.0, 1.0, self.alpha)
        if self.deg < 180 and self.deg > 0:
            self.image.blit(self.pos.x, self.pos.y)


class Moon(OrbitingObject):
    def __init__(self):
        self.current_phase = 0
        self.days_until_phasechange = 2
        self.phases = [image.load(data_file('moon-full.png')),
                      ]
        self.deg = 0

        OrbitingObject.__init__(self)

    def update(self, tick):
        OrbitingObject.update(self, tick)
        self.image = self.phases[self.current_phase]

    def set(self):
        pass
    def rise(self):
        pass

class Sun(OrbitingObject):
    def __init__(self):
        OrbitingObject.__init__(self)
        self.image = image.load(data_file('sun.png'))

        self.deg = 180

    def set(self):
        events.Fire('Sunset')
        print 'sunset'
    def rise(self):
        events.Fire('Sunrise')
        print 'sunrise'


class Rain:
    def __init__(self):
        self.quad = gluNewQuadric()
        self.active = True
        self.rain = []

        self.delay_time = 0.1
        self.counter = self.delay_time

        self.build()

        self.add_drops()

    def add_drops(self, amount=10):
        if not self.active:
            return
        for count in range(amount):
            self.rain.append(RainDrop(self.quad, self.display_id))

    def update(self, tick):
        if not self.active and not self.rain:
            return

        self.counter -= tick
        if self.counter <= 0:
            self.add_drops()
            self.counter = self.delay_time

        for drop in self.rain:
            drop.update(tick)

            if drop.dead:
                self.rain.remove(drop)

    def draw(self):
        if not self.active and not self.rain:
            return

        for drop in self.rain:
            drop.draw()

    def build(self):
        self.display_id = glGenLists(1)
        glNewList(self.display_id, GL_COMPILE)

        glColor4f(0, 0, 0.95, 0.7)

        glLineWidth(4)

        glBegin(GL_LINES)
        glVertex2i(0, 0)
        glVertex2i(0, 4)
        glEnd()

        glColor4f(1, 1, 1, 1)

        glEndList()

class RainDrop:
    def __init__(self, quad, display_id):
        self.quad = quad
        self.display_id = display_id
        self.color = (0, 0, 0.95, 0.7)
        self.vector = euclid.Vector2(0, 0)
        self.dead = False

        self.pos = euclid.Vector2(randint(0, SCREEN_WIDTH), SCREEN_HEIGHT-90)
        self.vector.y = -SCREEN_HEIGHT

    def update(self, tick):
        self.vector.x = WIND_SPEED

        self.pos.x += self.vector.x * tick
        self.pos.y += self.vector.y * tick

        if self.pos.y < 180:
            self.dead = True

    def draw(self):
        glPushMatrix()
        glTranslatef(self.pos.x, self.pos.y, 0)

        glCallList(self.display_id)

        glPopMatrix()




def main():
    global fps_display

    win = Window(width=800, height=600)

    clock.schedule(rabbyt.add_time)

    rabbyt.set_default_attribs()

    bg = Background()

    fps_display = clock.ClockDisplay()

    while not win.has_exit:
        tick = clock.tick()
        win.dispatch_events()

        bg.update(tick)

        rabbyt.clear((bg.color))

        bg.draw()
        fps_display.draw()

        win.flip()

if __name__ == '__main__':
    main()

