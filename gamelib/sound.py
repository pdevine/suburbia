from util import data_file
from pyglet import media

def queue_soundtrack(song='8bp069-06-she-streets.mp3', soundtrack=None):
    if not soundtrack:
        soundtrack = media.Player()
        soundtrack.eos_action = 'loop'

    soundtrack.queue(media.load(data_file(song)))
    return soundtrack

