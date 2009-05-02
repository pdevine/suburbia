import os.path

def data_file(filename):
    if os.path.exists(filename):
        return filename
    elif os.path.exists(os.path.join('../data/', filename)):
        return os.path.join('../data/', filename)
    elif os.path.exists(os.path.join('data/', filename)):
        return os.path.join('data/', filename)

def magicEventRegister(win, events, objects):
    for obj in objects:
        eventsListenerAdded = False
        for attr in dir(obj):
            if attr.startswith('On_'):
                events.AddListener(obj)
                eventsListenerAdded = True
            if attr.startswith('on_'):
                win.push_handlers(getattr(obj, attr))


def logicalToPerspective(x,y):
    bottomLine  = 80.0
    topLine = 300.0
    pct = (topLine-(y-bottomLine))/(topLine-bottomLine)
    x = max(-10,x - 150 * pct)
    return x,y

class Rect(object):
    def __init__(self, *args):
        if len(args) == 1:
            (self.x, self.y, self.width, self.height) = args[0]
        elif len(args) == 4:
            (self.x, self.y, self.width, self.height) = args
        elif len(args) == 3:
            (self.x, self.y, image_data) = args
            self.set_rect_from_image(image_data)

        # x and y args are the bottom left

        self.x += self.width/2
        self.y += self.height/2

    def __str__(self):
        return str((self.x, self.y, self.width, self.height))

    def _getCenter(self):
        return (self.x, self.y)

    def _setCenter(self, *args):
        if len(args) == 1:
            self.x, self.y = args[0]
        else:
            self.x, self.y = args

    center = property(_getCenter, _setCenter)

    def _getLeft(self, *args):
        return self.x - int(self.width / 2)

    left = property(_getLeft, None)

    def _getRight(self, *args):
        return self.x + int(self.width / 2)

    right = property(_getRight, None)

    def _getMidtop(self):
        return (self.x + int(self.width / 2), self.y)

    def _setMidtop(self, *args):
        if len(args) == 1:
            x, y = args[0]
        else:
            x, y = args
        self.x = x - self.width/2
        self.y = y

    midtop = property(_getMidtop, _setMidtop)

    def _getTop(self):
        return self.y + int(self.height / 2)

    def _setTop(self, *args):
        if len(args) == 1:
            y = args
            self.y = y - self.height/2
        else:
            raise ValueError

    top = property(_getTop, _setTop)

    def _getBottom(self):
        return self.y - int(self.height / 2)

    bottom = property(_getBottom, None)

    def _getBottomLeft(self):
        return (self.x - self.width/2, self.y - self.height/2)

    def _setBottomLeft(self, *args):
        if len(args) == 1:
            x, y = args[0]
        else:
            x, y = args

        self.x = x + self.width/2
        self.y = y + self.width/2

    bottomleft = property(_getBottomLeft, _setBottomLeft)

    def _getTopLeft(self):
        return (self.x - self.width/2, self.y + self.height/2)

    topleft = property(_getTopLeft, None)

    def _getBottomRight(self):
        return (self.x + self.width/2, self.y - self.height/2)

    bottomright = property(_getBottomRight, None)

    def _getTopRight(self):
        return (self.x + self.width/2, self.y + self.height/2)

    topright = property(_getTopRight, None)

    def set_rect_from_image(self, image):
        self.width = image.width
        self.height = image.height

        # reset center of image
        self.x += self.width/2
        self.y += self.height/2

    def move(self, x, y):
        return Rect(x+self.x, y+self.y, self.width, self.height)

    def collide_point(self, *args):
        if len(args) == 1:
            (x, y) = args[0]
        else:
            (x, y) = args

        if x > self.x - self.width/2 and x < self.x + self.width/2 and \
           y > self.y - self.height/2 and y < self.y + self.height/2:
            return True
        else:
            return False

