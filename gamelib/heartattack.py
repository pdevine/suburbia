
from pyglet.gl import *
import events

class HeartAttack:
    def __init__(self):
        self.quad = gluNewQuadric()

        self.inner = 500
        self.active = False

        events.AddListener(self)

    def update(self, tick):
        if self.active:
            if self.inner > 200:
                self.inner -= tick * 90

    def draw(self):
        if not self.active:
            return

        glColor4f(0.1, 0.1, 0.1, 0.8)
        glPushMatrix()
        glTranslatef(400, 300, 0)
        gluQuadricDrawStyle(self.quad, GLU_FILL)
        gluDisk(self.quad, self.inner, 500, 300, 1)
        glPopMatrix()

    def On_HeartAttack(self):
        self.active = True
        events.Fire('NewHint', 'Jesus, my arm is tingling')
