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
    vanishingLineX = 400.0
    vanishingLineY = 300.0

    oldDeltaX = vanishingLineX-x
    oldDeltaY = vanishingLineY-y

    # 0 means its right on it, 1.0 means it's really far away
    farnessFromLineY = (oldDeltaY/vanishingLineY)
    farnessFromLineX = (oldDeltaX/vanishingLineX)

    newDeltaX = (farnessFromLineY)*oldDeltaX
    newDeltaY = (farnessFromLineY)*oldDeltaY

    newX = x - (newDeltaX - oldDeltaX)
    newY = y - (newDeltaY - oldDeltaY)
    newY = y
    return newX, newY
